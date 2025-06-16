# 全局导入
import sys
import threading
import time
import queue
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QTextEdit, QPushButton,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor, QFont
import speech_recognition as sr
import pathlib
MIC_PATH = pathlib.Path(__file__).parent.parent / "/icon/mic.png"
STOP_PATH = pathlib.Path(__file__).parent.parent / "/icon/stop circle.png"

class VoiceRecorder(QObject):
    """语音录音组件"""
    
    # 信号定义
    text_recognized = pyqtSignal(str)  # 识别到文本时发出信号
    recording_started = pyqtSignal()   # 开始录音时发出信号
    recording_stopped = pyqtSignal()   # 停止录音时发出信号
    error_occurred = pyqtSignal(str)   # 发生错误时发出信号
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.voice_available = False
        self.recognizer = None
        self.microphone = None
        self.record_thread = None
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        
        self.init_voice_recognition()
    
    def init_voice_recognition(self):
        """初始化语音识别相关组件"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.voice_available = True
            
            # 调整环境噪音
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
            # 设置更短的超时时间和更低的能量阈值，提高响应速度
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.dynamic_energy_adjustment_damping = 0.15
            self.recognizer.dynamic_energy_ratio = 1.5
            self.recognizer.pause_threshold = 0.8  # 降低停顿阈值
            self.recognizer.phrase_threshold = 0.3  # 降低短语阈值
                
        except ImportError:
            self.voice_available = False
            self.error_occurred.emit("语音识别库未安装，请安装: pip install SpeechRecognition pyaudio")
        except Exception as e:
            self.voice_available = False
            self.error_occurred.emit(f"语音识别初始化失败: {e}")
    
    def start_recording(self):
        """开始录音"""
        if not self.voice_available:
            self.error_occurred.emit("语音功能不可用")
            return False
            
        if self.is_recording:
            return False
            
        self.is_recording = True
        self.recording_started.emit()
        
        # 清空音频队列
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # 启动录音线程（持续占用麦克风）
        self.record_thread = threading.Thread(target=self.continuous_record)
        self.record_thread.daemon = True
        self.record_thread.start()
        
        # 启动音频处理线程
        self.processing_thread = threading.Thread(target=self.process_audio_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        return True
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return False
            
        self.is_recording = False
        self.recording_stopped.emit()
        
        # 等待线程结束
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=2)
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2)
            
        return True
    
    def continuous_record(self):
        """持续录音 - 保持麦克风占用"""
        if not self.voice_available:
            return
            
        try:
            # 一次性打开麦克风，持续使用
            with self.microphone as source:
                print("开始持续录音...")
                
                while self.is_recording:
                    try:
                        # 使用较短的超时时间，确保能及时响应停止信号
                        audio_data = self.recognizer.listen(
                            source, 
                            timeout=0.5,           # 等待语音开始的超时时间
                            phrase_time_limit=3    # 单次录音片段的最大时长
                        )
                        
                        if not self.is_recording:
                            break
                            
                        # 将音频数据放入队列，由另一个线程处理
                        try:
                            self.audio_queue.put(audio_data, timeout=0.1)
                        except queue.Full:
                            # 队列满了，丢弃最旧的音频
                            try:
                                self.audio_queue.get_nowait()
                                self.audio_queue.put(audio_data, timeout=0.1)
                            except queue.Empty:
                                pass
                                
                    except sr.WaitTimeoutError:
                        # 等待超时，继续录音
                        continue
                    except Exception as e:
                        if self.is_recording:  # 只有在录音状态下才报告错误
                            self.error_occurred.emit(f"录音错误: {e}")
                        break
                        
        except Exception as e:
            if self.is_recording:
                self.error_occurred.emit(f"麦克风访问错误: {e}")
        
        print("录音线程结束")
    
    def process_audio_queue(self):
        """处理音频队列中的音频数据"""
        print("开始处理音频队列...")
        
        while self.is_recording or not self.audio_queue.empty():
            try:
                # 从队列中获取音频数据
                audio_data = self.audio_queue.get(timeout=1)
                
                if not self.is_recording and self.audio_queue.empty():
                    break
                
                # 识别语音
                try:
                    text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                    if text and text.strip():
                        self.text_recognized.emit(text.strip())
                        print(f"识别到: {text.strip()}")
                        
                except sr.UnknownValueError:
                    # 无法识别的音频片段
                    pass
                except sr.RequestError as e:
                    # 网络错误
                    if self.is_recording:
                        self.error_occurred.emit(f"语音识别服务错误: {e}")
                except Exception as e:
                    if self.is_recording:
                        self.error_occurred.emit(f"语音识别错误: {e}")
                        
                # 标记任务完成
                self.audio_queue.task_done()
                
            except queue.Empty:
                # 队列为空，继续等待
                continue
            except Exception as e:
                if self.is_recording:
                    self.error_occurred.emit(f"音频处理错误: {e}")
                break
        
        print("音频处理线程结束")


class AnimatedRecordButton(QPushButton):
    """带动画效果的录音按钮"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 52)
        self.setIcon(QIcon("./icon/mic.png"))
        self.setIconSize(QSize(24, 24))
        self.setToolTip("点击开始录音")
        
        # 动画相关属性
        self.is_recording = True
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        
        # 光圈动画参数
        self.ring_opacity = 0.0
        self.ring_scale = 1.0
        self.animation_direction = 1
        self.animation_speed = 0.050  # 降低速度，更优雅
        
        # 图标
        self.mic_icon = QIcon("./icon/mic.png")
        self.stop_icon = QIcon("./icon/stop circle.png")
        
        self.setup_style()
    
    def setup_style(self):
        """设置按钮样式"""
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
    
    def start_recording_animation(self):
        """开始录音动画"""
        self.is_recording = True
        self.setIcon(self.stop_icon)
        self.setToolTip("点击停止录音")
        
        # 重置动画参数
        self.ring_opacity = 0.0
        self.ring_scale = 1.0
        self.animation_direction = 1
        
        # 开始动画定时器
        self.animation_timer.start(50)  # 50ms更新一次，更流畅但不过快
        self.setStyleSheet("""
            QPushButton{
                background-color: #f8f9fa;
                border: 2px solid #34a853;
                color: #34a853;
            }
        """)


    def stop_recording_animation(self):
        """停止录音动画"""
        self.is_recording = False
        self.setIcon(self.mic_icon)
        self.setToolTip("点击开始录音")
        
        # 停止动画
        self.animation_timer.stop()
        
        # 恢复原始样式
        self.setup_style()
        
        # 清除阴影效果
        if hasattr(self, 'shadow_effect'):
            self.setGraphicsEffect(None)
            delattr(self, 'shadow_effect')
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #34a853;
                border: 2px solid #e8eaed;
        """)
        self.update()
    
    def update_animation(self):
        """更新动画效果"""
        if not self.is_recording:
            return
            
        # 更新光圈透明度
        self.ring_opacity += self.animation_direction * self.animation_speed
        
        if self.ring_opacity >= 0.6:
            self.animation_direction = -1
        elif self.ring_opacity <= 0.0:
            self.animation_direction = 1
            
        # 将透明度限制在0-1之间
        self.ring_opacity = max(0.0, min(1.0, self.ring_opacity))
        
        # 计算边框宽度（动态变化营造呼吸感）
        border_width = 2 + int(3 * self.ring_opacity)
        
        # 计算颜色透明度（转换为0-255范围）
        alpha_value = int(255 * self.ring_opacity * 0.6)  # 最大透明度60%
        
        # 更新样式
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #fef7f7);
                color: #ea4335;
                border: {border_width}px solid rgba(234, 67, 53, {alpha_value});
                border-radius: 26px;
                font-size: 14px;
                font-weight: 600;
                font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #fef7f7);
                color: #ea4335;
                border: {border_width}px solid rgba(234, 67, 53, {alpha_value});
            }}
            """)
        
        # 添加阴影效果
        shadow_blur = max(5, int(20 * self.ring_opacity))
        shadow_alpha = min(255, int(150 * self.ring_opacity))
        
        if not hasattr(self, 'shadow_effect'):
            self.shadow_effect = QGraphicsDropShadowEffect()
            self.shadow_effect.setOffset(0, 0)
            self.setGraphicsEffect(self.shadow_effect)
        
        self.shadow_effect.setBlurRadius(shadow_blur)
        self.shadow_effect.setColor(QColor(234, 67, 53, shadow_alpha))