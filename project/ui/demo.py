import sys
import time
import torch
import numpy as np
import pyaudio
import wave
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                             QVBoxLayout, QWidget, QLabel, QGraphicsDropShadowEffect)
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtCore import QSize


class VoiceActivityThread(QThread):
    """语音活动检测线程"""
    voice_activity_changed = pyqtSignal(bool)  # 语音活动状态变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.frame_size = 512
        self.confidence_threshold = 0.5  # 调整阈值以获得更好的检测效果
        self.current_voice_state = False
        self.voice_buffer = []  # 用于平滑语音检测
        self.buffer_size = 5
        self._setup_vad_model()
        self._init_audio()
        
        
    def _setup_vad_model(self):
        """设置VAD模型"""
        try:
            print("正在加载VAD模型...")
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True,
                source='github'
            )
            print("VAD模型加载成功")
        except Exception as e:
            print(f"模型加载失败: {e}")
            try:
                self.model, self.utils = torch.hub.load(
                    'snakers4/silero-vad',
                    'silero_vad',
                    force_reload=False
                )
                print("使用备用方式加载成功")
            except Exception as e2:
                print(f"备用加载方式也失败: {e2}")
                raise Exception("无法加载VAD模型")
    
    def _init_audio(self):
        """初始化音频"""
        self.audio = pyaudio.PyAudio()
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=self.frame_size
            )
            print("音频流初始化成功")
        except Exception as e:
            print(f"音频流初始化失败: {e}")
            raise
    
    def int2float(self, sound):
        """将音频从int16转换为float32"""
        abs_max = np.abs(sound).max()
        sound = sound.astype('float32')
        if abs_max > 0:
            sound /= abs_max
        sound = sound.clip(-1, 1)
        return sound
    
    def start_detection(self):
        """开始语音检测"""
        if not self.running:
            self.running = True
            self.start()
    
    def stop_detection(self):
        """停止语音检测"""
        self.running = False
        if self.isRunning():
            self.quit()
            self.wait()
    
    def run(self):
        """主检测循环"""
        print("语音检测线程启动")
        self.current_voice_state = False
        self.voice_buffer = []
        
        while self.running:
            try:
                # 读取音频数据
                audio_chunk = self.stream.read(self.frame_size, exception_on_overflow=False)
                audio_int16 = np.frombuffer(audio_chunk, np.int16)
                audio_float32 = self.int2float(audio_int16)
                
                # VAD检测
                confidence = self.model(torch.from_numpy(audio_float32), 16000).item()
                
                # 添加到缓冲区进行平滑处理
                self.voice_buffer.append(confidence > self.confidence_threshold)
                if len(self.voice_buffer) > self.buffer_size:
                    self.voice_buffer.pop(0)
                
                # 计算平均值决定语音状态
                voice_active = sum(self.voice_buffer) > len(self.voice_buffer) // 2
                
                # 如果状态发生变化，发送信号
                if voice_active != self.current_voice_state:
                    self.current_voice_state = voice_active
                    self.voice_activity_changed.emit(voice_active)
                    print(f"语音状态变化: {'活跃' if voice_active else '静默'}")
                
                time.sleep(0.01)  # 稍微延时以减少CPU使用
                
            except Exception as e:
                print(f"语音检测错误: {e}")
                time.sleep(0.1)
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'audio') and self.audio:
            self.audio.terminate()


