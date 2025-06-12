import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QListWidget, QScrollArea, 
                             QTextEdit, QPushButton, QLabel, QFrame, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
from main import ChatBot

chatbot = ChatBot()

class StreamingMessageWidget(QWidget):
    """支持流式输出的消息气泡组件"""
    def __init__(self, message="", is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.full_message = message
        self.current_message = ""
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 创建头像
        avatar = QLabel()
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet("""
            QLabel {
                background-color: %s;
                border-radius: 20px;
                border: 2px solid #ddd;
            }
        """ % ("#4CAF50" if self.is_user else "#2196F3"))
        
        # 添加头像文字
        avatar.setText("U" if self.is_user else "A")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(avatar.styleSheet() + """
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        
        # 创建消息气泡
        message_bubble = QFrame()
        message_bubble.setMaximumWidth(400)
        message_bubble.setStyleSheet("""
            QFrame {
                background-color: %s;
                border-radius: 15px;
                padding: 10px;
                margin: 5px;
            }
        """ % ("#E3F2FD" if self.is_user else "#F5F5F5"))
        
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(10, 10, 10, 10)
        
        self.message_label = QLabel(self.current_message)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #333;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        
        bubble_layout.addWidget(self.message_label)
        message_bubble.setLayout(bubble_layout)
        
        # 布局设置
        if self.is_user:
            layout.addStretch()
            layout.addWidget(message_bubble)
            layout.addWidget(avatar)
        else:
            layout.addWidget(avatar)
            layout.addWidget(message_bubble)
            layout.addStretch()
        
        self.setLayout(layout)
    
    def set_message(self, message):
        """设置消息内容"""
        self.current_message = message
        self.message_label.setText(message)
    
    def append_text(self, text):
        """追加文本（用于流式输出）"""
        self.current_message += text
        self.message_label.setText(self.current_message)


class MessageWidget(QWidget):
    """普通消息气泡组件"""
    def __init__(self, message, is_user=True, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 创建头像
        avatar = QLabel()
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet("""
            QLabel {
                background-color: %s;
                border-radius: 20px;
                border: 2px solid #ddd;
            }
        """ % ("#4CAF50" if self.is_user else "#2196F3"))
        
        # 添加头像文字
        avatar.setText("U" if self.is_user else "A")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setStyleSheet(avatar.styleSheet() + """
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        
        # 创建消息气泡
        message_bubble = QFrame()
        message_bubble.setMaximumWidth(400)
        message_bubble.setStyleSheet("""
            QFrame {
                background-color: %s;
                border-radius: 15px;
                padding: 10px;
                margin: 5px;
            }
        """ % ("#E3F2FD" if self.is_user else "#F5F5F5"))
        
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(10, 10, 10, 10)
        
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #333;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        
        bubble_layout.addWidget(message_label)
        message_bubble.setLayout(bubble_layout)
        
        # 布局设置
        if self.is_user:
            layout.addStretch()
            layout.addWidget(message_bubble)
            layout.addWidget(avatar)
        else:
            layout.addWidget(avatar)
            layout.addWidget(message_bubble)
            layout.addStretch()
        
        self.setLayout(layout)


class ChatInterface2(QMainWindow):
    """主聊天界面"""
    def __init__(self):
        super().__init__()
        self.conversations_dir = "chat_conversations"  # 对话文件夹
        self.current_conversation = []
        self.conversations = []
        self.current_conversation_index = -1  # 当前对话在历史列表中的索引，-1表示新对话
        self.current_conversation_file = None  # 当前对话的文件名
        self.is_ai_responding = False  # AI是否正在回复
        self.streaming_widget = None  # 当前流式输出的消息组件
        self.init_ui()
        self.ensure_conversations_dir()
        self.load_all_conversations()
        self.second_window = None
        
    def init_ui(self):
        self.setWindowTitle("知识问答")
        self.setGeometry(100, 100, 1200, 800)
        
        # 主窗口设置
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧历史会话面板
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # 右侧聊天面板
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # 设置分割器比例
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setSizes([300, 900])
        
        # 主布局
        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        central_widget.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QSplitter::handle {
                background-color: #ddd;
                width: 2px;
            }
        """)
    
    def create_left_panel(self):
        """创建左侧历史会话面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("历史对话")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        
        # 新建对话按钮
        self.new_chat_btn = QPushButton("+ 新建对话")
        self.new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.new_chat_btn.clicked.connect(self.new_conversation)
        
        # 历史对话列表
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
                min-height: 40px;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.history_list.itemClicked.connect(self.load_conversation)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(self.new_chat_btn)
        left_layout.addWidget(self.history_list)
        left_widget.setLayout(left_layout)
        
        return left_widget
    
    def create_right_panel(self):
        """创建右侧聊天面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        # 状态指示器
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        clear_btn = QPushButton("清除聊天记录")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        clear_btn.clicked.connect(self.clear_current_chat)
        
        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        toolbar.addWidget(clear_btn)
        
        # 聊天显示区域
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_widget.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_widget)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(100)
        self.input_text.setPlaceholderText("请输入消息...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #2196F3;
            }
        """)
        
        self.send_btn = QPushButton("发送")
        self.send_btn.setFixedSize(80, 40)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_text)
        input_layout.addWidget(self.send_btn)
        
        right_layout.addLayout(toolbar)
        right_layout.addWidget(self.chat_scroll)
        right_layout.addLayout(input_layout)
        right_widget.setLayout(right_layout)
        
        # 绑定回车键发送
        self.input_text.keyPressEvent = self.input_key_press_event
        
        return right_widget

    
    def input_key_press_event(self, event):
        """处理输入框按键事件"""
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            if not self.is_ai_responding:  # 只有在AI不在回复时才能发送
                self.send_message()
        else:
            QTextEdit.keyPressEvent(self.input_text, event)
    
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
        self.status_label.setText("正在回答...")
        
        # 清空输入框
        self.input_text.clear()
        
        # 添加用户消息
        self.add_message(message, True)
        self.current_conversation.append({"role": "user", "content": message, "timestamp": datetime.now().isoformat()})
        
        # 如果是在已有对话中继续聊天，更新该对话
        if self.current_conversation_index >= 0:
            self.update_existing_conversation()
        
        # 模拟AI流式回复
        QTimer.singleShot(500, lambda: self.start_streaming_response(message))
    
    def start_streaming_response(self, user_message):
        """开始流式回复"""
        # 生成完整的回复内容
        self.full_response = chatbot.run(user_message)
        
        # 创建流式输出的消息组件
        self.streaming_widget = StreamingMessageWidget("", False)
        self.chat_layout.addWidget(self.streaming_widget)
        
        # 开始逐字输出
        self.response_index = 0
        self.streaming_timer = QTimer()
        self.streaming_timer.timeout.connect(self.stream_next_char)
        self.streaming_timer.start(50)  # 每50毫秒输出一个字符
        
        self.scroll_to_bottom()
    
    def stream_next_char(self):
        """输出下一个字符"""
        if self.response_index < len(self.full_response):
            char = self.full_response[self.response_index]
            self.streaming_widget.append_text(char)
            self.response_index += 1
            self.scroll_to_bottom()
        else:
            # 流式输出完成
            self.streaming_timer.stop()
            self.finish_ai_response()
    
    def finish_ai_response(self):
        """完成AI回复"""
        # 恢复发送状态
        self.is_ai_responding = False
        self.send_btn.setEnabled(True)
        self.input_text.setEnabled(True)
        self.status_label.setText("")
        
        # 保存完整回复到对话记录
        self.current_conversation.append({
            "role": "assistant", 
            "content": self.full_response, 
            "timestamp": datetime.now().isoformat()
        })
        
        # 如果是在已有对话中继续聊天，更新该对话
        if self.current_conversation_index >= 0:
            self.update_existing_conversation()
        
        # 重新聚焦到输入框
        self.input_text.setFocus()
    
    def add_message(self, message, is_user):
        """添加消息到聊天区域"""
        message_widget = MessageWidget(message, is_user)
        self.chat_layout.addWidget(message_widget)
        
        # 滚动到底部
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_current_chat(self):
        """清除当前聊天记录"""
        # 清除显示
        for i in reversed(range(self.chat_layout.count())):
            child = self.chat_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 清除当前对话数据
        self.current_conversation = []
        self.current_conversation_index = -1  # 重置为新对话状态
        self.current_conversation_file = None  # 重置文件名
        
        # 重置状态
        self.is_ai_responding = False
        self.send_btn.setEnabled(True)
        self.input_text.setEnabled(True)
        self.status_label.setText("")
        
        # 停止可能正在进行的流式输出
        if hasattr(self, 'streaming_timer') and self.streaming_timer.isActive():
            self.streaming_timer.stop()
    
    def new_conversation(self):
        """新建对话"""
        # 如果AI正在回复，不允许新建对话
        if self.is_ai_responding:
            return
        
        # 只要当前有对话内容，就保存它
        if self.current_conversation:
            if self.current_conversation_index == -1:
                # 当前是新对话且有内容，保存为新的历史记录
                self.save_current_conversation()
                print("保存了当前新对话到历史记录")
            else:
                # 当前是已有对话，更新它
                self.update_existing_conversation()
                print("更新了当前已有对话")
        
        # 清除当前聊天显示和数据
        self.clear_current_chat()
        
        # 取消历史列表的选择，表示现在是全新对话
        self.history_list.clearSelection()
        
        # 聚焦到输入框
        self.input_text.setFocus()
        
        print("开始新对话")
    
    def load_conversation(self, item):
        """加载选中的对话"""
        # 如果AI正在回复，不允许切换对话
        if self.is_ai_responding:
            return
        
        # 在切换之前，先保存当前对话（如果有内容）
        if self.current_conversation:
            if self.current_conversation_index == -1:
                # 当前是新对话且有内容，保存它
                self.save_current_conversation()
                print("切换前保存了当前新对话")
            else:
                # 当前是已有对话，更新它
                self.update_existing_conversation()
                print("切换前更新了当前对话")
        
        # 清除当前显示
        self.clear_current_chat()
        
        # 加载选中的对话
        index = self.history_list.row(item)
        if index < len(self.conversations):
            conversation = self.conversations[index]
            self.current_conversation = conversation["messages"].copy()
            self.current_conversation_index = index  # 记录当前对话索引
            self.current_conversation_file = conversation.get("filename")  # 记录当前文件名
            
            # 显示对话内容
            for msg in self.current_conversation:
                is_user = msg["role"] == "user"
                self.add_message(msg["content"], is_user)
            
            print(f"加载对话: {conversation.get('title', '未知对话')}")
    
    def is_current_conversation_saved(self):
        """检查当前对话是否已保存"""
        if self.current_conversation_index >= 0:
            # 如果是已有对话，检查内容是否有变化
            if self.current_conversation_index < len(self.conversations):
                saved_messages = self.conversations[self.current_conversation_index]["messages"]
                return len(saved_messages) == len(self.current_conversation)
        return False
    
    def ensure_conversations_dir(self):
        """确保对话文件夹存在"""
        if not os.path.exists(self.conversations_dir):
            os.makedirs(self.conversations_dir)
            print(f"创建对话文件夹: {self.conversations_dir}")
    
    def generate_conversation_filename(self):
        """生成对话文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"chat_{timestamp}.json"
    
    def update_existing_conversation(self):
        """更新已有对话"""
        if self.current_conversation_index >= 0 and self.current_conversation_index < len(self.conversations):
            conversation_data = self.conversations[self.current_conversation_index]
            conversation_data["messages"] = self.current_conversation.copy()
            conversation_data["timestamp"] = datetime.now().isoformat()
            
            # 保存到对应的文件
            if self.current_conversation_file:
                filepath = os.path.join(self.conversations_dir, self.current_conversation_file)
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
                    print(f"更新对话文件: {self.current_conversation_file}")
                    
                    # 更新历史列表显示（因为时间戳可能变了）
                    self.update_history_list()
                except Exception as e:
                    print(f"更新对话文件失败: {e}")
    
    def save_current_conversation(self):
        """保存当前对话为新文件"""
        if not self.current_conversation:
            return
        
        # 生成新的文件名
        filename = self.generate_conversation_filename()
        
        # 生成对话标题（使用第一条用户消息的前20个字符）
        title = "新对话"
        for msg in self.current_conversation:
            if msg["role"] == "user":
                title = msg["content"][:20] + ("..." if len(msg["content"]) > 20 else "")
                break
        
        conversation_data = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "filename": filename,
            "messages": self.current_conversation.copy()
        }
        
        # 保存到文件
        filepath = os.path.join(self.conversations_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            print(f"保存新对话文件: {filename}")
            
            # 添加到对话列表的开头（最新的在前面）
            self.conversations.insert(0, conversation_data)
            
            # 更新当前对话索引和文件名
            self.current_conversation_index = 0
            self.current_conversation_file = filename
            
            # 更新历史列表显示
            self.update_history_list()
            
            # 选中新创建的对话（现在在第一位）
            self.history_list.setCurrentRow(0)
            
        except Exception as e:
            print(f"保存对话文件失败: {e}")
    
    def load_all_conversations(self):
        """加载所有对话文件"""
        self.conversations = []
        
        if not os.path.exists(self.conversations_dir):
            return
        
        # 获取所有JSON文件
        json_files = [f for f in os.listdir(self.conversations_dir) if f.endswith('.json')]
        json_files.sort()  # 按文件名排序
        
        for filename in json_files:
            filepath = os.path.join(self.conversations_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    conversation_data = json.load(f)
                    # 确保文件名信息存在
                    conversation_data["filename"] = filename
                    self.conversations.append(conversation_data)
                    print(f"加载对话文件: {filename}")
            except Exception as e:
                print(f"加载对话文件失败 {filename}: {e}")
        
        print(f"总共加载了 {len(self.conversations)} 个对话")
        self.update_history_list()
    
    def load_conversations(self):
        """加载历史对话（保留兼容性）"""
        self.load_all_conversations()
    
    def save_conversations(self):
        """保存对话（已不再使用单一文件，保留兼容性）"""
        pass
    
    def update_history_list(self):
        """更新历史对话列表"""
        current_row = self.history_list.currentRow()  # 保存当前选中行
        self.history_list.clear()
        
        # 按时间戳排序对话（最新的在前）
        sorted_conversations = sorted(self.conversations, key=lambda x: x.get("timestamp", ""), reverse=True)
        self.conversations = sorted_conversations  # 更新排序后的列表
        
        # 如果当前对话索引有效，需要重新计算索引
        if self.current_conversation_index >= 0:
            # 根据文件名找到新的索引位置
            for i, conv in enumerate(self.conversations):
                if conv.get("filename") == self.current_conversation_file:
                    self.current_conversation_index = i
                    break
        
        for i, conv in enumerate(self.conversations):
            # 显示对话标题和最后更新时间
            timestamp = datetime.fromisoformat(conv["timestamp"]).strftime("%m-%d %H:%M")
            display_text = f"{conv['title']}\n{timestamp}"
            
            item = QListWidgetItem(display_text)
            filename = conv.get("filename", "未知文件")
            item.setToolTip(f"文件名: {filename}\n创建时间: {timestamp}\n消息数: {len(conv['messages'])}")
            self.history_list.addItem(item)
        
        # 如果之前有选中的对话，恢复选中状态
        if self.current_conversation_index >= 0 and self.current_conversation_index < self.history_list.count():
            self.history_list.setCurrentRow(self.current_conversation_index)
    
    def closeEvent(self, event):
        """程序关闭时保存当前对话"""
        try:
            # 停止可能正在进行的流式输出
            if hasattr(self, 'streaming_timer') and self.streaming_timer.isActive():
                self.streaming_timer.stop()
            
            if self.current_conversation:
                if self.current_conversation_index == -1:
                    # 新对话，保存为新的历史记录
                    self.save_current_conversation()
                else:
                    # 已有对话，更新现有记录
                    self.update_existing_conversation()
            
            print("对话已自动保存")
        except Exception as e:
            print(f"保存对话时出错: {e}")
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    window = ChatInterface()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()