import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QLabel, QLineEdit, QCheckBox, QPushButton, 
                             QGroupBox, QListWidget, QListWidgetItem, QMessageBox,
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import datetime

class WakeWordsList(QFrame):
    """唤醒词列表组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # 添加唤醒词区域
        add_layout = QHBoxLayout()
        add_layout.setSpacing(8)
        
        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("输入唤醒词...")
        self.word_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        
        self.add_btn = QPushButton("添加")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-size: 12px;
                font-weight: 500;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.add_btn.clicked.connect(self.add_word)
        
        add_layout.addWidget(self.word_input)
        add_layout.addWidget(self.add_btn)
        layout.addLayout(add_layout)
        
        # 唤醒词列表
        self.word_list = QListWidget()
        self.word_list.setMaximumHeight(120)
        self.word_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #f8f9fa;
                selection-background-color: #007bff;
                selection-color: white;
                font-size: 12px;
                padding: 2px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #e9ecef;
                background-color: white;
                margin: 1px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
                color: black;
            }
        """)
        layout.addWidget(self.word_list)
        
        # 删除按钮
        self.delete_btn = QPushButton("删除选中")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 15px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #adb5bd;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        layout.addWidget(self.delete_btn)
        
        # 连接信号
        self.word_input.returnPressed.connect(self.add_word)
        self.word_list.itemSelectionChanged.connect(self.update_delete_button)
        
    def add_word(self):
        """添加唤醒词"""
        word = self.word_input.text().strip()
        if not word:
            return
            
        # 检查是否已存在
        for i in range(self.word_list.count()):
            if self.word_list.item(i).text() == word:
                QMessageBox.information(self, "提示", f"唤醒词 '{word}' 已存在！")
                return
        
        # 添加到列表
        self.word_list.addItem(word)
        self.word_input.clear()
        
    def delete_selected(self):
        """删除选中的唤醒词"""
        current_item = self.word_list.currentItem()
        if current_item:
            row = self.word_list.row(current_item)
            self.word_list.takeItem(row)
            
    def update_delete_button(self):
        """更新删除按钮状态"""
        self.delete_btn.setEnabled(self.word_list.currentItem() is not None)
        
    def set_words(self, words):
        """设置唤醒词列表"""
        self.word_list.clear()
        for word in words:
            self.word_list.addItem(word)
            
    def get_words(self):
        """获取唤醒词列表"""
        words = []
        for i in range(self.word_list.count()):
            words.append(self.word_list.item(i).text())
        return words


