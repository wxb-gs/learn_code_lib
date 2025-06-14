import time
import torch
import numpy as np
import pyaudio
import wave
import sys
from faster_whisper import WhisperModel
# 将VAD代码封装成一个线程类
class VAD_Whisper:
    def __init__(self, model_size="large-v3-turbo-ct2", beam_size=5, language='zh', 
                 initial_prompt="这是一条控制指令，A机A机，B机B机，平飞，偏置飞行，直线加速，小角度盘旋，拉起发射，俯仰角10度，速度100马赫。"):
        self.model_size = model_size
        self.beam_size = beam_size
        self.language = language
        self.initial_prompt = initial_prompt
        self.condition_on_previous_text = True
        # 加载模型和工具函数
        self.model, self.utils = torch.hub.load(
            repo_or_dir='snakers4',
            model='silero_vad',
            trust_repo=None,
            source='local'
        )
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

    def Init_model(self):
        if self.model_size in ["whisper-small","whisper-medium"]:
            self.whisper_model = WhisperModel(self.model_size, device="cuda")
        elif self.model_size in ["large-v3-turbo-ct2"]:
            self.whisper_model = WhisperModel(self.model_size, device="cuda", compute_type="float16")
        elif self.model_size == "whisper-small-ct2-int8":
            self.whisper_model = WhisperModel(self.model_size, device="cuda", compute_type="int8_float16")
        else:
            print("请选择对应模型或者修改代码")
        self.init_finish = True

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

        speech_text = None
        segments, info = self.whisper_model.transcribe(audio, beam_size=self.beam_size, language=self.language, initial_prompt=self.initial_prompt, condition_on_previous_text=self.condition_on_previous_text) # hotwords="A机A机",language_detection_threshold=0.5
        for segment in segments:
            text_ = segment.text
            # text_ = self.cc.convert(segment.text)
            if speech_text is None:
                speech_text = text_
            else:
                speech_text += ", " + text_
        if speech_text is None:
            return None
        else:
            speech_text = speech_text.replace(" ", "，")  # 将空格替换为中文逗号
            return speech_text
        
    def run(self):
        self.running = True
        self.pause = False
        
        self.audio_data = None
        self.is_recording = False
        self.is_activing = False
        self.start_time = 0
        self.record_size = 0
        self.Init_model()
        print("VAD线程启动，请开始说话...")
        while self.running:
            if self.pause:
                time.sleep(0.1)
                continue
            # 读取一帧音频
            audio_chunk = self.stream.read(self.frame_size,exception_on_overflow=False)
            if self.record_button_clicked is False: # 如果没有按键按下则执行自动语音活动检测
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
                    if self.audio_data is not None and self.countSize >= 20:
                        self.is_recording = False
            elif self.record_button_clicked is True: # 如果按键按下则一直录音
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
                if self.record_size > 20 + 5: 
                    # print(self.record_size)
                    self.save_audio_custom(self.audio_data)
                    # 将音频数据转换为识别格式并识别文本
                    speech_text = self.audio2text(self.audio_paths)
                    print("识别结果：", speech_text)
                    # self.audio_data = self.int2float(np.frombuffer(self.audio_data, np.int16))
                    # print("录音保存")
    
                else:
                    print("录音太短")
                self.audio_data = None
                self.countSize = 0
                self.record_size = 0

            # 保存录音前的一段音频，提高准确性
            self.last_audio_chunk_list.append(audio_chunk)
            if len(self.last_audio_chunk_list) > 20:
                self.last_audio_chunk_list.pop(0)


    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

# 主程序：加载VAD模型并启动线程
if __name__ == "__main__":
    # 创建并启动VAD线程
    vad_thread = VAD_Whisper()
    vad_thread.run()

    # 在主线程中运行一段时间，随后停止VAD线程
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止VAD线程...")
        vad_thread.stop()
