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

class AudioWaveWidget(QWidget):
    """音频波形显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("="*50 + "wave_audio start"+"="*50)
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
                background-color: #F3F5F6;
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
        print("="*50 + "wave_audio init end"+"="*50)
    
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
