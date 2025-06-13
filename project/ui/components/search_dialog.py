import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QScrollArea, 
                             QWidget, QLabel, QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from datetime import datetime
import re


class ConversationItem(QFrame):
    """会话项目组件"""
    clicked = pyqtSignal(dict)
    
    def __init__(self, conversation_data):
        super().__init__()
        self.conversation_data = conversation_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            ConversationItem {
                background-color: #ffffff;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
            }
            ConversationItem:hover {
                background-color: #f8f9fa;
                border-color: #d0d7de;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)
        
        # 会话名称
        name_label = QLabel(self.conversation_data['name'])
        name_label.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        name_label.setStyleSheet("color: #1f2328; margin-bottom: 2px;")
        layout.addWidget(name_label)
        
        # 时间信息
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(15)
        
        create_time_str = datetime.fromtimestamp(self.conversation_data['create_time']).strftime("%Y-%m-%d %H:%M:%S")
        create_time = QLabel(f"创建: {create_time_str}")
        create_time.setFont(QFont("Microsoft YaHei", 9))
        create_time.setStyleSheet("color: #656d76;")
        
        last_time_str = datetime.fromtimestamp(self.conversation_data['last_used_time']).strftime("%Y-%m-%d %H:%M:%S")
        last_time = QLabel(f"最近: {last_time_str}")
        last_time.setFont(QFont("Microsoft YaHei", 9))
        last_time.setStyleSheet("color: #656d76;")
        
        time_layout.addWidget(create_time)
        time_layout.addWidget(last_time)
        time_layout.addStretch()
        
        layout.addLayout(time_layout)
        
        # 唤醒词和智能模式
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)
        
        # 唤醒词
        if self.conversation_data['wake_words']:
            wake_words_text = ", ".join(self.conversation_data['wake_words'][:3])
            if len(self.conversation_data['wake_words']) > 3:
                wake_words_text += "..."
            wake_label = QLabel(f"唤醒词: {wake_words_text}")
        else:
            wake_label = QLabel("唤醒词: 无")
        wake_label.setFont(QFont("Microsoft YaHei", 9))
        wake_label.setStyleSheet("color: #656d76;")
        
        # 智能模式状态
        smart_status = "开启" if self.conversation_data['smart_mode'] else "关闭"
        smart_color = "#0969da" if self.conversation_data['smart_mode'] else "#cf222e"
        smart_label = QLabel(f"Agent模式: {smart_status}")
        smart_label.setFont(QFont("Microsoft YaHei", 9))
        smart_label.setStyleSheet(f"color: {smart_color}; font-weight: 500;")
        
        info_layout.addWidget(wake_label)
        info_layout.addWidget(smart_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        self.setCursor(Qt.PointingHandCursor)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.conversation_data)
        super().mousePressEvent(event)


