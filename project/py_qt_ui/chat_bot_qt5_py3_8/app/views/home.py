# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon
from ..common.config import cfg, HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.icon import Icon, FluentIconBase
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QScrollArea, QFrame, 
                            QLabel, QLineEdit, QSizePolicy)
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

from ..common.style_sheet import StyleSheet
from ..chatbot import chatbot, ChatBotThread
from ..components.message_widget import MessageWidget 

class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.bot = chatbot
        self.bot.connect(self.update_bot_message)
        self.current_bot_message = None
        self.chat_thread = None
        self.init_ui()
        
        self.__initWidget()
        

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    
    def init_ui(self):
        self.setWindowTitle("AI 聊天机器人")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # # 创建标题栏
        # title_frame = QFrame()
        # title_frame.setStyleSheet("""
        #     QFrame {
        #         background-color: #f8f9fa;
        #         border-bottom: 1px solid #dee2e6;
        #     }
        # """)
        # title_layout = QHBoxLayout(title_frame)
        # title_layout.setContentsMargins(20, 15, 20, 15)
        
        # title_label = QLabel("AI 聊天助手")
        # title_label.setFont(QFont("Arial", 16, QFont.Bold))
        # title_label.setStyleSheet("color: #333;")
        # title_layout.addWidget(title_label)
        
        # main_layout.addWidget(title_frame)
        
        # 创建聊天区域
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.chat_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f1f1f1;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a1a1a1;
            }
        """)
        
        # 聊天内容容器
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setContentsMargins(0, 10, 0, 10)
        self.chat_layout.setSpacing(2)  # 减少消息间距
        self.chat_layout.addStretch()
        
        self.chat_area.setWidget(self.chat_widget)
        main_layout.addWidget(self.chat_area)
        
        # 创建输入区域
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 15, 20, 15)
        input_layout.setSpacing(10)
        
        # 输入框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入您的问题...")
        self.input_field.setFont(QFont("Arial", 11))
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #dee2e6;
                border-radius: 25px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        main_layout.addWidget(input_frame)
        
        # 添加欢迎消息
        self.add_bot_message("你好！我是AI助手，有什么可以帮助您的吗？")
    
    def add_user_message(self, message):
        """添加用户消息"""
        message_widget = MessageWidget(message, is_user=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
        self.scroll_to_bottom()
        message_widget.adjust_message_width_by_content()
    
    def add_bot_message(self, message):
        """添加机器人消息"""
        message_widget = MessageWidget(message, is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
        self.current_bot_message = message_widget
        self.scroll_to_bottom()
    
    def update_bot_message(self, token):
        """更新当前机器人消息"""
        if self.current_bot_message:
            current_text = self.current_bot_message.message_text
            new_text = current_text + token
            self.current_bot_message.update_message(new_text)
            self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        QTimer.singleShot(10, lambda: self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()))
    
    def send_message(self):
        """发送消息"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        # 添加用户消息
        self.add_user_message(message)
        self.input_field.clear()
        
        # 禁用发送按钮和输入框
        self.send_button.setEnabled(False)
        self.input_field.setEnabled(False)
        
        # 添加空的机器人消息
        self.add_bot_message("")
        
        # 创建并启动聊天线程
        self.chat_thread = ChatBotThread(message, self.bot)
        self.chat_thread.finished.connect(self.on_chat_finished)
        self.chat_thread.start()
    
    def on_chat_finished(self, full_content):
        """聊天完成回调"""
        # 重新启用发送按钮和输入框
        self.send_button.setEnabled(True)
        self.input_field.setEnabled(True)
        self.input_field.setFocus()
        
        # 清理线程
        if self.chat_thread:
            self.chat_thread.quit()
            self.chat_thread.wait()
            self.chat_thread = None
        
        self.current_bot_message = None
    
    def closeEvent(self, event):
        """关闭窗口时的清理"""
        if self.chat_thread and self.chat_thread.isRunning():
            self.chat_thread.quit()
            self.chat_thread.wait()
        event.accept()
