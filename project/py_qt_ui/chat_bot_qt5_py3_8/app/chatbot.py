import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QScrollArea, QFrame, 
                             QLabel, QLineEdit, QSizePolicy)
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from langchain_ollama import ChatOllama
from langchain.schema.messages import HumanMessage

# 初始化LLM
llm = ChatOllama(model="qwen2.5:0.5b", streaming=True)

class ChatBot(QObject):
    # 通过信号通知界面新加token
    update_text = pyqtSignal(str)
    
    def __init__(self) -> None:
        super().__init__()
        return
    
    def connect(self, func_update):
        self.update_text.connect(func_update)
    
    def disconnect(self):
        self.update_text.disconnect()
    
    # 回答内容
    def answer(self, question: str):
        # 发送用户消息
        human_msg = HumanMessage(content=question)
        print([human_msg])
        # 逐步处理 token 并发信号更新 GUI
        full_token = ""
        for chunk in llm.stream([human_msg]):
            token = chunk.content
            full_token += token
            self.update_text.emit(token)
        return full_token

class ChatBotThread(QThread):
    # 增加线程结束信号
    finished = pyqtSignal(str)
    
    def __init__(self, question: str, bot: ChatBot):
        super().__init__()
        self.question = question
        self.bot = bot
    
    def run(self):
        full_content = self.bot.answer(self.question)
        # 完成后发出 finished 信号
        self.finished.emit(full_content)

chatbot = ChatBot()
