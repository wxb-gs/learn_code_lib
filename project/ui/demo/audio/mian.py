from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QPushButton, QLabel, QFrame,
                             QScrollArea, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QPen, QBrush, QLinearGradient
import sys
import numpy as np
import pyaudio
import threading
import time
from collections import deque

# 导入您的语音控制系统模块
try:
    from speech_system import VoiceControlSystem
except ImportError:
    print("警告: 无法导入语音控制系统模块，将使用模拟数据")
    VoiceControlSystem = None

class AudioWaveWidget(QWidget):
    """音频波形显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setMinimumWidth(300)
        
        # 音频数据缓冲区
        self.audio_buffer = deque(maxlen=200)
        self.max_amplitude = 1.0
        
        # 初始化为静音状态
        for _ in range(200):
            self.audio_buffer.append(0.0)
        
        # 设置样式
        self.setStyleSheet("""
            AudioWaveWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        # 启动更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(50)  # 20 FPS
        
        # 音频采集
        self.is_recording = False
        self.audio_thread = None
        self.start_audio_capture()
    
    def start_audio_capture(self):
        """启动音频采集"""
        if self.audio_thread and self.audio_thread.is_alive():
            return
        
        self.is_recording = True
        self.audio_thread = threading.Thread(target=self._audio_capture_loop, daemon=True)
        self.audio_thread.start()
    
    def stop_audio_capture(self):
        """停止音频采集"""
        self.is_recording = False
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
    
    def _audio_capture_loop(self):
        """音频采集循环"""
        try:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=512
            )
            
            while self.is_recording:
                try:
                    data = stream.read(512, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # 计算RMS振幅
                    rms = np.sqrt(np.mean(audio_data.astype(np.float64) ** 2))
                    normalized_rms = min(rms / 10000.0, 1.0)  # 归一化到0-1
                    
                    self.audio_buffer.append(normalized_rms)
                    
                except Exception as e:
                    # 如果音频采集失败，添加静音数据
                    self.audio_buffer.append(0.0)
                    time.sleep(0.05)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
        except Exception as e:
            print(f"音频采集错误: {e}")
            # 生成模拟数据
            while self.is_recording:
                fake_amplitude = np.random.random() * 0.3 if np.random.random() > 0.7 else 0.0
                self.audio_buffer.append(fake_amplitude)
                time.sleep(0.05)
    
    def paintEvent(self, event):
        """绘制波形"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        rect = self.rect()
        painter.fillRect(rect, QColor(255, 255, 255))  # 白色背景
        
        if not self.audio_buffer:
            return
        
        # 绘制波形
        width = rect.width() - 20
        height = rect.height() - 20
        center_y = rect.height() // 2
        
        # 设置黑色画笔和画刷
        painter.setBrush(QBrush(QColor(0, 0, 0)))  # 黑色填充
        painter.setPen(QPen(QColor(0, 0, 0), 1))   # 黑色边框
        
        # 绘制波形条
        bar_width = max(1, width // len(self.audio_buffer))
        
        for i, amplitude in enumerate(self.audio_buffer):
            if i * bar_width >= width:
                break
            
            bar_height = int(amplitude * height * 0.8)
            x = 10 + i * bar_width
            y = center_y - bar_height // 2
            
            painter.drawRect(x, y, bar_width - 1, bar_height)

class MessageBubble(QFrame):
    """消息气泡组件"""
    
    def __init__(self, message, is_system=False, parent=None):
        super().__init__(parent)
        self.is_system = is_system
        self.setup_ui(message)
    
    def setup_ui(self, message):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 消息标签
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Microsoft YaHei", 10))
        
        if self.is_system:
            # 系统消息样式
            self.setStyleSheet("""
                MessageBubble {
                    background-color: #f0f0f0;
                    border-radius: 15px;
                    margin: 5px 50px 5px 5px;
                }
            """)
            self.message_label.setStyleSheet("color: #333333;")
        else:
            # 用户消息样式
            self.setStyleSheet("""
                MessageBubble {
                    background-color: #007acc;
                    border-radius: 15px;
                    margin: 5px 5px 5px 50px;
                }
            """)
            self.message_label.setStyleSheet("color: white;")
        
        layout.addWidget(self.message_label)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

class ChatArea(QScrollArea):
    """聊天区域"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 创建内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(10)
        
        # 设置滚动区域
        self.setWidget(self.content_widget)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 样式设置
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                background-color: #e9ecef;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #007acc;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #0056a3;
            }
        """)
    
    def add_message(self, message, is_system=False):
        """添加消息"""
        bubble = MessageBubble(message, is_system)
        self.content_layout.addWidget(bubble)
        
        # 滚动到底部
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

class StatusIndicator(QWidget):
    """状态指示器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.is_active = False
        self.is_listening = False
        
        # 动画效果
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        
        # 呼吸灯效果定时器
        self.breath_timer = QTimer()
        self.breath_timer.timeout.connect(self.update)
        self.breath_timer.start(100)
        
        self.breath_phase = 0
    
    def set_active(self, active):
        """设置激活状态"""
        self.is_active = active
        self.update()
    
    def set_listening(self, listening):
        """设置监听状态"""
        self.is_listening = listening
        self.update()
    
    def paintEvent(self, event):
        """绘制状态指示器"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        if self.is_active:
            if self.is_listening:
                # 监听状态 - 呼吸灯效果
                self.breath_phase += 0.2
                alpha = int(128 + 127 * np.sin(self.breath_phase))
                color = QColor(255, 0, 0, alpha)  # 红色呼吸灯
            else:
                color = QColor(0, 255, 0)  # 绿色
        else:
            color = QColor(128, 128, 128)  # 灰色
        
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(), 1))
        painter.drawEllipse(rect)

class ModernVoiceControlUI(QMainWindow):
    """现代化语音控制界面"""
    
    def __init__(self):
        super().__init__()
        self.voice_system = None
        self.setup_ui()
        self.setup_voice_system()
        
        # 自动启动系统
        QTimer.singleShot(1000, self.auto_start_system)
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("AI语音助手 - 现代化界面")
        self.setGeometry(100, 100, 900, 700)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部标题栏
        self.create_header(main_layout)
        
        # 聊天区域
        self.chat_area = ChatArea()
        main_layout.addWidget(self.chat_area)
        
        # 底部控制区域
        self.create_footer(main_layout)
        
        # 添加欢迎消息
        self.chat_area.add_message("欢迎使用AI语音助手！系统正在初始化中...", is_system=True)
    
    def create_header(self, parent_layout):
        """创建头部区域"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                          stop: 0 #007acc, stop: 1 #00a0e6);
                border-bottom: 1px solid #005999;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # 标题
        title_label = QLabel("🎤 AI语音助手")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 状态指示器
        status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        status_layout.addWidget(self.status_indicator)
        
        self.status_label = QLabel("系统初始化中...")
        self.status_label.setFont(QFont("Microsoft YaHei", 10))
        self.status_label.setStyleSheet("color: white;")
        status_layout.addWidget(self.status_label)
        
        header_layout.addLayout(status_layout)
        
        parent_layout.addWidget(header)
    
    def create_footer(self, parent_layout):
        """创建底部区域"""
        footer = QFrame()
        footer.setFixedHeight(120)
        footer.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        footer_layout.setSpacing(10)
        
        # 音频波形显示
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("🔊 音频输入:"))
        
        self.audio_wave = AudioWaveWidget()
        wave_layout.addWidget(self.audio_wave)
        wave_layout.addStretch()
        
        footer_layout.addLayout(wave_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.control_button = QPushButton("🔴 停止系统")
        self.control_button.setFixedHeight(40)
        self.control_button.setFont(QFont("Microsoft YaHei", 10))
        self.control_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.control_button.clicked.connect(self.toggle_system)
        
        button_layout.addStretch()
        button_layout.addWidget(self.control_button)
        button_layout.addStretch()
        
        footer_layout.addLayout(button_layout)
        
        parent_layout.addWidget(footer)
    
    def setup_voice_system(self):
        """设置语音控制系统"""
        if VoiceControlSystem:
            try:
                self.voice_system = VoiceControlSystem()
                self.voice_system.text_recognized.connect(self.on_text_recognized)
                self.voice_system.status_changed.connect(self.on_status_changed)
                print("语音控制系统初始化成功")
            except Exception as e:
                print(f"语音控制系统初始化失败: {e}")
                self.chat_area.add_message(f"语音系统初始化失败: {str(e)}", is_system=True)
        else:
            print("语音控制系统模块未找到，使用模拟模式")
            self.setup_demo_mode()
    
    def setup_demo_mode(self):
        """设置演示模式"""
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.demo_message)
        
        # 模拟激活状态变化
        QTimer.singleShot(3000, lambda: self.on_status_changed("系统待命 - 等待唤醒"))
        QTimer.singleShot(6000, lambda: self.on_text_recognized("[A机] 已激活"))
        QTimer.singleShot(9000, lambda: self.on_text_recognized("[A机] 平飞。"))
        QTimer.singleShot(12000, lambda: self.on_text_recognized("指令结束"))
    
    def demo_message(self):
        """演示消息"""
        import random
        messages = [
            "[B机] 已激活",
            "[B机] 左转。",
            "[C机] 爬升。",
            "[D机] 返航。",
            "指令结束"
        ]
        self.on_text_recognized(random.choice(messages))
    
    def auto_start_system(self):
        """自动启动系统"""
        if self.voice_system:
            if self.voice_system.start_system():
                self.system_running = True
                self.control_button.setText("🔴 停止系统")
                self.control_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 20px;
                        padding: 0 20px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                self.status_indicator.set_active(True)
                self.chat_area.add_message("系统已自动启动，可以开始语音交互", is_system=True)
            else:
                self.chat_area.add_message("系统启动失败", is_system=True)
        else:
            self.system_running = True
            self.control_button.setText("🔴 停止系统")
            self.status_indicator.set_active(True)
            self.chat_area.add_message("演示模式已启动", is_system=True)
            self.demo_timer.start(5000)
    
    def toggle_system(self):
        """切换系统状态"""
        if hasattr(self, 'system_running') and self.system_running:
            # 停止系统
            if self.voice_system:
                self.voice_system.stop_system()
            else:
                if hasattr(self, 'demo_timer'):
                    self.demo_timer.stop()
            
            self.system_running = False
            self.control_button.setText("▶️ 启动系统")
            self.control_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.status_indicator.set_active(False)
            self.status_indicator.set_listening(False)
            self.chat_area.add_message("系统已停止", is_system=True)
        else:
            # 启动系统
            self.auto_start_system()
    
    def on_text_recognized(self, text):
        """处理识别到的文本"""
        if text:
            is_system_msg = text.startswith("系统") or "已激活" in text or "指令结束" in text
            self.chat_area.add_message(text, is_system=is_system_msg)
            
            # 设置监听状态
            if "已激活" in text:
                self.status_indicator.set_listening(True)
            elif "指令结束" in text:
                self.status_indicator.set_listening(False)
    
    def on_status_changed(self, status):
        """处理状态变化"""
        self.status_label.setText(status)
        self.chat_area.add_message(f"状态: {status}", is_system=True)
        
        # 更新状态指示器
        if "已激活" in status:
            self.status_indicator.set_listening(True)
        elif "待命" in status:
            self.status_indicator.set_listening(False)
    
    def closeEvent(self, event):
        """关闭事件"""
        if hasattr(self, 'system_running') and self.system_running:
            if self.voice_system:
                self.voice_system.stop_system()
        
        # 停止音频采集
        if hasattr(self, 'audio_wave'):
            self.audio_wave.stop_audio_capture()
        
        event.accept()

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 创建并显示主窗口
    window = ModernVoiceControlUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()