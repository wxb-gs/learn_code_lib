import json
import os
import pprint
import random
import re
import sys
from datetime import datetime
import mistune
import uuid
import sys
import threading
import time
# import markdown
# 后端代码
from chatbot import ChatBot, ChatBotThread
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QPainter, QPixmap,
                         QTextCursor)
from PyQt5.QtWidgets import QMessageBox  # 如果还没有导入的话
from PyQt5.QtWidgets import (QAction, QApplication, QFrame,  # 你现有的导入
                             QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QMainWindow, QMenu, QPushButton, QScrollArea,
                             QSizePolicy, QSplitter, QTextEdit, QVBoxLayout,
                             QWidget, QDialog)
import speech_recognition as sr
import pyaudio

from styles.btn_qss import blue_btn_qss, simple_btn_qss, blue_btn_with_disable_style
from styles.history_list_qss import history_list_styles
from styles.left_panel_qss import left_panel_style
from components.search_dialog import SearchDialog
from components.params_dialog import ConversationEditDialog
from db.database import ConversationDatabase
from components.streaming_message_widget import StreamingMessageWidget
from components.record_audio import VoiceRecorder, AnimatedRecordButton

chatbot = ChatBot()
db = ConversationDatabase()

MAX_HEIGHT = 650
MIN_HEIGHT = 28

USER_MAX_WIDTH = 300
AI_MAX_WIDTH = 680


