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

class VADDetectionThread(QThread):
    """VAD检测线程 - 负责检测语音活动并录音"""
    audio_detected = pyqtSignal(str)  # 检测到音频文件时发出信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 加载VAD模型
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4',
            model='silero_vad',
            trust_repo=None,
            source='local'
        )
        
        self.running = False
        self.pause = False
        self.frame_size = 512
        self.confidence_threshold = 0.8
        self.audio_path = "./current_speech.wav"
        
        # 录音状态
        self.is_recording = False
        self.audio_data = None
        self.count_size = 0
        self.record_size = 0
        self.last_audio_chunk_list = []
        self.is_activing = False  # 是否已激活状态
        
        # 初始化PyAudio
        self.audio = pyaudio.PyAudio()
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=self.frame_size
            )
        except Exception as e:
            print(f"Error opening audio stream: {e}")
    
    def int2float(self, sound):
        """将int16音频转换为float32"""
        abs_max = np.abs(sound).max()
        sound = sound.astype('float32')
        if abs_max > 0:
            sound /= abs_max
        sound = sound.clip(-1, 1)
        return sound
    
    def save_audio_custom(self, audio):
        """保存音频到文件"""
        with wave.open(self.audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio)
    
    def set_activation_state(self, is_active):
        """设置激活状态"""
        self.is_activing = is_active
    
    def run(self):
        """主运行循环"""
        self.running = True
        self.pause = False
        print("VAD检测线程启动，开始监听...")
        
        self.audio_data = None
        self.is_recording = False
        self.record_size = 0
        
        while self.running:
            if self.pause:
                time.sleep(0.1)
                continue
                
            try:
                # 读取音频帧
                audio_chunk = self.stream.read(self.frame_size, exception_on_overflow=False)
                
                # 设置静音阈值
                if self.is_activing:
                    threshold = max(15 - self.record_size // 10, 5)  # 激活状态下阈值更短
                else:
                    threshold = 15  # 未激活状态下需要较长停顿
                
                # VAD检测
                audio_int16 = np.frombuffer(audio_chunk, np.int16)
                audio_float32 = self.int2float(audio_int16)
                confidence = self.model(torch.from_numpy(audio_float32), 16000).item()
                
                # 语音活动检测逻辑
                if confidence > self.confidence_threshold:
                    if not self.is_recording:
                        self.is_recording = True
                        print("检测到语音，开始录音...")
                    else:
                        self.count_size = 0
                elif self.is_recording:
                    if self.count_size == 0:
                        self.start_time = time.time()
                    self.count_size += 1
                    if self.audio_data is not None and self.count_size >= threshold:
                        self.is_recording = False
                
                # 录音处理
                if self.is_recording:
                    if self.audio_data is None:
                        # 添加之前缓存的音频
                        self.audio_data = b''.join(self.last_audio_chunk_list)
                        self.audio_data += audio_chunk
                    else:
                        self.audio_data += audio_chunk
                    self.record_size += 1
                elif self.audio_data is not None:
                    # 录音结束，保存并发送
                    if self.record_size > threshold + 5:
                        self.save_audio_custom(self.audio_data)
                        print(f"录音完成，时长: {self.record_size} 帧")
                        self.audio_detected.emit(self.audio_path)
                    else:
                        print("录音太短，忽略")
                    
                    # 重置状态
                    self.audio_data = None
                    self.count_size = 0
                    self.record_size = 0
                
                # 维护音频缓存
                self.last_audio_chunk_list.append(audio_chunk)
                if len(self.last_audio_chunk_list) > 30:
                    self.last_audio_chunk_list.pop(0)
                    
            except Exception as e:
                print(f"VAD检测错误: {e}")
                break
    
    def stop(self):
        """停止检测"""
        self.running = False
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()