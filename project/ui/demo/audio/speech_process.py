
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

class SpeechProcessingThread(QThread):
    """语音处理线程 - 负责识别和指令处理"""
    text_recognized = pyqtSignal(str)  # 识别结果信号
    activation_changed = pyqtSignal(bool)  # 激活状态改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 初始化语音识别
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # 队列和状态
        self.audio_queue = queue.Queue(maxsize=10)
        self.running = False
        self.is_activing = False
        self.current_plane = ""
        
        # 唤醒词数据库
        self.wakeword_database = {
            "A机": ["A机", "AG", "阿机"],
            "B机": ["B机", "BG", "逼机"],
            "C机": ["C机", "CG", "西机"],
            "D机": ["D机", "DG", "迪机"],0
        }
        self.pinyin_wakeword_database = self.convert_wakewords_to_pinyin(self.wakeword_database)
        
        # 指令数据库
        self.instruct_database = [
            "平飞", "偏置", "盘旋", "扩包", "发射", "飞行", "直线",
            "加速", "减速", "爬升", "下降", "左转", "右转", "返航"
        ]
    
    def accept_audio(self, audio_path):
        """接收音频文件路径"""
        try:
            self.audio_queue.put(audio_path, timeout=0.1)
        except queue.Full:
            print("音频队列已满，丢弃音频")
    
    def get_pinyin(self, text):
        """获取文本的拼音"""
        segments = re.split(r'([^a-zA-Z0-9])', text)
        element_list = []
        element_type_list = []
        
        for segment in segments:
            if segment.strip():
                if re.match(r'^[a-zA-Z0-9]+$', segment):
                    element_list.append(segment)
                    element_type_list.append(0)
                else:
                    pinyin_segment = pinyin(segment, style=Style.NORMAL)
                    for item in pinyin_segment:
                        element_list.append(item[0])
                        element_type_list.append(1)
        
        return (element_list, element_type_list)
    
    def convert_wakewords_to_pinyin(self, wakeword_database):
        """转换唤醒词为拼音"""
        pinyin_database = {}
        for keyword, wakewords in wakeword_database.items():
            pinyin_database[keyword] = [self.get_pinyin(wakeword)[0] for wakeword in wakewords]
        return pinyin_database
    
    def search_pinyin_wakewords(self, pinyin_list, pinyin_wakeword_database):
        """搜索拼音唤醒词"""
        last_wakeword = None
        last_keyword = None
        last_index = -1
        element_list, element_type_list = pinyin_list
        text_str = ''.join(element_list)
        
        for keyword, pinyin_wakewords in pinyin_wakeword_database.items():
            for pinyin_wakeword in pinyin_wakewords:
                wakeword_str = ''.join(pinyin_wakeword)
                index = text_str.rfind(wakeword_str)
                
                if index != -1 and index > last_index:
                    last_index = index
                    last_wakeword = wakeword_str
                    last_keyword = keyword
        
        return last_keyword
    
    def process_string(self, input_str):
        """处理识别字符串"""
        # 查找 "over" 之前的内容
        match = re.search(r'(.*?)\s*over\b', input_str, flags=re.IGNORECASE)
        if match:
            content = match.group(1).strip()
        else:
            content = input_str.strip()
        
        # 处理标点
        if content.startswith('，') or content.startswith(','):
            content = content[1:]
        
        if content.endswith('。'):
            return content
        elif content.endswith(','):
            return content[:-1] + '。'
        elif content.endswith('，'):
            return content[:-1] + '。'
        else:
            return content + '。'
    
    def recognize_audio(self, audio_path):
        """识别音频文件"""
        try:
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
            
            # 使用Google语音识别
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            return text.strip() if text else None
            
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"语音识别服务错误: {e}")
            return None
        except Exception as e:
            print(f"音频识别错误: {e}")
            return None
    
    def run(self):
        """主处理循环"""
        self.running = True
        print("语音处理线程启动...")
        
        while self.running:
            try:
                # 从队列获取音频文件
                audio_path = self.audio_queue.get(timeout=1)
                
                # 识别音频
                speech_text = self.recognize_audio(audio_path)
                print(f"识别结果: {speech_text}")
                
                if speech_text is None:
                    self.text_recognized.emit("")
                    continue
                
                if not self.is_activing:
                    # 未激活状态 - 检测唤醒词
                    pinyin_text = self.get_pinyin(speech_text)
                    last_keyword = self.search_pinyin_wakewords(pinyin_text, self.pinyin_wakeword_database)
                    
                    if last_keyword is not None:
                        self.is_activing = True
                        self.current_plane = last_keyword
                        self.activation_changed.emit(True)
                        self.text_recognized.emit(f"[{last_keyword}] 已激活")
                        print(f"{last_keyword} 激活成功")
                    else:
                        self.text_recognized.emit("")
                else:
                    # 激活状态 - 处理指令
                    processed_text = self.process_string(speech_text)
                    
                    # 检查是否包含有效指令
                    instruct_enable = False
                    for instruct in self.instruct_database:
                        if instruct in processed_text:
                            instruct_enable = True
                            break
                    
                    if instruct_enable:
                        result_text = f"[{self.current_plane}] {processed_text}"
                        self.text_recognized.emit(result_text)
                        print(f"指令执行: {result_text}")
                    else:
                        # 检查是否为结束指令
                        if "结束" in processed_text or "完毕" in processed_text or "over" in processed_text.lower():
                            self.is_activing = False
                            self.current_plane = ""
                            self.activation_changed.emit(False)
                            self.text_recognized.emit(f"指令结束")
                            print("指令会话结束")
                        else:
                            self.text_recognized.emit("")
                
                # 标记任务完成
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"语音处理错误: {e}")
                continue
    
    def stop(self):
        """停止处理"""
        self.running = False