class AnimatedRecordButton(QPushButton):
    """带语音检测动画效果的录音按钮"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
         # 图标
        self.mic_icon = QIcon("./icon/mic.png")
        self.stop_icon = QIcon("./icon/stop circle.png")
        self.setFixedSize(52, 52)
        self.setIcon(QIcon("./icon/mic.png"))
        self.setIconSize(QSize(24, 24))
        self.setToolTip("点击开始录音")

        # 状态变量
        self.is_recording = False
        self.is_voice_active = False
        
        # 动画相关
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.ring_opacity = 0.0
        self.animation_direction = 1
        self.animation_speed = 0.1
        
        # 语音检测线程
        self.voice_thread = VoiceActivityThread()
        self.voice_thread.voice_activity_changed.connect(self.on_voice_activity_changed)
        
        self.setup_style()
    
    def setup_style(self):
        """设置默认样式"""
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #34a853;
                border: 2px solid #e8eaed;
                border-radius: 26px;
                font-size: 14px;
                font-weight: 500;
                font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
            }
            QPushButton:pressed {
                background-color: #e8f5e8;
            }
            """)
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return
        
        self.is_recording = True
        self.setIcon(self.stop_icon)
        self.setToolTip("录音中... 点击停止录音")
        
        # 增加了绿圈
        self.setStyleSheet("""
            QPushButton{
                background-color: #f8f9fa;
                border: 2px solid #34a853;
                color: #34a853;
            }
        """)
        
        # 开始语音检测
        try:
            self.voice_thread.start_detection()
            print("开始录音，启动语音检测")
        except Exception as e:
            print(f"启动语音检测失败: {e}")
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.is_voice_active = False
        self.setIcon(self.mic_icon)
        self.setToolTip("点击开始录音")
        
        # 停止语音检测
        self.voice_thread.stop_detection()
        
        # 停止动画
        self.animation_timer.stop()
        
        # 恢复默认样式
        self.setup_style()
        
        # 清除特效
        self.setGraphicsEffect(None)
        
        print("停止录音")
    
    def on_voice_activity_changed(self, is_active):
        """语音活动状态变化回调"""
        if not self.is_recording:
            return
        
        if is_active and not self.is_voice_active:
            # 检测到语音，开始动画
            self.is_voice_active = True
            self.start_voice_animation()
        elif not is_active and self.is_voice_active:
            # 语音结束，停止动画
            self.is_voice_active = False
            self.stop_voice_animation()
    
    def start_voice_animation(self):
        """开始语音检测动画（红色脉冲）"""
        self.ring_opacity = 0.0
        self.animation_direction = 1
        self.animation_timer.start(50)  # 50ms更新一次
        print("🔴 检测到语音，开始动画")
    
    def stop_voice_animation(self):
        """停止语音动画，回到录音待机状态"""
        self.animation_timer.stop()
        
        # 回到录音待机状态（蓝色）
        self.setStyleSheet("""
            QPushButton {
                background-color: #e3f2fd;
                color: #1976d2;
                border: 3px solid #1976d2;
                border-radius: 40px;
                font-size: 24px;
                font-weight: bold;
                font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
            }
        """)
        
        self.setGraphicsEffect(None)
        print("⚪ 语音结束，停止动画")
    
    def update_animation(self):
        """更新动画效果"""
        if not self.is_recording or not self.is_voice_active:
            return
        
        # 更新透明度
        self.ring_opacity += self.animation_direction * self.animation_speed
        
        if self.ring_opacity >= 1.0:
            self.animation_direction = -1
        elif self.ring_opacity <= 0.3:
            self.animation_direction = 1
        
        self.ring_opacity = max(0.3, min(1.0, self.ring_opacity))
        
        # 动态边框宽度
        border_width = 3 + int(4 * self.ring_opacity)
        alpha_value = int(255 * self.ring_opacity)
        
        # 红色脉冲样式
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:0.5 #ffebee, stop:1 #fef7f7);
                color: #d32f2f;
                border: {border_width}px solid rgba(211, 47, 47, {alpha_value});
                border-radius: 40px;
                font-size: 24px;
                font-weight: bold;
                font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
            }}
        """)
        
        # 添加阴影效果
        shadow_blur = max(10, int(25 * self.ring_opacity))
        shadow_alpha = min(180, int(150 * self.ring_opacity))
        
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setOffset(0, 0)
        shadow_effect.setBlurRadius(shadow_blur)
        shadow_effect.setColor(QColor(211, 47, 47, shadow_alpha))
        self.setGraphicsEffect(shadow_effect)
    
    def mousePressEvent(self, event):
        """处理鼠标点击"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
        super().mousePressEvent(event)
    
    def closeEvent(self, event):
        """清理资源"""
        if self.is_recording:
            self.stop_recording()
        if hasattr(self, 'voice_thread'):
            self.voice_thread.cleanup()
        super().closeEvent(event)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("语音检测动画录音按钮")
        self.setGeometry(300, 300, 400, 300)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # 标题
        title = QLabel("语音检测录音按钮")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei UI", 16, QFont.Bold))
        title.setStyleSheet("color: #333; margin: 20px;")
        
        # 说明文字
        instruction = QLabel("点击按钮开始录音\n检测到语音时按钮会显示红色脉冲动画")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setFont(QFont("Microsoft YaHei UI", 10))
        instruction.setStyleSheet("color: #666; margin: 10px; line-height: 1.5;")
        
        # 录音按钮
        self.record_button = AnimatedRecordButton()
        
        # 状态标签
        self.status_label = QLabel("点击按钮开始录音")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Microsoft YaHei UI", 10))
        self.status_label.setStyleSheet("color: #888; margin: 10px;")
        
        # 添加到布局
        layout.addWidget(title)
        layout.addWidget(instruction)
        layout.addWidget(self.record_button)
        layout.addWidget(self.status_label)
        
        central_widget.setLayout(layout)
        
        # 连接信号更新状态
        self.record_button.voice_thread.voice_activity_changed.connect(self.update_status)
    
    def update_status(self, is_active):
        """更新状态显示"""
        if self.record_button.is_recording:
            if is_active:
                self.status_label.setText("🔴 检测到语音...")
                self.status_label.setStyleSheet("color: #d32f2f; margin: 10px; font-weight: bold;")
            else:
                self.status_label.setText("⚪ 录音中，等待语音...")
                self.status_label.setStyleSheet("color: #1976d2; margin: 10px;")
        else:
            self.status_label.setText("点击按钮开始录音")
            self.status_label.setStyleSheet("color: #888; margin: 10px;")
    
    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        if hasattr(self, 'record_button'):
            self.record_button.closeEvent(event)
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #fafafa;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()