class ConversationEditDialog(QDialog):
    """会话编辑对话框"""
    
    def __init__(self, conversation_data=None, parent=None):
        super().__init__(parent)
        print("====================open edit===================")
        self.conversation_data = conversation_data or {}
        self.setWindowTitle("编辑会话")
        self.setModal(True)
        self.resize(500, 650)
        
        # 存储参数值
        self.parameters = {}
        self.widgets = {}
        
        # 设置样式
        self.setup_style()
        
        # 创建界面
        self.setup_ui()
        
        # 加载数据
        if self.conversation_data:
            self.load_data()
    
    def format_timestamp(self, timestamp):
        """
        将时间戳转换为可读的时间格式
        支持多种输入格式：整数时间戳、浮点时间戳、字符串时间戳、已格式化的时间字符串
        """
        if not timestamp:
            return "未知"
        
        try:
            # 如果已经是格式化的时间字符串，直接返回
            if isinstance(timestamp, str):
                # 尝试解析是否为有效的时间格式字符串
                try:
                    # 检查是否为 YYYY-MM-DD HH:MM 格式
                    if len(timestamp) >= 16 and '-' in timestamp and ':' in timestamp:
                        datetime.datetime.strptime(timestamp[:16], '%Y-%m-%d %H:%M')
                        return timestamp
                    # 检查是否为 YYYY-MM-DD HH:MM:SS 格式
                    elif len(timestamp) >= 19 and '-' in timestamp and ':' in timestamp:
                        datetime.datetime.strptime(timestamp[:19], '%Y-%m-%d %H:%M:%S')
                        return timestamp
                    else:
                        # 尝试转换为数字时间戳
                        timestamp = float(timestamp)
                except ValueError:
                    # 如果解析失败，尝试作为时间戳处理
                    try:
                        timestamp = float(timestamp)
                    except ValueError:
                        return timestamp  # 返回原字符串
            
            # 处理数字时间戳
            if isinstance(timestamp, (int, float)):
                # 检查时间戳长度，处理毫秒时间戳
                if timestamp > 1e10:  # 毫秒时间戳
                    timestamp = timestamp / 1000
                
                # 转换为datetime对象
                dt = datetime.datetime.fromtimestamp(timestamp)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            return str(timestamp)
            
        except (ValueError, OSError, OverflowError) as e:
            print(f"时间戳转换错误: {e}, 原始值: {timestamp}")
            return str(timestamp)
        
    def setup_style(self):
        """设置现代化样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 12px;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
            }
            
            QLabel {
                color: #495057;
                font-size: 12px;
                font-weight: 500;
            }
            
            QLabel.info-label {
                color: #6c757d;
                font-size: 11px;
                font-style: italic;
            }
            
            QLabel.readonly-label {
                color: #6c757d;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
            }
            
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                selection-background-color: #007bff;
            }
            
            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QLineEdit:hover {
                border-color: #80bdff;
            }
            
            QCheckBox {
                spacing: 8px;
                color: #495057;
                font-size: 13px;
                font-weight: 500;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #dee2e6;
                # background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjUgNEw2IDExLjVMMi41IDhMMS41IDlMNiAxMy41TDE0LjUgNUwxMy41IDRaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K);
            }
            
            QCheckBox::indicator:hover {
                border-color: #007bff;
            }
            
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #0056b3;
            }
            
            QPushButton:pressed {
                background-color: #004494;
            }
            
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)
    
    def setup_ui(self):
        """创建用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        title_label = QLabel("编辑会话")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建参数组
        self.create_basic_info(layout)
        self.create_editable_params(layout)
        
        # 弹性空间
        layout.addStretch()
        
        # 按钮区域
        self.create_buttons(layout)
        
    def create_basic_info(self, parent_layout):
        """创建基本信息组（只读）"""
        group = QGroupBox("基本信息（只读）")
        layout = QFormLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # ID
        self.id_label = QLabel()
        self.id_label.setObjectName("readonly-label")
        self.id_label.setStyleSheet("QLabel { color: #6c757d; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 8px 12px; font-size: 13px; }")
        layout.addRow("会话ID:", self.id_label)
        
        # 创建时间
        self.create_time_label = QLabel()
        self.create_time_label.setObjectName("readonly-label")
        self.create_time_label.setStyleSheet("QLabel { color: #6c757d; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 8px 12px; font-size: 13px; }")
        layout.addRow("创建时间:", self.create_time_label)
        
        # 最后使用时间
        self.last_time_label = QLabel()
        self.last_time_label.setObjectName("readonly-label")
        self.last_time_label.setStyleSheet("QLabel { color: #6c757d; background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 8px 12px; font-size: 13px; }")
        layout.addRow("最后使用:", self.last_time_label)
        
        parent_layout.addWidget(group)
        
    def create_editable_params(self, parent_layout):
        """创建可编辑参数组"""
        group = QGroupBox("可编辑参数")
        layout = QFormLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # 会话名称
        self.widgets['name'] = QLineEdit()
        self.widgets['name'].setPlaceholderText("请输入会话名称")
        layout.addRow("会话名称:", self.widgets['name'])
        
        # 唤醒词列表
        wake_words_layout = QVBoxLayout()
        wake_words_info = QLabel("可以添加多个唤醒词，用于快速识别会话")
        wake_words_info.setObjectName("info-label")
        wake_words_info.setStyleSheet("QLabel { color: #6c757d; font-size: 11px; font-style: italic; margin-bottom: 5px; }")
        
        self.widgets['wake_words'] = WakeWordsList()
        
        wake_words_layout.addWidget(wake_words_info)
        wake_words_layout.addWidget(self.widgets['wake_words'])
        layout.addRow("唤醒词:", wake_words_layout)
        
        # 智能模式
        smart_mode_layout = QVBoxLayout()
        smart_mode_info = QLabel("开启后将启用智能分析和优化功能")
        smart_mode_info.setObjectName("info-label")
        smart_mode_info.setStyleSheet("QLabel { color: #6c757d; font-size: 11px; font-style: italic; margin-bottom: 5px; }")
        
        self.widgets['smart_mode'] = QCheckBox("启用Agent模式")
        self.widgets['smart_mode'].setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #2c3e50;
            }
        """)
        
        smart_mode_layout.addWidget(smart_mode_info)
        smart_mode_layout.addWidget(self.widgets['smart_mode'])
        layout.addRow("", smart_mode_layout)
        
        parent_layout.addWidget(group)
        
    def create_buttons(self, parent_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_changes)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(save_btn)
        
        parent_layout.addLayout(button_layout)
        
    def load_data(self):
        """加载会话数据"""
        # 加载只读信息
        self.id_label.setText(self.conversation_data.get('id', ''))
        
        # 格式化时间戳显示
        create_time = self.conversation_data.get('create_time', '')
        formatted_create_time = self.format_timestamp(create_time)
        self.create_time_label.setText(formatted_create_time)
        
        last_time = self.conversation_data.get('last_used_time', '')
        formatted_last_time = self.format_timestamp(last_time)
        self.last_time_label.setText(formatted_last_time)
        
        # 加载可编辑信息
        self.widgets['name'].setText(self.conversation_data.get('name', ''))
        self.widgets['wake_words'].set_words(self.conversation_data.get('wake_words', []))
        self.widgets['smart_mode'].setChecked(self.conversation_data.get('smart_mode', False))
        
    def save_changes(self):
        """保存更改"""
        # 验证输入
        name = self.widgets['name'].text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "会话名称不能为空！")
            self.widgets['name'].setFocus()
            return
            
        wake_words = self.widgets['wake_words'].get_words()
        if not wake_words:
            reply = QMessageBox.question(
                self, "确认", 
                "没有设置唤醒词，确定要保存吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 收集参数（保留原始时间戳格式）
        self.parameters = {
            'id': self.conversation_data.get('id', ''),
            'name': name,
            'create_time': self.conversation_data.get('create_time', ''),  # 保留原始时间戳
            'last_used_time': self.conversation_data.get('last_used_time', ''),  # 保留原始时间戳
            'wake_words': wake_words,
            'smart_mode': self.widgets['smart_mode'].isChecked(),
        }
        
        self.accept()
        
    def get_parameters(self):
        """获取参数字典"""
        return self.parameters


# 使用示例
def main():
    app = QApplication(sys.argv)
    
    # 测试数据 - 使用不同格式的时间戳
    test_data = {
        'id': '111111111111114',
        'name': '生活顾问',
        'create_time': 1710072000,  # 整数时间戳
        'last_used_time': '1717977000.123',  # 字符串格式的浮点时间戳
        'wake_words': ['生活', '建议', '推荐'],
        'smart_mode': False
    }
    
    # 也可以测试毫秒时间戳
    # test_data['create_time'] = 1710072000000  # 毫秒时间戳
    
    # 创建对话框
    dialog = ConversationEditDialog(test_data)
    
    # 显示对话框
    if dialog.exec_() == QDialog.Accepted:
        params = dialog.get_parameters()
        print("用户修改后的参数:")
        for key, value in params.items():
            print(f"  {key}: {value}")
    else:
        print("用户取消了操作")
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()