class SearchDialog(QDialog):
    """ChatGPT风格的搜索对话框"""
    conversation_selected = pyqtSignal(dict)
    
    def __init__(self, conversations, parent=None):
        super().__init__(parent)
        self.conversations = conversations
        self.filtered_conversations = conversations.copy()
        self.setup_ui()
        self.setup_search()
        
    def setup_ui(self):
        self.setWindowTitle("搜索会话")
        self.setModal(True)
        self.resize(600, 500)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QLineEdit {
                border: 2px solid #e5e5e5;
                border-radius: 20px;
                padding: 12px 16px;
                font-size: 14px;
                font-family: "Microsoft YaHei";
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #0969da;
                background-color: #ffffff;
                outline: none;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f1f3f4;
                width: 8px;
                border: 'none;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # 标题
        title_label = QLabel("搜索会话")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1f2328; margin-bottom: 8px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入会话名称、唤醒词进行搜索...")
        self.search_input.setFixedHeight(44)
        layout.addWidget(self.search_input)
        
        # 结果提示
        self.result_label = QLabel(f"找到 {len(self.conversations)} 个会话")
        self.result_label.setFont(QFont("Microsoft YaHei", 10))
        self.result_label.setStyleSheet("color: #656d76; margin: 4px 0;")
        layout.addWidget(self.result_label)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 结果容器
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(8)
        
        self.scroll_area.setWidget(self.results_widget)
        layout.addWidget(self.scroll_area)
        
        # 取消按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFont(QFont("Microsoft YaHei", 10))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                padding: 8px 16px;
                color: #24292f;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                border-color: #d0d7de;
            }
            QPushButton:pressed {
                background-color: #e1e4e8;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def setup_search(self):
        """设置搜索功能"""
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.update_results()
        
    def on_search_text_changed(self):
        """搜索文本改变时触发"""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms延迟搜索
        
    def perform_search(self):
        """执行搜索"""
        query = self.search_input.text().strip().lower()
        
        if not query:
            self.filtered_conversations = self.conversations.copy()
        else:
            self.filtered_conversations = []
            for conv in self.conversations:
                # 搜索会话名称
                if query in conv['name'].lower():
                    self.filtered_conversations.append(conv)
                    continue
                
                # 搜索唤醒词
                wake_words_match = any(query in word.lower() for word in conv['wake_words'])
                if wake_words_match:
                    self.filtered_conversations.append(conv)
                    continue
        
        self.update_results()
        
    def update_results(self):
        """更新搜索结果显示"""
        # 清空现有结果
        for i in reversed(range(self.results_layout.count())):
            child = self.results_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 更新结果计数
        count = len(self.filtered_conversations)
        self.result_label.setText(f"找到 {count} 个会话")
        
        # 添加搜索结果
        if not self.filtered_conversations:
            no_result_label = QLabel("未找到匹配的会话")
            no_result_label.setFont(QFont("Microsoft YaHei", 12))
            no_result_label.setStyleSheet("color: #656d76; text-align: center; padding: 40px;")
            no_result_label.setAlignment(Qt.AlignCenter)
            self.results_layout.addWidget(no_result_label)
        else:
            for conv in self.filtered_conversations:
                item = ConversationItem(conv)
                item.clicked.connect(self.on_conversation_selected)
                self.results_layout.addWidget(item)
        
        # 添加弹性空间
        self.results_layout.addStretch()
        
    def on_conversation_selected(self, conversation_data):
        """会话被选中时触发"""
        self.conversation_selected.emit(conversation_data)
        self.accept()


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setup_sample_data()
        self.setup_ui()
        
    def setup_sample_data(self):
        """设置示例数据"""
        self.conversations = [
            {
                'name': '工作助手',
                'create_time': '2024-01-15 09:30',
                'last_used_time': '2024-06-12 14:20',
                'wake_words': ['工作', '工作', '任务', '安排'],
                'smart_mode': True
            },
            {
                'name': '学习伙伴',
                'create_time': '2024-02-20 16:45',
                'last_used_time': '2024-06-11 20:15',
                'wake_words': ['学习', '知识', '教学'],
                'smart_mode': True
            },
            {
                'name': '生活顾问',
                'create_time': '2024-03-10 11:20',
                'last_used_time': '2024-06-10 08:30',
                'wake_words': ['生活', '建议', '推荐'],
                'smart_mode': False
            },
            {
                'name': '创意写作',
                'create_time': '2024-04-05 19:15',
                'last_used_time': '2024-06-09 22:45',
                'wake_words': ['写作', '创意', '故事'],
                'smart_mode': True
            },
            {
                'name': '技术问答',
                'create_time': '2024-05-12 13:25',
                'last_used_time': '2024-06-08 16:10',
                'wake_words': ['编程', '技术', '代码'],
                'smart_mode': False
            }
        ]
        
    def setup_ui(self):
        self.setWindowTitle("会话管理器")
        self.setGeometry(300, 300, 400, 200)
        
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QPushButton {
                background-color: #0969da;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-family: "Microsoft YaHei";
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0860ca;
            }
            QPushButton:pressed {
                background-color: #0757ba;
            }
        """)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # 搜索按钮
        self.search_btn = QPushButton("🔍 搜索会话")
        self.search_btn.setFixedSize(200, 50)
        self.search_btn.clicked.connect(self.open_search_dialog)
        
        layout.addWidget(self.search_btn, alignment=Qt.AlignCenter)
        
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
        print(f"Agent模式: {'开启' if conversation_data['smart_mode'] else '关闭'}")
        print("-" * 40)


def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()