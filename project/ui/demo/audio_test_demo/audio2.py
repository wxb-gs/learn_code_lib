import sys
import pyaudio
import wave
import threading
import time
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QProgressBar, QFrame)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QLinearGradient
from PyQt5.QtCore import QRect, pyqtProperty

class PulseButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self._pulse_radius = 0
        self.animation = QPropertyAnimation(self, b"pulse_radius")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(30)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.setLoopCount(-1)  # 无限循环
        
    @pyqtProperty(int)
    def pulse_radius(self):
        return self._pulse_radius
    
    @pulse_radius.setter
    def pulse_radius(self, value):
        self._pulse_radius = value
        self.update()
    
    def start_pulse(self):
        self.animation.start()
    
    def stop_pulse(self):
        self.animation.stop()
        self._pulse_radius = 0
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._pulse_radius > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 绘制脉冲效果
            center = self.rect().center()
            color = QColor(255, 69, 58, max(0, 100 - self._pulse_radius * 3))
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(QColor(255, 69, 58, max(0, 30 - self._pulse_radius))))
            painter.drawEllipse(center.x() - self._pulse_radius, 
                              center.y() - self._pulse_radius,
                              self._pulse_radius * 2, 
                              self._pulse_radius * 2)

class AudioRecorder(QThread):
    audio_level = pyqtSignal(float)
    recording_finished = pyqtSignal(str)
    silence_detected = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # 音频参数
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.silence_threshold = 500  # 静音阈值
        self.silence_duration = 2.0   # 静音持续时间（秒）
        self.max_duration = 8.0       # 最大录音时间（秒）
        
        self.recording = False
        self.frames = []
        
    def run(self):
        audio = pyaudio.PyAudio()
        
        try:
            stream = audio.open(format=self.format,
                              channels=self.channels,
                              rate=self.rate,
                              input=True,
                              frames_per_buffer=self.chunk)
            
            self.frames = []
            silence_start = None
            start_time = time.time()
            
            while self.recording:
                data = stream.read(self.chunk)
                self.frames.append(data)
                
                # 计算音频级别
                audio_data = np.frombuffer(data, dtype=np.int16)
                audio_level = np.sqrt(np.mean(audio_data**2))
                self.audio_level.emit(audio_level)
                
                # 检查静音
                if audio_level < self.silence_threshold:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > self.silence_duration:
                        self.silence_detected.emit()
                        break
                else:
                    silence_start = None
                
                # 检查最大录音时间
                if time.time() - start_time > self.max_duration:
                    break
            
            stream.stop_stream()
            stream.close()
            
            # 保存录音文件
            if self.frames:
                filename = f"recording_{int(time.time())}.wav"
                wf = wave.open(filename, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
                wf.close()
                self.recording_finished.emit(filename)
            
        except Exception as e:
            print(f"录音错误: {e}")
        finally:
            audio.terminate()
    
    def start_recording(self):
        self.recording = True
        self.start()
    
    def stop_recording(self):
        self.recording = False

class WaveWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_levels = [0] * 50
        self.setFixedHeight(80)
        
    def update_level(self, level):
        # 标准化音频级别
        normalized_level = min(level / 3000.0, 1.0)
        self.audio_levels.append(normalized_level)
        self.audio_levels.pop(0)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        # 绘制波形
        width = self.width()
        height = self.height()
        bar_width = width / len(self.audio_levels)
        
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(0, 255, 127))
        gradient.setColorAt(0.5, QColor(255, 215, 0))
        gradient.setColorAt(1, QColor(255, 69, 58))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        
        for i, level in enumerate(self.audio_levels):
            bar_height = level * height
            x = i * bar_width
            y = height - bar_height
            painter.drawRect(int(x), int(y), int(bar_width - 1), int(bar_height))

class RecordingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recorder = AudioRecorder()
        self.recording_timer = QTimer()
        self.recording_time = 0
        self.is_recording = False
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        self.setWindowTitle("智能录音助手")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #3498db);
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 10px;
                background-color: #2c3e50;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #f39c12);
                border-radius: 8px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("🎤 智能录音助手")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # 状态显示
        self.status_label = QLabel("准备录音")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(self.status_label)
        
        # 时间显示
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(self.time_label)
        
        # 波形显示
        self.wave_widget = WaveWidget()
        layout.addWidget(self.wave_widget)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(int(self.recorder.max_duration * 10))
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("录音进度 %p%")
        layout.addWidget(self.progress_bar)
        
        # 录音按钮
        self.record_button = PulseButton("🎤 开始录音")
        self.record_button.setFixedSize(200, 60)
        self.record_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                border: none;
                border-radius: 30px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #229954, stop:1 #28b463);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e8449, stop:1 #239b56);
            }
        """)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.record_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 提示信息
        self.tip_label = QLabel("💡 提示：超过2秒静音或8秒后自动停止录音")
        self.tip_label.setAlignment(Qt.AlignCenter)
        self.tip_label.setStyleSheet("font-size: 12px; color: #bdc3c7; margin-top: 20px;")
        layout.addWidget(self.tip_label)
        
    def setup_connections(self):
        self.record_button.clicked.connect(self.toggle_recording)
        self.recorder.audio_level.connect(self.wave_widget.update_level)
        self.recorder.recording_finished.connect(self.on_recording_finished)
        self.recorder.silence_detected.connect(self.on_silence_detected)
        self.recording_timer.timeout.connect(self.update_timer)
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        self.is_recording = True
        self.recording_time = 0
        
        # 更新UI
        self.record_button.setText("⏹️ 停止录音")
        self.record_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                border: none;
                border-radius: 30px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cb4335, stop:1 #a93226);
            }
        """)
        self.record_button.start_pulse()
        self.status_label.setText("🔴 正在录音...")
        self.progress_bar.setValue(0)
        
        # 开始录音和计时
        self.recorder.start_recording()
        self.recording_timer.start(100)  # 每100ms更新一次
        
    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.recorder.stop_recording()
            self.recording_timer.stop()
            
            # 重置UI
            self.record_button.stop_pulse()
            self.record_button.setText("🎤 开始录音")
            self.record_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #27ae60, stop:1 #2ecc71);
                    border: none;
                    border-radius: 30px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #229954, stop:1 #28b463);
                }
            """)
            
    def update_timer(self):
        if self.is_recording:
            self.recording_time += 0.1
            minutes = int(self.recording_time // 60)
            seconds = int(self.recording_time % 60)
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
            
            # 更新进度条
            progress = min(int(self.recording_time * 10), self.progress_bar.maximum())
            self.progress_bar.setValue(progress)
            
            # 检查是否达到最大时间
            if self.recording_time >= self.recorder.max_duration:
                self.stop_recording()
                self.status_label.setText("⚠️ 录音时间已达上限")
    
    def on_silence_detected(self):
        self.stop_recording()
        self.status_label.setText("🔇 检测到静音，录音已停止")
        
    def on_recording_finished(self, filename):
        self.status_label.setText(f"✅ 录音已保存: {filename}")
        self.time_label.setText("00:00")
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QApplication {
            font-family: "Microsoft YaHei", "SimHei", sans-serif;
        }
    """)
    
    window = RecordingApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()