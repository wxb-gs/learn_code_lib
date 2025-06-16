from PyQt5.QtCore import QObject, QThread, pyqtSignal
import time
import numpy as np
import torch
import pyaudio
import wave
import speech_recognition as sr
import queue
import threading
import os
import re
from pypinyin import pinyin, Style
from vad import VADThread
from speech_process import SpeechProcessingThread

class VoiceControlSystem(QObject):
    """语音控制系统主类"""
    text_recognized = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 创建线程
        self.vad_thread = VADThread()
        self.processing_thread = SpeechProcessingThread()
        
        # 连接信号
        self.vad_thread.vad_detected.connect(self.processing_thread.accept_audio)
        self.processing_thread.text_recognized.connect(self.text_recognized.emit)
        self.processing_thread.activation_changed.connect(self.vad_thread.set_activation_state)
        self.processing_thread.activation_changed.connect(self.on_activation_changed)
        
        self.is_running = False
    
    def on_activation_changed(self, is_active):
        """激活状态改变处理"""
        if is_active:
            self.status_changed.emit("系统已激活 - 等待指令")
        else:
            self.status_changed.emit("系统待命 - 等待唤醒")
    
    def start_system(self):
        """启动系统"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.processing_thread.start()
        self.vad_thread.start()
        self.status_changed.emit("语音控制系统启动")
        return True
    
    def stop_system(self):
        """停止系统"""
        if not self.is_running:
            return False
        
        self.is_running = False
        
        # 停止线程
        self.vad_thread.stop()
        self.processing_thread.stop()
        
        # 等待线程结束
        self.vad_thread.wait(3000)
        self.processing_thread.wait(3000)
        
        self.status_changed.emit("语音控制系统已停止")
        return True


# 使用示例
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton
    import sys
    
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("语音控制系统")
            self.setGeometry(100, 100, 600, 400)
            
            # 创建界面
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # 文本显示区域
            self.text_display = QTextEdit()
            self.text_display.setReadOnly(True)
            layout.addWidget(self.text_display)
            
            # 控制按钮
            self.start_button = QPushButton("启动系统")
            self.start_button.clicked.connect(self.toggle_system)
            layout.addWidget(self.start_button)
            
            # 创建语音控制系统
            self.voice_system = VoiceControlSystem()
            self.voice_system.text_recognized.connect(self.on_text_recognized)
            self.voice_system.status_changed.connect(self.on_status_changed)
            
            self.system_running = False
        
        def toggle_system(self):
            if not self.system_running:
                if self.voice_system.start_system():
                    self.system_running = True
                    self.start_button.setText("停止系统")
            else:
                if self.voice_system.stop_system():
                    self.system_running = False
                    self.start_button.setText("启动系统")
        
        def on_text_recognized(self, text):
            if text:
                self.text_display.append(f"识别: {text}")
        
        def on_status_changed(self, status):
            self.text_display.append(f"状态: {status}")
        
        def closeEvent(self, event):
            if self.system_running:
                self.voice_system.stop_system()
            event.accept()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())