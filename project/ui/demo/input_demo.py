import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ===== 辅助类和常量 =====

class DPIHelper:
    """DPI 辅助类"""
    def __init__(self):
        self.scale_factor = 1.0
        
    def scale(self, value):
        return int(value * self.scale_factor)
        
    def scale_font_size(self, size):
        return int(size * self.scale_factor)

# 全局 DPI 辅助实例
dpi_helper = DPIHelper()

# 图标路径常量
MICROPHONE_ICON_PATH = "microphone.png"
STOP_ICON_PATH = "stop.png"

class PlainTextEdit(QTextEdit):
    """自定义文本编辑器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)
        
    def keyPressEvent(self, event):
        # 限制文本高度，防止无限扩展
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            if not (event.modifiers() & Qt.ShiftModifier):
                # 不处理回车，让父类处理
                return
        super().keyPressEvent(event)

class IconButton(QPushButton):
    """图标按钮"""
    def __init__(self, icon_path, fallback_text, size, parent=None):
        super().__init__(parent)
        self.fallback_text = fallback_text
        self.setFixedSize(size, size)
        self.update_icon(icon_path, fallback_text)
        
    def update_icon(self, icon_path, fallback_text):
        """更新图标"""
        self.fallback_text = fallback_text
        self.setText(fallback_text)

class ModernInputBox(QFrame):
    """现代化输入框组件 - 增强语音控制"""
    text_submitted = pyqtSignal(str)
    voice_requested = pyqtSignal()
    voice_force_stop_requested = pyqtSignal()  # 🔴 新增信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.voice_system_ready = False
        self.is_recording = False
        self.setupUI()
        self.setStyleSheet(self.getStyleSheet())

        # 🔴 新增：防止重复发送的参数
        self.last_submitted_text = ""
        self.last_submit_time = 0
        self.submit_cooldown = 1.0  # 1秒内不能发送相同内容

    def setupUI(self):
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(dpi_helper.scale(8))
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, dpi_helper.scale(2))
        self.setGraphicsEffect(shadow)

        # 设置主框架属性
        self.setFixedHeight(dpi_helper.scale(56))
        self.setMinimumWidth(dpi_helper.scale(400))
        self.setObjectName("modernInputFrame")

        # 创建水平布局
        layout = QHBoxLayout()
        layout.setContentsMargins(
            dpi_helper.scale(16), dpi_helper.scale(10),
            dpi_helper.scale(8), dpi_helper.scale(10)
        )
        layout.setSpacing(dpi_helper.scale(8))

        # 创建输入框
        self.input_field = PlainTextEdit()
        self.input_field.setObjectName("modernInputField")
        self.input_field.setPlaceholderText("请输入您的问题，或点击麦克风进行语音输入...")
        self.input_field.setFixedHeight(dpi_helper.scale(36))
        self.input_field.setFont(
            QFont("Microsoft YaHei", dpi_helper.scale_font_size(10)))

        # 输入框设置
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_field.setLineWrapMode(QTextEdit.WidgetWidth)
        self.input_field.document().setDocumentMargin(dpi_helper.scale(2))
        self.input_field.installEventFilter(self)

        # 创建按钮
        button_size = dpi_helper.scale(40)
        self.mic_button = IconButton(MICROPHONE_ICON_PATH, "🎤", button_size)
        self.mic_button.setObjectName("modernMicButton")
        self.mic_button.setToolTip("语音输入")
        self.mic_button.clicked.connect(self.handle_mic_button_click)  # 🔴 修改

        self.send_button = IconButton("icons/send.png", "➤", button_size)
        self.send_button.setObjectName("modernSendButton")
        self.send_button.setToolTip("发送消息")
        self.send_button.clicked.connect(self.onSubmit)

        # 添加组件到布局
        layout.addWidget(self.input_field)
        layout.addWidget(self.mic_button)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    # 🔴 新增：处理麦克风按钮点击
    def handle_mic_button_click(self):
        """处理麦克风按钮点击"""
        if self.is_recording:
            # 如果正在录音，点击可以手动停止
            self.voice_force_stop_requested.emit()
        else:
            # 开始录音
            self.voice_requested.emit()

    def eventFilter(self, obj, event):
        """处理回车键发送"""
        if obj == self.input_field:
            if event.type() == event.KeyPress:
                if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and \
                   not (event.modifiers() & Qt.ShiftModifier):
                    self.onSubmit()
                    return True
        return super().eventFilter(obj, event)

    def onSubmit(self):
        """🔴 修改：防止重复提交"""
        text = self.input_field.toPlainText().strip()
        if not text:
            return

        current_time = time.time()

        # 检查是否是重复提交
        if (text == self.last_submitted_text and
                current_time - self.last_submit_time < self.submit_cooldown):
            print(f"跳过重复提交: {text}")
            return

        # 更新记录
        self.last_submitted_text = text
        self.last_submit_time = current_time

        self.text_submitted.emit(text)
        self.input_field.clear()

    def setText(self, text):
        self.input_field.setPlainText(text)

    def text(self):
        return self.input_field.toPlainText()

    def clear(self):
        self.input_field.clear()

    def setPlaceholderText(self, text):
        self.input_field.setPlaceholderText(text)

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.input_field.setEnabled(enabled)
        self.mic_button.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

    # 麦克风状态更新方法
    def update_mic_button_starting(self):
        """更新麦克风按钮为启动状态"""
        self.mic_button.setEnabled(False)
        self.mic_button.update_icon(MICROPHONE_ICON_PATH, "⏳")
        self.mic_button.setToolTip("正在启动语音识别系统...")
        self.update_mic_button_style("starting")

    def update_mic_button_recording(self):
        """更新麦克风按钮为录音状态"""
        self.is_recording = True
        self.mic_button.setEnabled(True)
        self.mic_button.update_icon(STOP_ICON_PATH, "⏹")
        self.mic_button.setToolTip("点击停止录音")  # 🔴 修改提示
        self.update_mic_button_style("recording")

    def update_mic_button_normal(self):
        """更新麦克风按钮为正常状态"""
        self.is_recording = False
        self.mic_button.setEnabled(True)
        self.mic_button.update_icon(MICROPHONE_ICON_PATH, "🎤")
        self.mic_button.setToolTip("语音输入")
        self.update_mic_button_style("normal")

    def update_mic_button_style(self, state):
        """更新麦克风按钮样式"""
        border_radius = dpi_helper.scale(20)
        padding = dpi_helper.scale(8)

        if state == "starting":
            hover_color = "rgba(255, 152, 0, 0.1)"
        elif state == "recording":
            hover_color = "rgba(244, 67, 54, 0.1)"
        else:
            hover_color = "rgba(0, 0, 0, 0.05)"

        self.mic_button.setStyleSheet(f"""
            QPushButton#modernMicButton {{
                background: transparent;
                border: none;
                border-radius: {border_radius}px;
                padding: {padding}px;
                font-size: {dpi_helper.scale_font_size(16)}px;
                color: #666666;
            }}
            QPushButton#modernMicButton:hover {{
                background-color: {hover_color};
            }}
        """)

    def update_send_button_processing(self, processing=False):
        """更新发送按钮处理状态"""
        if processing:
            self.send_button.update_icon("icons/send.png", "⏳")
            self.send_button.setToolTip("处理中...")
            self.send_button.setEnabled(False)
        else:
            self.send_button.update_icon("icons/send.png", "➤")
            self.send_button.setToolTip("发送消息")
            self.send_button.setEnabled(True)

    def getStyleSheet(self):
        border_radius = dpi_helper.scale(6)
        padding = dpi_helper.scale(6)
        font_size = dpi_helper.scale_font_size(14)
        placeholder_font_size = dpi_helper.scale_font_size(13)
        button_font_size = dpi_helper.scale_font_size(16)
        button_radius = dpi_helper.scale(20)
        button_padding = dpi_helper.scale(8)

        return f"""
            QFrame#modernInputFrame {{
                background-color: white;
                border: 1px solid #E5E5E5;
                border-radius: {border_radius}px;
                margin: 0px;
            }}
            
            QFrame#modernInputFrame:focus-within {{
                border: 1px solid #4A90E2;
            }}
            
            QTextEdit#modernInputField {{
                background-color: transparent;
                border: none;
                padding: {padding}px {padding + 2}px;
                font-size: {font_size}px;
                color: #333333;
                selection-background-color: #4A90E2;
            }}
            
            QTextEdit#modernInputField::placeholder {{
                color: #999999;
                font-size: {placeholder_font_size}px;
                line-height: 1.3;
            }}
            
            QPushButton#modernMicButton, QPushButton#modernSendButton {{
                background: transparent;
                border: none;
                border-radius: {button_radius}px;
                font-size: {button_font_size}px;
                color: #666666;
                padding: {button_padding}px;
            }}
            
            QPushButton#modernMicButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
            
            QPushButton#modernSendButton {{
                color: #1976D2;
                font-weight: bold;
            }}
            
            QPushButton#modernSendButton:hover {{
                background-color: rgba(0, 0, 0, 0.05);
            }}
        """

# ===== Demo 应用程序 =====

class DemoMainWindow(QMainWindow):
    """Demo 主窗口"""
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.voice_timer = None
        
    def setupUI(self):
        self.setWindowTitle("ModernInputBox Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title = QLabel("ModernInputBox 组件演示")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # 说明文字
        description = QLabel("""
        功能演示：
        • 支持文本输入和回车发送
        • 点击麦克风按钮模拟语音输入
        • 防重复提交（1秒内相同内容）
        • 现代化的UI设计
        • 支持处理状态显示
        """)
        description.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        layout.addWidget(description)
        
        # 消息显示区域
        self.message_area = QTextEdit()
        self.message_area.setReadOnly(True)
        self.message_area.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                color: #333333;
            }
        """)
        self.message_area.setPlaceholderText("消息将显示在这里...")
        layout.addWidget(self.message_area)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("清空消息")
        self.clear_button.clicked.connect(self.clear_messages)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        self.disable_button = QPushButton("禁用组件")
        self.disable_button.clicked.connect(self.toggle_input_enabled)
        self.disable_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.disable_button)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 创建输入框
        self.input_box = ModernInputBox()
        self.input_box.text_submitted.connect(self.on_text_submitted)
        self.input_box.voice_requested.connect(self.on_voice_requested)
        self.input_box.voice_force_stop_requested.connect(self.on_voice_force_stop)
        
        layout.addWidget(self.input_box)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
        
    def on_text_submitted(self, text):
        """处理文本提交"""
        self.add_message(f"📝 发送消息: {text}")
        
        # 模拟处理状态
        self.input_box.update_send_button_processing(True)
        QTimer.singleShot(1500, lambda: self.input_box.update_send_button_processing(False))
        
    def on_voice_requested(self):
        """处理语音请求"""
        self.add_message("🎤 开始语音识别...")
        
        # 模拟语音识别流程
        self.input_box.update_mic_button_starting()
        
        # 2秒后开始录音
        QTimer.singleShot(2000, self.start_recording)
        
    def start_recording(self):
        """开始录音"""
        self.input_box.update_mic_button_recording()
        self.add_message("🔴 正在录音... (点击停止按钮或等待自动停止)")
        
        # 5秒后自动停止
        self.voice_timer = QTimer()
        self.voice_timer.setSingleShot(True)
        self.voice_timer.timeout.connect(self.stop_recording)
        self.voice_timer.start(5000)
        
    def on_voice_force_stop(self):
        """强制停止语音"""
        if self.voice_timer:
            self.voice_timer.stop()
        self.stop_recording()
        self.add_message("⏹ 手动停止录音")
        
    def stop_recording(self):
        """停止录音"""
        self.input_box.update_mic_button_normal()
        
        # 模拟识别结果
        demo_texts = [
            "这是语音识别的结果",
            "今天天气怎么样？",
            "帮我查询一下最新消息",
            "语音输入测试成功"
        ]
        
        import random
        recognized_text = random.choice(demo_texts)
        self.input_box.setText(recognized_text)
        self.add_message(f"✅ 语音识别完成: {recognized_text}")
        
    def add_message(self, message):
        """添加消息到显示区域"""
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        formatted_message = f"[{current_time}] {message}"
        self.message_area.append(formatted_message)
        
        # 自动滚动到底部
        scrollbar = self.message_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_messages(self):
        """清空消息"""
        self.message_area.clear()
        self.add_message("消息已清空")
        
    def toggle_input_enabled(self):
        """切换输入框启用状态"""
        is_enabled = self.input_box.isEnabled()
        self.input_box.setEnabled(not is_enabled)
        
        if is_enabled:
            self.disable_button.setText("启用组件")
            self.disable_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.add_message("⚠️ 输入框已禁用")
        else:
            self.disable_button.setText("禁用组件")
            self.disable_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.add_message("✅ 输入框已启用")

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    window = DemoMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()