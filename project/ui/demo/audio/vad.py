from PyQt5.QtCore import QThread, pyqtSignal
import time
import torch
import numpy as np
import pyaudio
import wave
import sys
import requests
import os

# 将VAD代码封装成一个线程类
class VADThread(QThread):
    vad_detected = pyqtSignal(str)  # 语音活动检测信号 np.ndarray
    def __init__(self, parent=None):
        super().__init__(parent)
        # 加载模型和工具函数 - 修复了repo路径
        try:
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',  # 修正：添加完整的GitHub仓库路径
                model='silero_vad',
                force_reload=False,  # 可选：避免每次都重新下载
                trust_repo=True,
                source='github'
            )
        except Exception as e:
            print(f"模型加载失败: {e}")
            print("尝试使用备用方式加载模型...")
            try:
                # 备用方式：直接使用预训练模型
                self.model, self.utils = torch.hub.load(
                    'snakers4/silero-vad',
                    'silero_vad',
                    force_reload=False
                )
            except Exception as e2:
                print(f"备用加载方式也失败: {e2}")
                sys.exit(1)
        
        self.running = False
        self.pause = False
        self.audio_stream = None
        self.audio_data = None
        self.audio_paths = "./current_speech.wav"
        self.frame_size = 512  # 帧大小
        self.confidence_threshold = 0.8  # VAD 置信度阈值
        self.countSize = 0  # 语音记录长度计数
        self.record_size = 0
        self.last_audio_chunk_list = []
        self.record_button_clicked = False
        self.is_recording = False
        self.is_activing = False
        
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
            sys.exit(1)

    def set_activation_state(self, is_active):
        """设置激活状态"""
        self.is_activing = is_active

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

    def run(self):
        self.running = True
        self.pause = False
        print("VAD线程启动，请开始说话...")
        self.audio_data = None
        self.is_recording = False
        self.is_activing = False
        self.start_time = 0
        self.record_size = 0
        test_num = 0
        
        while self.running:
            if self.pause:
                time.sleep(0.1)
                continue
            
            try:
                # 读取一帧音频
                audio_chunk = self.stream.read(self.frame_size, exception_on_overflow=False)
                
                if self.record_button_clicked is False:  # 如果没有按键按下则执行自动语音活动检测
                    if self.is_activing is True:
                        threshold = 15  # 静音等待时间缩短，实现类流式语音识别
                        threshold = max(15 - self.record_size // 10, 5)
                    else:
                        threshold = 15  # 确保指令之间有停顿
                    
                    audio_int16 = np.frombuffer(audio_chunk, np.int16)
                    audio_float32 = self.int2float(audio_int16)
                    
                    # 使用VAD模型检测语音活动
                    new_confidence = self.model(torch.from_numpy(audio_float32), 16000).item()
                    
                    # 如果检测到语音活动
                    if new_confidence > self.confidence_threshold:
                        if self.is_recording is False:
                            self.is_recording = True
                        else:
                            self.countSize = 0
                    elif self.is_recording is True:
                        if self.countSize == 0:
                            self.start_time = time.time()
                        self.countSize += 1
                        if self.audio_data is not None and self.countSize >= threshold:
                            self.is_recording = False
                elif self.record_button_clicked is True:  # 如果按键按下则一直录音
                    pass

                # 进行音频录制
                if self.is_recording:
                    if self.audio_data is None:
                        # 将之前的音频数据追加到当前音频
                        self.audio_data = b''.join(self.last_audio_chunk_list)
                        self.audio_data += audio_chunk
                        # print("开始录音...")
                    else:
                        # 继续录制
                        self.audio_data += audio_chunk
                    self.record_size += 1
                elif self.audio_data is not None:
                    if self.record_size > threshold + 5:
                        # print(self.record_size)
                        self.save_audio_custom(self.audio_data)
                        # self.audio_data = self.int2float(np.frombuffer(self.audio_data, np.int16))
                        print("录音保存")
                        self.vad_detected.emit(self.audio_paths)
                    else:
                        print("录音太短")
                    self.audio_data = None
                    self.countSize = 0
                    self.record_size = 0

                # 保存录音前的一段音频，提高准确性
                self.last_audio_chunk_list.append(audio_chunk)
                if len(self.last_audio_chunk_list) > 30:
                    self.last_audio_chunk_list.pop(0)
                    
            except Exception as e:
                print(f"运行时错误: {e}")
                time.sleep(0.1)
                continue

    def stop(self):
        self.running = False
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'audio'):
            self.audio.terminate()

# 主程序：并启动线程
if __name__ == "__main__":
    # 创建并启动VAD线程
    vad_thread = VADThread()
    vad_thread.start()

    # 在主线程中运行一段时间，随后停止VAD线程
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止VAD线程...")
        vad_thread.running = False
        vad_thread.stop()
        vad_thread.wait()  # 等待线程结束