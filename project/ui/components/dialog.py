import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QFormLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QCheckBox, QComboBox, QPushButton, QGroupBox, QFrame,
                             QTextEdit, QSlider, QProgressBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon


class ModernParameterDialog(QDialog):
    """现代化的参数设置对话框"""
    
    def __init__(self, title="参数设置", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(450, 600)
        
        # 存储参数值
        self.parameters = {}
        self.widgets = {}
        
        # 设置样式
        self.setup_style()
        
        # 创建界面
        self.setup_ui()
        
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
            
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                selection-background-color: #007bff;
            }
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
                border-color: #007bff;
                outline: none;
            }
            
            QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {
                border-color: #80bdff;
            }
            
            QCheckBox {
                spacing: 8px;
                color: #495057;
                font-size: 13px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #dee2e6;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border-color: #007bff;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjg1IDQuMTVMMy4xNSA0LjE1TDYuNSAxMy44NUwxMy44NSA0LjE1WiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+);
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #e9ecef;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #007bff;
                border: 2px solid #0056b3;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #0056b3;
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
            
            QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            
            QTextEdit:focus {
                border-color: #007bff;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
        """)
    
    def setup_ui(self):
        """创建用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        title_label = QLabel("参数配置")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 创建参数组
        self.create_basic_params(layout)
        self.create_advanced_params(layout)
        
        # 弹性空间
        layout.addStretch()
        
        # 按钮区域
        self.create_buttons(layout)
        
    def create_basic_params(self, parent_layout):
        """创建基础参数组"""
        group = QGroupBox("基础参数")
        layout = QFormLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # 项目名称
        self.widgets['project_name'] = QLineEdit()
        self.widgets['project_name'].setPlaceholderText("请输入项目名称")
        layout.addRow("项目名称:", self.widgets['project_name'])
        
        # 数值参数
        self.widgets['max_count'] = QSpinBox()
        self.widgets['max_count'].setRange(1, 9999)
        self.widgets['max_count'].setValue(100)
        layout.addRow("最大数量:", self.widgets['max_count'])
        
        # 精度参数
        self.widgets['precision'] = QDoubleSpinBox()
        self.widgets['precision'].setRange(0.01, 10.0)
        self.widgets['precision'].setValue(0.1)
        self.widgets['precision'].setSingleStep(0.01)
        self.widgets['precision'].setDecimals(3)
        layout.addRow("精度:", self.widgets['precision'])
        
        # 选择框
        self.widgets['mode'] = QComboBox()
        self.widgets['mode'].addItems(['自动模式', '手动模式', '混合模式'])
        layout.addRow("运行模式:", self.widgets['mode'])
        
        # 复选框
        self.widgets['enable_cache'] = QCheckBox("启用缓存")
        self.widgets['enable_cache'].setChecked(True)
        layout.addRow("", self.widgets['enable_cache'])
        
        parent_layout.addWidget(group)
        
    def create_advanced_params(self, parent_layout):
        """创建高级参数组"""
        group = QGroupBox("高级参数")
        layout = QFormLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # 滑块参数
        slider_layout = QVBoxLayout()
        self.widgets['timeout'] = QSlider(Qt.Horizontal)
        self.widgets['timeout'].setRange(1, 60)
        self.widgets['timeout'].setValue(30)
        self.timeout_label = QLabel("超时时间: 30 秒")
        self.timeout_label.setStyleSheet("color: #007bff; font-weight: 500;")
        self.widgets['timeout'].valueChanged.connect(
            lambda v: self.timeout_label.setText(f"超时时间: {v} 秒")
        )
        
        slider_layout.addWidget(self.timeout_label)
        slider_layout.addWidget(self.widgets['timeout'])
        layout.addRow("", slider_layout)
        
        # 多行文本
        self.widgets['description'] = QTextEdit()
        self.widgets['description'].setMaximumHeight(80)
        self.widgets['description'].setPlaceholderText("请输入描述信息...")
        layout.addRow("描述:", self.widgets['description'])
        
        # 多个复选框
        checkbox_layout = QVBoxLayout()
        self.widgets['auto_save'] = QCheckBox("自动保存")
        self.widgets['backup'] = QCheckBox("创建备份")
        self.widgets['notifications'] = QCheckBox("启用通知")
        
        for cb in [self.widgets['auto_save'], self.widgets['backup'], self.widgets['notifications']]:
            checkbox_layout.addWidget(cb)
        
        layout.addRow("选项:", checkbox_layout)
        
        parent_layout.addWidget(group)
        
    def create_buttons(self, parent_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept_params)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(ok_btn)
        
        parent_layout.addLayout(button_layout)
        
    def accept_params(self):
        """接受参数并返回"""
        # 收集所有参数
        self.parameters = {
            'project_name': self.widgets['project_name'].text(),
            'max_count': self.widgets['max_count'].value(),
            'precision': self.widgets['precision'].value(),
            'mode': self.widgets['mode'].currentText(),
            'enable_cache': self.widgets['enable_cache'].isChecked(),
            'timeout': self.widgets['timeout'].value(),
            'description': self.widgets['description'].toPlainText(),
            'auto_save': self.widgets['auto_save'].isChecked(),
            'backup': self.widgets['backup'].isChecked(),
            'notifications': self.widgets['notifications'].isChecked(),
        }
        
        self.accept()
        
    def get_parameters(self):
        """获取参数字典"""
        return self.parameters
        
    def set_parameters(self, params):
        """设置参数初始值"""
        if 'project_name' in params:
            self.widgets['project_name'].setText(params['project_name'])
        if 'max_count' in params:
            self.widgets['max_count'].setValue(params['max_count'])
        if 'precision' in params:
            self.widgets['precision'].setValue(params['precision'])
        if 'mode' in params:
            index = self.widgets['mode'].findText(params['mode'])
            if index >= 0:
                self.widgets['mode'].setCurrentIndex(index)
        if 'enable_cache' in params:
            self.widgets['enable_cache'].setChecked(params['enable_cache'])
        if 'timeout' in params:
            self.widgets['timeout'].setValue(params['timeout'])
        if 'description' in params:
            self.widgets['description'].setPlainText(params['description'])
        if 'auto_save' in params:
            self.widgets['auto_save'].setChecked(params['auto_save'])
        if 'backup' in params:
            self.widgets['backup'].setChecked(params['backup'])
        if 'notifications' in params:
            self.widgets['notifications'].setChecked(params['notifications'])


# 使用示例
def main():
    app = QApplication(sys.argv)
    
    # 创建对话框
    dialog = ModernParameterDialog("系统配置")
    
    # 可选：设置初始参数
    initial_params = {
        'project_name': '测试项目',
        'max_count': 200,
        'precision': 0.05,
        'mode': '自动模式',
        'enable_cache': True,
        'timeout': 45,
        'description': '这是一个测试项目的描述信息。',
        'auto_save': True,
        'backup': False,
        'notifications': True
    }
    dialog.set_parameters(initial_params)
    
    # 显示对话框
    if dialog.exec_() == QDialog.Accepted:
        params = dialog.get_parameters()
        print("用户设置的参数:")
        for key, value in params.items():
            print(f"  {key}: {value}")
    else:
        print("用户取消了操作")
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()