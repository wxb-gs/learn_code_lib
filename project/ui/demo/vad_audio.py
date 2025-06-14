import sys
import time
import threading
import torch
import numpy as np
import pyaudio
import wave
from faster_whisper import WhisperModel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class VAD_Whisper(QObject):
    # 定义信号
    text_recognized = pyqtSignal(str)
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    
    def __init__(self, model_size="small", beam_size=5, language='zh', 
                 initial_prompt="这是一条控制指令，A机A机，B机B机，平飞，偏置飞行，直线加速，小角度盘旋，拉起发射，俯仰角10度，速度100马赫。"):
        super().__init__()
        self.model_size = model_size
        self.beam_size = beam_size
        self.language = language
        self.initial_prompt = initial_prompt
        self.condition_on_previous_text = True
        
        # 加载模型和工具函数
        try:
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4',
                model='silero_vad',
                trust_repo=None,
                source='local'
            )
        except:
            print("VAD模型加载失败，将使用简化版本")
            self.model = None
            
        self.running = False
        self.pause = False
        self.audio_paths = "./current_speech.wav"
        self.frame_size = 512
        self.confidence_threshold = 0.8
        self.countSize = 0
        self.record_size = 0
        self.last_audio_chunk_list = []
        self.record_button_clicked = False
        self.is_recording = False
        self.is_activing = False
        self.init_finish = False
        
        # 初始化PyAudio
        self.audio = pyaudio.PyAudio()
        try:
            self.stream = self.audio.open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=16000,
                                        input=True,
                                        frames_per_buffer=self.frame_size)
        except Exception as e:
            print(f"Error opening audio stream: {e}")
            self.stream = None

    def Init_model(self):
        try:
            if self.model_size in ["small","whisper-small","whisper-medium"]:
                self.whisper_model = WhisperModel(self.model_size, device="cuda")
            elif self.model_size in ["large-v3-turbo-ct2"]:
                self.whisper_model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
            elif self.model_size == "whisper-small-ct2-int8":
                self.whisper_model = WhisperModel(self.model_size, device="cuda", compute_type="int8_float16")
            else:
                # 使用CPU版本作为备选
                self.whisper_model = WhisperModel("base", device="cpu")
            self.init_finish = True
        except Exception as e:
            print(f"模型初始化失败: {e}")
            self.init_finish = False

    def int2float(self, sound):
        abs_max = np.abs(sound).max()
        sound = sound.astype('float32')
        if abs_max > 0:
            sound /= abs_max
        sound = sound.clip(-1, 1)
        return sound
    
    def save_audio_custom(self, audio):
        with wave.open(self.audio_paths, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio)

    def audio2text(self, audio):
        if not self.init_finish:
            return "模型未初始化"
            
        try:
            speech_text = None
            segments, info = self.whisper_model.transcribe(
                audio, 
                beam_size=self.beam_size, 
                language=self.language, 
                initial_prompt=self.initial_prompt, 
                condition_on_previous_text=self.condition_on_previous_text
            )
            
            for segment in segments:
                text_ = segment.text
                if speech_text is None:
                    speech_text = text_
                else:
                    speech_text += ", " + text_
                    
            if speech_text is None:
                return None
            else:
                speech_text = speech_text.replace(" ", "，")
                return speech_text
        except Exception as e:
            print(f"语音识别错误: {e}")
            return f"识别失败: {str(e)}"
        
    def start_recording(self):
        self.record_button_clicked = True
        self.is_recording = True
        self.recording_started.emit()
        
    def stop_recording(self):
        self.record_button_clicked = False
        self.recording_stopped.emit()
        
    def run(self):
        if not self.stream:
            return
            
        self.running = True
        self.pause = False
        self.audio_data = None
        self.is_recording = False
        self.is_activing = False
        self.start_time = 0
        self.record_size = 0
        self.Init_model()
        
        while self.running:
            if self.pause:
                time.sleep(0.1)
                continue
                
            try:
                audio_chunk = self.stream.read(self.frame_size, exception_on_overflow=False)
            except:
                continue
                
            if not self.record_button_clicked and self.model:
                audio_int16 = np.frombuffer(audio_chunk, np.int16)
                audio_float32 = self.int2float(audio_int16)
                new_confidence = self.model(torch.from_numpy(audio_float32), 16000).item()
                
                if new_confidence > self.confidence_threshold:
                    if not self.is_recording:
                        self.is_recording = True
                        self.recording_started.emit()
                    else:
                        self.countSize = 0
                elif self.is_recording:
                    if self.countSize == 0:
                        self.start_time = time.time()
                    self.countSize += 1
                    if self.audio_data is not None and self.countSize >= 20:
                        self.is_recording = False
                        self.recording_stopped.emit()

            if self.is_recording:
                if self.audio_data is None:
                    self.audio_data = b''.join(self.last_audio_chunk_list)
                    self.audio_data += audio_chunk
                else:
                    self.audio_data += audio_chunk
                self.record_size += 1
            elif self.audio_data is not None:
                if self.record_size > 25:
                    self.save_audio_custom(self.audio_data)
                    speech_text = self.audio2text(self.audio_paths)
                    if speech_text:
                        self.text_recognized.emit(speech_text)
                else:
                    self.text_recognized.emit("录音太短，请重新录制")
                    
                self.audio_data = None
                self.countSize = 0
                self.record_size = 0

            self.last_audio_chunk_list.append(audio_chunk)
            if len(self.last_audio_chunk_list) > 20:
                self.last_audio_chunk_list.pop(0)

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()


class PulseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.is_recording = False
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.update)
        self.pulse_value = 0
        self.pulse_direction = 1
        
    def start_pulse(self):
        self.is_recording = True
        self.pulse_timer.start(50)
        
    def stop_pulse(self):
        self.is_recording = False
        self.pulse_timer.stop()
        self.pulse_value = 0
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算脉冲效果
        if self.is_recording:
            self.pulse_value += self.pulse_direction * 5
            if self.pulse_value >= 30:
                self.pulse_direction = -1
            elif self.pulse_value <= 0:
                self.pulse_direction = 1
        
        # 绘制外圈（脉冲效果）
        if self.is_recording:
            pulse_color = QColor(74, 144, 226, 100 - self.pulse_value)
            painter.setBrush(QBrush(pulse_color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.rect().adjusted(-self.pulse_value//2, -self.pulse_value//2, 
                                                  self.pulse_value//2, self.pulse_value//2))
        
        # 绘制主按钮
        main_color = QColor(239, 68, 68) if self.is_recording else QColor(74, 144, 226)
        painter.setBrush(QBrush(main_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.rect().adjusted(10, 10, -10, -10))
        
        # 绘制麦克风图标
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.NoBrush)
        center = self.rect().center()
        
        # 麦克风身体
        mic_rect = QRect(center.x() - 8, center.y() - 15, 16, 20)
        painter.drawRoundedRect(mic_rect, 8, 8)
        
        # 麦克风底座
        painter.drawLine(center.x(), center.y() + 8, center.x(), center.y() + 18)
        painter.drawLine(center.x() - 8, center.y() + 18, center.x() + 8, center.y() + 18)
        
        # 录音时显示停止图标
        if self.is_recording:
            painter.setBrush(QBrush(Qt.white))
            stop_rect = QRect(center.x() - 6, center.y() - 6, 12, 12)
            painter.drawRect(stop_rect)


class ChatBubble(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.setMinimumHeight(60)
        
        # 设置布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        if is_user:
            layout.addStretch()
            
        # 创建消息气泡
        bubble = QLabel(text)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(f"""
            QLabel {{
                background-color: {'#4A90E2' if is_user else '#f0f0f0'};
                color: {'white' if is_user else 'black'};
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 14px;
                max-width: 300px;
            }}
        """)
        
        layout.addWidget(bubble)
        
        if not is_user:
            layout.addStretch()


class LoadingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.dots = 0
        
    def start_animation(self):
        self.timer.start(500)
        self.show()
        
    def stop_animation(self):
        self.timer.stop()
        self.hide()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制三个跳动的点
        colors = [QColor(150, 150, 150), QColor(100, 100, 100), QColor(150, 150, 150)]
        
        for i in range(3):
            color = colors[i] if (self.dots % 4) != i else QColor(74, 144, 226)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            x = 10 + i * 15
            y = 15 + (5 if (self.dots % 4) == i else 0)
            painter.drawEllipse(x, y, 8, 8)
            
        self.dots += 1


class VoiceChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_voice_system()
        
    def init_ui(self):
        self.setWindowTitle("语音助手 - ChatGPT风格")
        self.setGeometry(100, 100, 400, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        # 中央窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(60)
        title_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #4A90E2, stop:1 #357ABD);
                border-bottom: 1px solid #ddd;
            }
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)
        title_label = QLabel("🎤 语音助手")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 聊天区域
        self.chat_scroll = QScrollArea()
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(0, 20, 0, 20)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        self.chat_scroll.setWidget(self.chat_widget)
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 加载动画
        self.loading_widget = LoadingWidget()
        self.loading_widget.hide()
        
        # 底部控制区域
        bottom_widget = QWidget()
        bottom_widget.setFixedHeight(120)
        bottom_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #e9ecef;
            }
        """)
        
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(20, 20, 20, 20)
        
        # 状态标签
        self.status_label = QLabel("点击按钮开始语音输入")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                background: transparent;
            }
        """)
        
        # 录音按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.record_button = PulseButton()
        self.record_button.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.record_button)
        button_layout.addStretch()
        
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addLayout(button_layout)
        
        # 添加到主layout
        main_layout.addWidget(title_bar)
        main_layout.addWidget(self.chat_scroll)
        main_layout.addWidget(bottom_widget)
        
        # 初始化状态
        self.is_recording = False
        
        # 添加欢迎消息
        self.add_message("你好！我是你的语音助手，点击下方按钮开始语音对话。", False)
        
    def init_voice_system(self):
        # 创建语音识别对象
        self.vad_whisper = VAD_Whisper()
        
        # 连接信号
        self.vad_whisper.text_recognized.connect(self.on_text_recognized)
        self.vad_whisper.recording_started.connect(self.on_recording_started)
        self.vad_whisper.recording_stopped.connect(self.on_recording_stopped)
        
        # 在单独线程中运行
        self.voice_thread = threading.Thread(target=self.vad_whisper.run, daemon=True)
        self.voice_thread.start()
        
    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.is_recording = True
        self.record_button.start_pulse()
        self.status_label.setText("🎤 正在录音...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ef4444;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.vad_whisper.start_recording()
        
    def stop_recording(self):
        self.is_recording = False
        self.record_button.stop_pulse()
        self.status_label.setText("⏳ 正在识别...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4A90E2;
                font-size: 14px;
                background: transparent;
            }
        """)
        self.vad_whisper.stop_recording()
        self.loading_widget.start_animation()
        
    @pyqtSlot()
    def on_recording_started(self):
        if not self.is_recording:  # 自动检测开始录音
            self.is_recording = True
            self.record_button.start_pulse()
            self.status_label.setText("🎤 检测到语音，正在录音...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ef4444;
                    font-size: 14px;
                    font-weight: bold;
                    background: transparent;
                }
            """)
            
    @pyqtSlot()
    def on_recording_stopped(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.stop_pulse()
            self.status_label.setText("⏳ 正在识别...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #4A90E2;
                    font-size: 14px;
                    background: transparent;
                }
            """)
        
    @pyqtSlot(str)
    def on_text_recognized(self, text):
        self.loading_widget.stop_animation()
        self.status_label.setText("点击按钮开始语音输入")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                background: transparent;
            }
        """)
        
        if text and text.strip():
            self.add_message(text, True)
            # 这里可以添加对话逻辑，比如调用AI接口
            QTimer.singleShot(1000, lambda: self.add_message(f"收到您的消息：{text}", False))
            
    def add_message(self, text, is_user=True):
        bubble = ChatBubble(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        
        # 滚动到底部
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()))
        
    def closeEvent(self, event):
        self.vad_whisper.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用图标和样式
    app.setStyle('Fusion')
    
    window = VoiceChatApp()
    window.show()
    
    sys.exit(app.exec_())