class ChatInterface(QMainWindow):
    """主聊天界面"""

    def __init__(self):
        super().__init__()
        # self.conversations_dir = "chat_conversations"  # 对话文件夹
        self.current_conversation = []
        self.conversations = []  # 包含已保存和未保存的会话
        self.current_conversation_index = -1  # 当前对话在历史列表中的索引，-1表示新对话
        self.current_conversation_file = None  # 当前对话的文件名
        self.is_ai_responding = False  # AI是否正在回复
        self.streaming_widget = None  # 当前流式输出的消息组件
        self.db = db
        self.init_ui()
        self.load_all_conversations()
        # 录音组件加载
        self.voice_recorder = VoiceRecorder()
        self.setup_voice_signals()
        
        # 启动时自动创建新会话
        if len(self.conversations) <= 0:
            self.create_initial_session()
        else:
            self.load_conversation(index=0)
            self.update_history_list()
        count = self.chat_layout.count()
        if count == 0:
            self.show_empty_chat_hint()

        self.second_window = None
        self.source = None
    
    # ==============================================main windows ========================================
    def show_empty_chat_hint(self):
        """显示空聊天提示"""
        if not hasattr(self, 'empty_chat_label'):
            # 创建默认提示标签
            self.empty_chat_label = QLabel("请开始聊天吧")
            self.empty_chat_label.setAlignment(Qt.AlignCenter)
            self.empty_chat_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                    color: #9aa0a6;
                    background-color: transparent;
                    padding: 40px;
                    border: none;
                }
                """)
            # 添加到布局的开头
            self.chat_layout.insertWidget(0, self.empty_chat_label)
        else:
            self.empty_chat_label.show()
    
    def hide_empty_chat_hint(self):
        """隐藏空聊天提示"""
        if hasattr(self, 'empty_chat_label'):
            self.empty_chat_label.hide()

    def setup_voice_signals(self):
        """设置语音识别信号连接"""
        self.voice_recorder.text_recognized.connect(self.append_voice_text)
        self.voice_recorder.recording_started.connect(self.on_recording_started)
        self.voice_recorder.recording_stopped.connect(self.on_recording_stopped)
        self.voice_recorder.error_occurred.connect(self.on_voice_error)

    def init_ui(self):
        self.setWindowTitle("智能助手")
        self.setGeometry(100, 100, 1400, 900)
        self. pre_hot()
        # 主窗口设置
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # # 创建主标题 - 更加简洁的设计
        # main_title = QLabel("智能助手")
        # main_title.setAlignment(Qt.AlignCenter)
        # main_title.setFixedHeight(60)
        # main_title.setStyleSheet("""
        #     QLabel {
        #         font-size: 18px;
        #         font-weight: 600;
        #         font-family: "Microsoft YaHei UI", "PingFang SC", "SF Pro Display", sans-serif;
        #         padding: 15px;
        #         background-color: #ffffff;
        #         color: #1a73e8;
        #         border: none;
        #         border-bottom: 1px solid #e8eaed;
        #         margin: 0px;
        #         text-align: center;
        #         letter-spacing: 0.5px;
        #     }
        #     """)

        # 创建内容分割器（左右布局）
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(1)

        # 左侧历史会话面板
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)

        # 右侧聊天面板
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)

        # 设置分割器比例
        content_splitter.setStretchFactor(0, 0)
        content_splitter.setStretchFactor(1, 1)
        content_splitter.setSizes([320, 1080])
        content_splitter.setCollapsible(0, False)
        content_splitter.setCollapsible(1, False)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.addWidget(main_title)
        main_layout.addWidget(content_splitter, 1)
        central_widget.setLayout(main_layout)

        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
                font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
            }
            QSplitter::handle {
                background-color: #e8eaed;
                width: 1px;
                border: none;
            }
            QSplitter::handle:hover {
                background-color: #dadce0;
            }
        """)

    def pre_hot(self):
        # self.thread1 = ChatBotThread("你好1", chatbot)
        # self.thread2 = ChatBotThread("你好2", chatbot)
        # self.thread3 = ChatBotThread("你好3", chatbot)
        # self.thread1.start()
        # self.thread2.start()
        # self.thread3.start()
        return
    
    # ===================================left panel=============================================
    def create_left_panel(self):
        """创建左侧历史会话面板"""
        left_widget = QWidget()
        left_widget.setMinimumWidth(320)
        left_widget.setMaximumWidth(380)

        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # 顶部操作区域
        top_section = QWidget()
        top_section.setFixedHeight(70)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)
        top_layout.setContentsMargins(16, 16, 16, 16)
        
        # 新建对话按钮
        self.new_chat_btn = QPushButton("新建对话")
        self.new_chat_btn.setFixedHeight(36)
        self.new_chat_btn.setIcon(QIcon("./icon/new_chat.png"))  # 设置图标
        self.new_chat_btn.setIconSize(QSize(16, 16))  # 设置图标大小
        self.new_chat_btn.setStyleSheet(blue_btn_qss)
        self.new_chat_btn.clicked.connect(self.new_conversation)

        # 搜索按钮
        self.search_btn = QPushButton("搜索对话")
        self.search_btn.setFixedHeight(36)
        self.search_btn.setIcon(QIcon("./icon/search.png"))  # 设置图标
        self.search_btn.setIconSize(QSize(16, 16))  # 设置图标大小
        self.search_btn.setStyleSheet(simple_btn_qss)
        self.search_btn.clicked.connect(self.open_search_dialog)

        top_layout.addWidget(self.new_chat_btn)
        top_layout.addWidget(self.search_btn)
        top_layout.addStretch()
        # top_layout.addWidget(self.delete_all_btn)
        top_section.setLayout(top_layout)

        # 历史对话列表
        self.history_list = QListWidget()
        self.history_list.setStyleSheet(history_list_styles)
        self.history_list.itemClicked.connect(self.load_conversation)

        # 设置右键菜单
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(
            self.show_context_menu)

        # 组装左侧面板
        left_layout.addWidget(top_section)
        left_layout.addWidget(self.history_list, 1)

        left_widget.setLayout(left_layout)

        # 左侧面板整体样式
        left_widget.setStyleSheet(left_panel_style)

        return left_widget

    # ******************************************** 搜索界面 ********************************************
    def open_search_dialog(self):
        """打开搜索对话框"""
        dialog = SearchDialog(self.conversations, self)
        dialog.conversation_selected.connect(self.on_conversation_selected)
        dialog.exec_()

    def on_conversation_selected(self, conversation_data):
        """处理会话选择"""
        print(f"选中会话: {conversation_data['name']}")
        print(f"创建时间: {conversation_data['create_time']}")
        print(f"最近使用: {conversation_data['last_used_time']}")
        print(f"唤醒词: {conversation_data['wake_words']}")
        print(f"智能模式: {'开启' if conversation_data['smart_mode'] else '关闭'}")
        print("-" * 40)
        id = conversation_data['id']
        index = 0
        for i, conv in enumerate(self.conversations):
            if conv['id'] == id:
                index = i
                break
        self.load_conversation(index = index)
        self.update_history_list()

    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.history_list.itemAt(position)
        if item is None:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e3f2fd;
                border-radius: 8px;
                padding: 6px;
                font-family: "Microsoft YaHei UI", "PingFang SC", "SF Pro Display", sans-serif;
                min-width: 140px;
            }
            
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
                color: #424242;
                margin: 1px 2px;
                background-color: transparent;
                border: none;
            }
            
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: #e8e8e8;
                margin: 4px 8px;
            }
        """)

        # # 保存会话选项
        # save_action = QAction("💾 保存会话", self)
        # save_action.triggered.connect(
        #     lambda: self.save_session_from_menu(item))
        # menu.addAction(save_action)

        # # 添加分隔符
        # menu.addSeparator()

        # 编辑会话选项
        edit_action = QAction("✏️ 编辑会话", self)
        edit_action.triggered.connect(lambda: self.open_edit_dialog(item))
        menu.addAction(edit_action)

        # 添加分隔符
        menu.addSeparator()

        # 删除会话选项
        delete_action = QAction("🗑️ 删除会话", self)
        delete_action.triggered.connect(
            lambda: self.delete_session_from_menu(item))
        menu.addAction(delete_action)

        # 显示菜单
        menu.exec_(self.history_list.mapToGlobal(position))

    # ************************************* 弹出编辑界面 **************************
    def open_edit_dialog(self, item):
        conversations = self.conversations
        """打开搜索对话框"""
        index = self.history_list.row(item)
        dialog = ConversationEditDialog(conversations[index], self)
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            params = dialog.get_parameters()
            print("======================================")
            print(params)

            print("用户修改后的参数:")
            for key, value in params.items():
                print(f"  {key}: {value}")

            conversations[index]["name"] = params["name"]
            conversations[index]["smart_mode"] = params["smart_mode"]
            conversations[index]["wake_words"] = params["wake_words"]
            conversations[index]["time_threshold"] = params["time_threshold"]
            # 写入
            self.db.update_conversation_settings(
                conversation_id=conversations[index]['id'],
                name=params['name'],
                wake_words=params['wake_words'],
                smart_mode=params['smart_mode'],
                time_threshold=params['time_threshold']
            )
            self.update_history_list()
        else:
            print("用户取消了操作")

        return
    
    # ***************************************** 会话管理  *********************************
    def delete_all_conversations(self):
        """删除所有对话"""

        if not self.conversations:
            return

        # 确认对话框
        reply = QMessageBox.question(
            self,
            '确认删除',
            f'确定要删除所有 {len(self.conversations)} 个对话吗？\n此操作不可恢复！',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # 删除所有保存的文件
                db.clear_all_conversations()

                # 清空对话列表
                self.conversations.clear()

                # 重置当前对话状态
                self.current_conversation = []
                self.current_conversation_index = -1
                self.current_conversation_file = None

                # 清除界面显示
                self.clear_current_chat()

                # 更新历史列表
                self.update_history_list()

                # 创建新的空会话
                self.create_initial_session()

                # 显示成功消息
                QMessageBox.information(
                    self,
                    '删除完成',
                    f'成功删除所有历史记录！'
                )

            except Exception as e:
                print(f"删除所有对话失败: {e}")
                QMessageBox.critical(
                    self,
                    '删除失败',
                    f'删除过程中出现错误：{str(e)}'
                )
    
    def save_session_from_menu(self, item):
        """从右键菜单保存会话"""
        index = self.history_list.row(item)
        if index < len(self.conversations):
            conversation = self.conversations[index]
            
            # 更新消息记录
            conversation['messages'] = self.current_conversation.copy() if self.current_conversation_index == index else conversation.get('messages', [])
            
            # 保存到数据库
            if self.db.save_conversation(conversation):
                # 更新内存中的数据
                conversation['modified'] = False
                print(f"保存会话: {conversation.get('name', '未知对话')}")
                
                # 更新历史列表显示
                self.update_history_list()
            else:
                print(f"保存会话失败: {conversation.get('name', '未知对话')}")

    def delete_session_from_menu(self, item):
        """从右键菜单删除会话"""
        index = self.history_list.row(item)
        if index < len(self.conversations):
            conversation = self.conversations[index]
            conversation_id = conversation['id']
            
            # 如果当前选中的是要删除的会话，需要处理
            if self.current_conversation_index == index:
                self.clear_current_chat()
                self.current_conversation_index = -1
                self.current_conversation_id = None
            elif self.current_conversation_index > index:
                # 如果当前会话在被删除会话之后，需要调整索引
                self.current_conversation_index -= 1
            
            # 从数据库删除
            if self.db.delete_conversation(conversation_id):
                # 从内存列表中移除
                self.conversations.pop(index)
                self.update_history_list()
                print(f"删除会话: {conversation.get('name', '未知对话')}")
            else:
                print(f"删除会话失败: {conversation.get('name', '未知对话')}")

    def create_initial_session(self):
        """创建初始会话"""
        new_conversation = self.db.create_new_conversation()
        if new_conversation:
            # 添加到会话列表的开头
            self.conversations.insert(0, new_conversation)
            self.current_conversation_index = 0
            self.current_conversation = []
            self.current_conversation_id = new_conversation['id']
            
            # 更新历史列表显示
            self.update_history_list()
            
            # 选中新创建的会话
            if self.history_list.count() > 0:
                self.history_list.setCurrentRow(0)
            
            print("创建初始会话成功")
        else:
            print("创建初始会话失败")

    def clear_current_chat(self):
        """清除当前聊天记录显示（仅清除界面，不删除保存的对话内容）"""
        # 清除界面显示
        for i in reversed(range(self.chat_layout.count())):
            child = self.chat_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 重置UI状态
        self.is_ai_responding = False
        self.send_btn.setEnabled(True)
        self.input_text.setEnabled(True)
        self.status_label.setText("")
        
        # 停止可能正在进行的流式输出
        if hasattr(self, 'streaming_timer') and self.streaming_timer.isActive():
            self.streaming_timer.stop()
        
        print("清除界面显示（对话内容仍保留）")

    def save_current_conversation_state(self):
        """保存当前对话状态到数据库"""
        if (self.current_conversation_index >= 0 and 
            self.current_conversation_index < len(self.conversations) and
            self.current_conversation_id):
            
            # 更新当前会话的消息记录
            conversation = self.conversations[self.current_conversation_index]
            conversation["messages"] = self.current_conversation.copy()
            
            # 检查是否有新消息添加
            original_count = len(conversation.get("original_messages", []))
            current_count = len(self.current_conversation)
            
            if current_count > original_count:
                conversation["modified"] = True
                # 更新数据库中的消息记录
                self.db.update_conversation_messages(
                    self.current_conversation_id, 
                    self.current_conversation
                )
            else:
                # 只更新最后使用时间
                self.db.update_last_used_time(self.current_conversation_id)
            
            # 更新内存中的最后使用时间
            conversation["last_used_time"] = datetime.now().timestamp()
            
            print(f"保存当前对话状态，消息数: {len(self.current_conversation)}")

    def new_conversation(self):
        """新建对话"""
        # 如果AI正在回复，不允许新建对话
        if self.is_ai_responding:
            return
        
        # 保存当前对话状态
        self.save_current_conversation_state()
        
        # 清除当前聊天显示
        self.clear_current_chat()
        
        # 创建新会话
        new_conversation = self.db.create_new_conversation()
        if new_conversation:
            # 添加到会话列表的开头
            self.conversations.insert(0, new_conversation)
            self.current_conversation_index = 0
            self.current_conversation = []
            self.current_conversation_id = new_conversation['id']
            
            # 更新历史列表显示
            self.update_history_list()
            
            # 选中新创建的会话
            self.history_list.setCurrentRow(0)
            
            # 聚焦到输入框
            self.input_text.setFocus()
            
            print("开始新对话")
        else:
            print("创建新对话失败")

    def load_conversation(self, item = None, index = None):
        """加载选中的对话"""
        # 如果AI正在回复，不允许切换对话
        if self.is_ai_responding:
            return
        
        # 保存当前对话状态
        self.save_current_conversation_state()
        
        # 清除当前显示
        self.clear_current_chat()
        
        if index == None:
            # 加载选中的对话
            index = self.history_list.row(item)

        # 设置当前index
        self.current_conversation_index = index

        print(f"切换到对话索引: {index}")
        if index < len(self.conversations):
            conversation = self.conversations[index]
            self.current_conversation = conversation["messages"].copy()
            self.current_conversation_index = index
            self.current_conversation_id = conversation['id']
            
            # 更新数据库中的最后使用时间
            self.db.update_last_used_time(conversation['id'])
            
            # 更新内存中的最后使用时间
            conversation["last_used_time"] = datetime.now().timestamp()
            
            # 记录原始消息数量，用于判断是否有新消息添加
            conversation["original_messages"] = conversation["messages"].copy()
            
            # 显示对话内容
            for msg in self.current_conversation:
                is_user = msg["role"] == "user"
                
                # 如果是AI回复且有source，将source合并到内容中
                if not is_user and msg.get("source"):
                    display_content = msg["content"] + \
                        f"\n\n参考文献：{msg['source']}"
                else:
                    display_content = msg["content"]
                
                self.add_message(display_content, is_user)
            
            print(
                f"加载对话: {conversation.get('name', '未知对话')}, 消息数: {len(self.current_conversation)}")

            # if self.chat_layout.count() == 0:
            #     self.show_empty_chat_hint()
            # else:
            #     self.hide_empty_chat_hint()

    def load_all_conversations(self):
        saved_conversations =  self.db.load_all_conversations()

        # 保存已加载的对话
        self.conversations = saved_conversations
        print(f"总共加载了 {len(self.conversations)} 个已保存的对话")
        self.update_history_list()

    #========================================update history list===========================================
    def update_history_list(self):
        """更新历史对话列表"""
        self.history_list.clear()

        for i, conv in enumerate(self.conversations):
            # 显示对话名称
            display_text = conv['name']

            # # # 如果有修改标记，在名称后添加标识
            # if conv.get("modified", False):
            #     display_text += " *"

            item = QListWidgetItem(display_text)

            # 设置工具提示
            id = conv.get("id","xxxx")
            # if conv.get("modified", False):
            #     save_status += " (已修改)"
            filename = conv.get("name", "无文件")

            # 时间戳转换为可读格式
            create_time_str = datetime.fromtimestamp(
                conv.get("create_time", 0)).strftime("%Y-%m-%d %H:%M")
            last_used_time_str = datetime.fromtimestamp(
                conv.get("last_used_time", 0)).strftime("%Y-%m-%d %H:%M")

            wake_words_str = ', '.join(conv.get("wake_words", []))
            smart_mode_str = "是" if conv.get("smart_mode", False) else "否"

            time_threshold = conv.get("time_threshold",1.0)
            tooltip_text = f"会话id: {id}\n文件名: {filename}\n 时间阈值：{time_threshold} \n创建时间: {create_time_str}\n最后使用: {last_used_time_str}\n消息数: {len(conv['messages'])}\n唤醒词: {wake_words_str}\n智能模式: {smart_mode_str}"

            item.setToolTip(tooltip_text)

            # # 为未保存的会话设置不同的样式
            # if conv.get("modified", False):
            #     item.setForeground(QColor("#ff6600"))  # 橙色字体表示已修改

            self.history_list.addItem(item)

        # 如果之前有选中的对话，恢复选中状态
        if self.current_conversation_index >= 0 and self.current_conversation_index < self.history_list.count():
            self.history_list.setCurrentRow(self.current_conversation_index)

    # ===================================right all logic=============================================
    def create_right_panel(self):
        """创建右侧聊天面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 顶部工具栏
        toolbar_widget = QWidget()
        toolbar_widget.setFixedHeight(70)
        # toolbar_widget.setStyleSheet("""
        #     QWidget {
        #         background-color: #F3F5F6;
        #         border-top: 1px solid #e8eaed;
        #         border-bottom: 1px solid #e8eaed;
        #     }
        # """)
        toolbar_widget.setFixedHeight(60)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        toolbar.setContentsMargins(16, 16, 16, 16)
        # toolbar.setSpacing(12)
        # toolbar.setContentsMargins(20, 12, 20, 12)

        # 状态指示器
        self.status_label = QLabel("")
        # self.status_label.setStyleSheet("""
        #     QLabel {
        #         font-size: 13px;
        #         font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
        #         padding: 6px 12px;
        #         border-radius: 12px;
        #         color: #3f6368;
        #         background-color: #f8f9fa;
        #         min-width:100px;
        #     }
        #     """)

        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        toolbar_widget.setLayout(toolbar)

        # 聊天显示区域
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
                margin: 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #dadce0;
                border-radius: 3px;
                min-height: 20px;
                border: none;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #bdc1c6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            """)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(16)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_widget.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_widget)

        # 美化的输入区域
        input_container = QWidget()
        input_container.setFixedHeight(120)
        input_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafafa, stop:1 #ffffff);
                border-top: 1px solid #e8eaed;
                border-bottom: 1px solid #f0f0f0;
            }
            """)

        # 主输入布局
        main_input_layout = QVBoxLayout()
        main_input_layout.setContentsMargins(24, 16, 24, 16)
        main_input_layout.addStretch()
        
        # 输入控件的水平布局
        input_layout = QHBoxLayout()
        input_layout.setSpacing(16)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # 输入框容器
        input_wrapper = QWidget()
        input_wrapper.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e8eaed;
                border-radius: 26px;
            }
            QWidget:hover {
                border-color: #dadce0;
            }
            """)
        
        input_wrapper_layout = QHBoxLayout()
        input_wrapper_layout.setContentsMargins(16, 4, 16, 4)
        input_wrapper_layout.setSpacing(0)

        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(52)
        self.input_text.setMinimumHeight(52)
        self.input_text.setPlaceholderText("💬 输入您的消息...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 12px 4px;
                font-size: 14px;
                font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
                background-color: transparent;
                color: #3c4043;
                line-height: 1.5;
                selection-background-color: #1a73e8;
                selection-color: white;
            }
            QTextEdit:focus {
                background-color: transparent;
                outline: none;
            }
            """)

        input_wrapper_layout.addWidget(self.input_text)
        input_wrapper.setLayout(input_wrapper_layout)
 

        # 使用新的动画录音按钮
        self.record_btn = AnimatedRecordButton()
        self.record_btn.clicked.connect(self.toggle_recording)

        # 发送按钮
        self.send_btn = QPushButton("")
        self.send_btn.setFixedSize(52, 52)
        self.send_btn.setIcon(QIcon("./icon/send.png"))
        self.send_btn.setIconSize(QSize(24, 24))
        self.send_btn.setStyleSheet(blue_btn_with_disable_style)
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setToolTip("发送文本消息")

        # 清除记录按钮
        clear_btn = QPushButton("")
        clear_btn.setFixedSize(52, 52)
        clear_btn.setIcon(QIcon("./icon/del1.png"))
        clear_btn.setIconSize(QSize(22, 22))
        clear_btn.setToolTip("清除聊天记录")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #5f6368;
                border: 1px solid #e8eaed;
                border-radius: 26px;
                font-size: 14px;
                font-weight: 500;
                font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border: 1px solid #dadce0;
                color: #d93025;
            }
            QPushButton:pressed {
                background-color: #f1f3f4;
            }
            """)
        clear_btn.clicked.connect(self.clear_current_chat)

        # 添加控件到布局
        input_layout.addWidget(input_wrapper, 1)
        input_layout.addWidget(self.record_btn)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(clear_btn)

        main_input_layout.addLayout(input_layout)
        main_input_layout.addStretch()
        input_container.setLayout(main_input_layout)

        # 组装右侧面板
        right_layout.addWidget(toolbar_widget)
        right_layout.addWidget(self.chat_scroll, 1)
        right_layout.addWidget(input_container)
        right_widget.setLayout(right_layout)

        # 绑定回车键发送
        self.input_text.keyPressEvent = self.input_key_press_event

        # 右侧面板整体样式
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            """)

        return right_widget

    def toggle_recording(self):
        """切换录音状态"""
        if not self.voice_recorder.is_recording:
            self.voice_recorder.start_recording()
        else:
            self.voice_recorder.stop_recording()

    def on_recording_started(self):
        """录音开始回调"""
        self.record_btn.start_recording_animation()
        self.status_label.setText("🎙️ 正在录音...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                padding: 6px 12px;
                border-radius: 12px;
                color: #ea4335;
                background-color: #fef7f7;
                border: 1px solid #fce8e6;
            }
            """)

    def on_recording_stopped(self):
        """录音停止回调"""
        self.record_btn.stop_recording_animation()
        self.status_label.setText("")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                padding: 6px 12px;
                border-radius: 12px;
                color: #5f6368;
                background-color: #f8f9fa;
            }
            """)

    def on_voice_error(self, error_msg):
        """语音错误回调"""
        print(f"语音错误: {error_msg}")
        self.status_label.setText("❌ 语音识别出错")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                padding: 6px 12px;
                border-radius: 12px;
                color: #d93025;
                background-color: #fce8e6;
                border: 1px solid #fce8e6;
            }
            """)

    def append_voice_text(self, text):
        """将识别的文本追加到输入框"""
        current_text = self.input_text.toPlainText()
        if current_text and not current_text.endswith(' '):
            new_text = current_text + " " + text
        else:
            new_text = current_text + text
            
        self.input_text.setPlainText(new_text)
        
        # 将光标移到最后
        cursor = self.input_text.textCursor()
        cursor.movePosition(cursor.End)
        self.input_text.setTextCursor(cursor)

    def input_key_press_event(self, event):
        """处理输入框按键事件"""
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            if not self.is_ai_responding:
                self.send_message()
        else:
            QTextEdit.keyPressEvent(self.input_text, event)

    # ===================================send message all logic=============================================
    # 发送消息，触发对话
    def send_message(self):
        """发送消息"""
        if self.is_ai_responding:  # 如果AI正在回复，禁止发送
            return

        message = self.input_text.toPlainText().strip()
        if not message:
            return

        # 设置发送状态
        self.is_ai_responding = True
        self.send_btn.setEnabled(False)
        self.input_text.setEnabled(False)
        self.status_label.setText("🤖 AI正在思考中...")

        # 清空输入框
        self.input_text.clear()

        # 添加用户消息
        self.add_message(message, True)
        # 添加用户消息（在现有的添加用户消息部分）
        self.current_conversation.append({
            "role": "user",
            "content": message,
            "source": None,  # 用户消息没有source
            "timestamp": datetime.now().isoformat()
        })

        # 更新当前会话的消息记录
        if self.current_conversation_index >= 0:
            self.conversations[self.current_conversation_index]["messages"] = self.current_conversation.copy()
            self.conversations[self.current_conversation_index]["modified"] = True

        # 模拟AI流式回复
        QTimer.singleShot(500, lambda: self.start_response(message))

    def start_response(self, usr_message: str):
        print("====================开始流式输出===================")
        streaming_widget = StreamingMessageWidget("", False)
        self.chat_layout.addWidget(streaming_widget)

        # 线程结束后emit
        def finished(token):
            print("==================finished===========================")
            self.full_response = token
            # 断开与chatbot的连接关系
            chatbot.disconnect()
            self.finish_ai_response()
            streaming_widget.message_edit.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 开辟一个线程运行对话链
        print("==================start-tread-use-langchain===========================")

        def process_chunk(chunk):
            streaming_widget.append_text(chunk)
            self.scroll_to_bottom()
        chatbot.connect(process_chunk)
        self.bot_thread = ChatBotThread(usr_message, chatbot)
        self.bot_thread.finished.connect(finished)
        self.bot_thread.start()
        streaming_widget.message_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 根据需要显示垂直滚动条

    def finish_ai_response(self):
        """完成AI回复"""
        # 恢复发送状态
        self.is_ai_responding = False
        self.send_btn.setEnabled(True)
        self.input_text.setEnabled(True)
        self.status_label.setText("")

        #保存完整回复到对话记录（包含source）
        self.current_conversation.append({
            "role": "assistant",
            "content": self.full_response,  # 原始内容
        })

        # 更新当前会话的消息记录
        if self.current_conversation_index >= 0:
            self.conversations[self.current_conversation_index]["messages"] = self.current_conversation.copy()
            # 标记为已修改（如果是已保存的对话，需要重新保存）
            self.conversations[self.current_conversation_index]["modified"] = True
            self.save_current_conversation_state()

        # 重新聚焦到输入框
        self.input_text.setFocus()

    # 添加到聊天区域
    def add_message(self, message, is_user):
        """添加消息到聊天区域"""
        message_widget = StreamingMessageWidget(message, is_user)
        self.chat_layout.addWidget(message_widget)

        # 滚动到底部
        QTimer.singleShot(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    window = ChatInterface()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()