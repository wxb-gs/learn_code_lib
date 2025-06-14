import sys
import time
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import speech_recognition as sr
import pyaudio

class PulseEffect(QWidget):
    """脉冲动画效果组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.pulse_radius = 40
        self.max_radius = 80
        self.is_recording = False
        
        # 动画定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pulse)
        
    def start_pulse(self):
        self.is_recording = True
        self.timer.start(50)  # 50ms间隔
        
    def stop_pulse(self):
        self.is_recording = False
        self.timer.stop()
        self.pulse_radius = 40
        self.update()
        
    def update_pulse(self):
        if self.is_recording:
            self.pulse_radius += 2
            if self.pulse_radius > self.max_radius:
                self.pulse_radius = 40
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        
        if self.is_recording:
            # 绘制脉冲圆环
            for i in range(3):
                alpha = max(0, 100 - i * 30 - (self.pulse_radius - 40) * 2)
                color = QColor(66, 165, 245, alpha)
                painter.setPen(QPen(color, 2))
                painter.setBrush(QBrush(color))
                radius = self.pulse_radius + i * 15
                painter.drawEllipse(center, radius, radius)
        
        # 绘制中心麦克风图标
        icon_color = QColor(244, 67, 54) if self.is_recording else QColor(158, 158, 158)
        painter.setPen(QPen(icon_color, 3))
        painter.setBrush(QBrush(icon_color))
        
        # 绘制麦克风形状
        mic_rect = QRect(center.x() - 15, center.y() - 20, 30, 35)
        painter.drawRoundedRect(mic_rect, 15, 15)
        
        # 麦克风底座
        painter.drawLine(center.x(), center.y() + 20, center.x(), center.y() + 35)
        painter.drawLine(center.x() - 10, center.y() + 35, center.x() + 10, center.y() + 35)

class VoiceInputWidget(QWidget):
    """语音输入主界面"""
    
    text_recognized = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.setup_ui()
        self.setup_speech_recognition()
        
    def setup_ui(self):
        self.setWindowTitle("ChatGPT风格语音输入")
        self.setFixedSize(600, 700)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #404040;
                border-color: #4285f4;
            }
            
            QPushButton:pressed {
                background-color: #505050;
            }
            
            QPushButton#recordButton {
                background-color: #4285f4;
                border-color: #4285f4;
                color: white;
            }
            
            QPushButton#recordButton:hover {
                background-color: #3367d6;
            }
            
            QPushButton#recordButton:pressed {
                background-color: #2455c4;
            }
            
            QPushButton#stopButton {
                background-color: #ea4335;
                border-color: #ea4335;
                color: white;
            }
            
            QPushButton#stopButton:hover {
                background-color: #d33b2c;
            }
            
            QTextEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 16px;
                font-size: 14px;
                line-height: 1.5;
            }
            
            QLabel {
                color: #e0e0e0;
                font-size: 16px;
            }
            
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #4285f4;
            }
            
            QLabel#statusLabel {
                font-size: 14px;
                color: #9e9e9e;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title_label = QLabel("🎤 语音输入助手")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 脉冲动画区域
        pulse_container = QWidget()
        pulse_container.setFixedHeight(220)
        pulse_layout = QHBoxLayout(pulse_container)
        pulse_layout.setContentsMargins(0, 0, 0, 0)
        
        self.pulse_effect = PulseEffect()
        pulse_layout.addWidget(self.pulse_effect, alignment=Qt.AlignCenter)
        layout.addWidget(pulse_container)
        
        # 状态标签
        self.status_label = QLabel("点击开始录音")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)
        
        self.record_button = QPushButton("🎙️ 开始录音")
        self.record_button.setObjectName("recordButton")
        self.record_button.clicked.connect(self.start_recording)
        
        self.stop_button = QPushButton("⏹️ 停止录音")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        
        self.clear_button = QPushButton("🗑️ 清空文本")
        self.clear_button.clicked.connect(self.clear_text)
        
        button_layout.addWidget(self.record_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)
        
        # 识别结果显示
        result_label = QLabel("识别结果:")
        layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("语音识别的文本将显示在这里...")
        self.result_text.setMaximumHeight(200)
        layout.addWidget(self.result_text)
        
        # 连接信号
        self.text_recognized.connect(self.on_text_recognized)
        
    def setup_speech_recognition(self):
        """设置语音识别"""
        try:
            # 调整环境噪音
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"设置语音识别失败: {e}")
    
    def start_recording(self):
        """开始录音"""
        if not self.is_listening:
            self.is_listening = True
            self.record_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            
            self.status_label.setText("🔴 正在录音，请说话...")
            self.pulse_effect.start_pulse()
            
            # 在新线程中进行语音识别
            threading.Thread(target=self.recognize_speech, daemon=True).start()
    
    def stop_recording(self):
        """停止录音"""
        self.is_listening = False
        self.record_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.status_label.setText("⏸️ 录音已停止，正在处理...")
        self.pulse_effect.stop_pulse()
    
    def recognize_speech(self):
        """语音识别线程"""
        try:
            with self.microphone as source:
                # 监听音频
                audio_data = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                
            if self.is_listening:
                # 使用Google语音识别 (需要网络连接)
                try:
                    text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                    self.text_recognized.emit(text)
                except sr.UnknownValueError:
                    self.text_recognized.emit("[无法识别语音内容]")
                except sr.RequestError as e:
                    self.text_recognized.emit(f"[识别服务错误: {e}]")
                    
        except sr.WaitTimeoutError:
            if self.is_listening:
                # 继续监听
                threading.Thread(target=self.recognize_speech, daemon=True).start()
        except Exception as e:
            self.text_recognized.emit(f"[录音错误: {e}]")
    
    def on_text_recognized(self, text):
        """处理识别到的文本"""
        current_text = self.result_text.toPlainText()
        if current_text:
            new_text = current_text + "\n" + text
        else:
            new_text = text
            
        self.result_text.setPlainText(new_text)
        
        # 自动滚动到底部
        cursor = self.result_text.textCursor()
        cursor.movePosition(cursor.End)
        self.result_text.setTextCursor(cursor)
        
        if self.is_listening:
            self.status_label.setText("🔴 继续录音中...")
            # 继续监听
            threading.Thread(target=self.recognize_speech, daemon=True).start()
        else:
            self.status_label.setText("✅ 识别完成")
    
    def clear_text(self):
        """清空文本"""
        self.result_text.clear()
        self.status_label.setText("📝 文本已清空")

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT风格语音输入Demo")
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        
        # 创建中心部件
        central_widget = VoiceInputWidget()
        self.setCentralWidget(central_widget)
        
        # 窗口居中
        self.center_window()
        
    def center_window(self):
        """窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("语音输入Demo")
    app.setApplicationVersion("1.0")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()