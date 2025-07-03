import sys
import markdown
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QPushButton, QScrollArea, QFrame,
                             QLabel, QLineEdit, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QColor, QFontMetrics, QPainter, QPainterPath, QBrush
from qfluentwidgets import FluentIcon, IconWidget

class MessageWidget(QFrame):
    """单条消息组件 - 支持Markdown格式，自适应高度和宽度，最大宽度70%，美观的气泡样式"""
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.message_text = message
        self.max_width_ratio = 0.7  # 增大最大宽度比例到70%
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        # 设置框架样式 - 占满整行，增加上下间距
        self.setFrameStyle(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 创建主布局 - 增加垂直间距
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 12, 20, 12)  # 增加左右边距
        
        # 创建消息文本框（支持富文本）
        self.message_text_edit = QTextEdit()
        self.message_text_edit.setReadOnly(True)
        
        # 使用更现代的字体
        if sys.platform == "win32":
            font = QFont("Segoe UI", 10)
        elif sys.platform == "darwin":
            font = QFont("SF Pro Text", 10)
        else:
            font = QFont("Ubuntu", 10)
        
        self.message_text_edit.setFont(font)
        
        # 设置文本框自动调整高度和宽度
        self.message_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_text_edit.setWordWrapMode(1)  # 启用自动换行
        
        # 转换markdown为HTML并设置内容
        self.set_markdown_content(self.message_text)
        
        # 设置消息样式和对齐
        if self.is_user:
            # 用户消息 - 靠右，现代蓝色渐变背景，最大宽度70%
            # 左侧弹性空间
            left_spacer = QWidget()
            left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            main_layout.addWidget(left_spacer, 6)
            
            # 消息内容
            self.message_text_edit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            main_layout.addWidget(self.message_text_edit,3)
            
            icon = IconWidget(FluentIcon.PEOPLE.colored(QColor(255, 0, 0), QColor(0, 0, 255)))
            icon.setMaximumSize(30, 30)
            main_layout.addWidget(icon, 1)
            
            # 现代化的用户消息样式
            self.message_text_edit.setStyleSheet("""
                QTextEdit {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                               stop:0 #007AFF, stop:1 #0056CC);
                    color: white;
                    padding: 16px 20px;
                    border-radius: 20px;
                    margin: 0px;
                    border: none;
                    font-weight: 500;
                    selection-background-color: rgba(255, 255, 255, 0.3);
                }
                QTextEdit:focus {
                    outline: none;
                }
            """)
            
        else:
            # AI消息 - 靠左，优雅的浅色背景，最大宽度70%
            # 消息内容
            self.message_text_edit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            icon = IconWidget(FluentIcon.ROBOT.colored(QColor(255, 0, 0), QColor(0, 0, 255)))
            icon.setMaximumSize(30, 30)
            main_layout.addWidget(icon, 1)
            main_layout.addWidget(self.message_text_edit, 5)
            # 右侧弹性空间
            right_spacer = QWidget()
            right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            main_layout.addWidget(right_spacer, 4)
            
            # 现代化的AI消息样式
            self.message_text_edit.setStyleSheet("""
                QTextEdit {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #F8F9FA, stop:1 #E9ECEF);
                    color: black;
                    padding: 16px 20px;
                    border-radius: 20px;
                    margin: 0px;
                    border: 1px solid #E9ECEF;
                    font-weight: 400;
                    selection-background-color: rgba(0, 122, 255, 0.2);
                }
                QTextEdit:focus {
                    outline: none;
                    border: 1px solid #007AFF;
                }
            """)
        
        # 添加阴影效果
        self.add_shadow_effect()
        
        # 调整文本框尺寸以适应内容
        self.adjust_text_edit_size()

    def add_shadow_effect(self):
        """添加优雅的阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 25))  # 25% 透明度的黑色
        shadow.setOffset(0, 2)
        self.message_text_edit.setGraphicsEffect(shadow)

    def setup_animations(self):
        """设置动画效果"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutQuart)

    def set_markdown_content(self, markdown_text):
        """将markdown文本转换为HTML并设置到文本框"""
        try:
            # 使用markdown库转换为HTML
            html_content = markdown.markdown(
                markdown_text,
                extensions=['codehilite', 'fenced_code', 'tables', 'toc']
            )
            
            # 优化的CSS样式，更现代化的设计
            styled_html = f"""
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Ubuntu', sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                    font-size: 14px;
                }}
                p {{
                    margin: 0 0 12px 0;
                }}
                p:last-child {{
                    margin-bottom: 0;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    margin: 16px 0 8px 0;
                    font-weight: 600;
                    line-height: 1.3;
                }}
                h1:first-child, h2:first-child, h3:first-child,
                h4:first-child, h5:first-child, h6:first-child {{
                    margin-top: 0;
                }}
                code {{
                    background-color: {'rgba(255, 255, 255, 0.15)' if self.is_user else 'rgba(0, 0, 0, 0.05)'};
                    color: {'#FFE4E1' if self.is_user else '#D73A49'};
                    padding: 3px 6px;
                    border-radius: 6px;
                    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
                    font-size: 13px;
                    word-wrap: break-word;
                    white-space: pre-wrap;
                }}
                pre {{
                    background-color: {'rgba(255, 255, 255, 0.1)' if self.is_user else '#F6F8FA'};
                    color: {'#FFFFFF' if self.is_user else '#24292E'};
                    padding: 16px;
                    border-radius: 12px;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
                    font-size: 13px;
                    line-height: 1.4;
                    margin: 12px 0;
                    border: {'1px solid rgba(255, 255, 255, 0.2)' if self.is_user else '1px solid #E1E4E8'};
                }}
                pre:first-child {{
                    margin-top: 0;
                }}
                pre:last-child {{
                    margin-bottom: 0;
                }}
                blockquote {{
                    border-left: 4px solid {'rgba(255, 255, 255, 0.3)' if self.is_user else '#DFE2E5'};
                    margin: 12px 0;
                    padding: 8px 0 8px 16px;
                    color: {'rgba(255, 255, 255, 0.9)' if self.is_user else '#6A737D'};
                    font-style: italic;
                    word-wrap: break-word;
                }}
                ul, ol {{
                    margin: 12px 0;
                    padding-left: 24px;
                }}
                li {{
                    margin: 4px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 12px 0;
                    border-radius: 8px;
                    overflow: hidden;
                    background-color: {'rgba(255, 255, 255, 0.05)' if self.is_user else '#FFFFFF'};
                }}
                th, td {{
                    border: 1px solid {'rgba(255, 255, 255, 0.2)' if self.is_user else '#E1E4E8'};
                    padding: 12px;
                    text-align: left;
                    word-wrap: break-word;
                }}
                th {{
                    background-color: {'rgba(255, 255, 255, 0.1)' if self.is_user else '#F6F8FA'};
                    font-weight: 600;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 8px;
                    margin: 8px 0;
                }}
                a {{
                    color: {'#7DD3FC' if self.is_user else '#0366D6'};
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                strong {{
                    font-weight: 600;
                }}
                em {{
                    font-style: italic;
                }}
                * {{
                    max-width: 100%;
                    word-wrap: break-word;
                }}
            </style>
            {html_content}
            """
            
            self.message_text_edit.setHtml(styled_html)
            
        except Exception as e:
            # 如果markdown转换失败，直接显示原始文本
            print(f"Markdown转换错误: {e}")
            self.message_text_edit.setPlainText(markdown_text)

    def calculate_optimal_width(self, text_content):
        """根据文档内容计算最佳宽度"""
        # 获取字体信息
        font = self.message_text_edit.font()
        font_metrics = QFontMetrics(font)
        
        # 获取父窗口宽度
        parent_width = self.parent().width() if self.parent() else 800
        max_allowed_width = int(parent_width * self.max_width_ratio)
        
        # 分行处理文本
        lines = text_content.split('\n')
        max_line_width = 0
        
        for line in lines:
            # 处理markdown语法，简单估算实际显示宽度
            clean_line = line.replace('**', '').replace('*', '').replace('#', '')
            clean_line = clean_line.replace('`', '').replace('>', '')
            
            # 如果是代码块，使用等宽字体计算
            if '```' in line or line.strip().startswith('    '):
                # 代码行通常需要更多空间
                line_width = font_metrics.width(clean_line) * 1.2
            else:
                line_width = font_metrics.width(clean_line)
            
            max_line_width = max(max_line_width, line_width)
        
        # 添加padding和边距
        padding = 40  # 增加padding
        margin = 24   # 增加边距
        
        # 计算最佳宽度
        optimal_width = max_line_width + padding + margin
        
        # 设置最小和最大宽度限制
        min_width = 280  # 增加最小宽度
        optimal_width = max(min_width, min(optimal_width, max_allowed_width))
        
        return int(optimal_width)

    def adjust_message_width_by_content(self):
        """根据文档内容调整消息widget宽度的函数"""
        # 获取纯文本内容用于宽度计算
        plain_text = self.message_text_edit.toPlainText()
        
        # 计算最佳宽度
        optimal_width = self.calculate_optimal_width(plain_text)
        
        # 设置文本框的最大宽度
        self.message_text_edit.setMaximumWidth(optimal_width)
        
        # 更新文档宽度并重新计算高度
        self.adjust_text_edit_size()
        
        return optimal_width

    def adjust_text_edit_size(self):
        """根据内容调整文本框高度，宽度由布局管理"""
        # 获取文档内容
        document = self.message_text_edit.document()
        
        # 设置文档宽度为文本框的当前宽度（由布局管理）
        QTimer.singleShot(0, self._delayed_size_adjustment)

    def _delayed_size_adjustment(self):
        """延迟调整尺寸，确保布局已经完成"""
        document = self.message_text_edit.document()
        
        # 获取文本框的当前宽度
        current_width = self.message_text_edit.width()
        if current_width <= 0:
            # 如果宽度还没有设置，使用父窗口的宽度
            parent_width = self.parent().width() if self.parent() else 800
            current_width = int(parent_width * self.max_width_ratio)
        
        # 确保不超过最大宽度
        max_width = int((self.parent().width() if self.parent() else 800) * self.max_width_ratio)
        current_width = min(current_width, max_width)
        
        # 设置最大宽度限制
        self.message_text_edit.setMaximumWidth(max_width)
        
        # 设置文档的文本宽度为当前宽度减去padding
        document.setTextWidth(current_width - 40)  # 减去增加的padding
        
        # 获取文档的高度
        content_height = document.size().height()
        
        # 设置高度约束
        min_height = 48  # 增加最小高度
        max_height = 1000  # 增加最大高度以适应长文本
        
        # 计算合适的高度
        adjusted_height = max(min_height, min(content_height + 24, max_height)) + 8
        
        # 只设置固定高度，让宽度由布局管理
        self.message_text_edit.setFixedHeight(int(adjusted_height))

    def set_max_width_ratio(self, ratio):
        """设置最大宽度比例"""
        self.max_width_ratio = max(0.1, min(1.0, ratio))  # 限制在10%-100%之间
        self.adjust_text_edit_size()

    def update_message(self, message):
        """更新消息内容"""
        self.message_text = message
        self.set_markdown_content(message)
        self.adjust_text_edit_size()

    def resizeEvent(self, event):
        """窗口大小改变时重新调整文本框尺寸"""
        super().resizeEvent(event)
        self.adjust_text_edit_size()

    def enterEvent(self, event):
        """鼠标进入时的动画效果"""
        super().enterEvent(event)
        # 可以在这里添加悬停效果
        pass

    def leaveEvent(self, event):
        """鼠标离开时的动画效果"""
        super().leaveEvent(event)
        # 可以在这里添加悬停效果
        pass


# 使用示例和测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QWidget()
    window.setWindowTitle("优化的消息气泡组件")
    window.setGeometry(100, 100, 800, 600)
    window.setStyleSheet("""
        QWidget {
            background-color: #F5F5F7;
        }
    """)
    
    # 创建布局
    layout = QVBoxLayout(window)
    
    # 创建一些测试消息
    messages = [
        ("你好！这是一条用户消息", True),
        ("您好！我是AI助手，很高兴为您服务。这是一条包含**粗体文本**和*斜体文本*的消息。", False),
        ("请帮我解释一下这段代码：\n\n```python\ndef hello_world():\n    print('Hello, World!')\n```", True),
        ("这是一段Python代码的解释：\n\n```python\ndef hello_world():\n    print('Hello, World!')\n```\n\n这个函数定义了一个名为`hello_world`的函数，当调用时会打印出'Hello, World!'。\n\n代码解释：\n- `def` 关键字用于定义函数\n- `hello_world` 是函数名\n- `print()` 用于输出文本", False),
        ("谢谢你的解释！", True)
    ]
    
    # 添加消息到布局
    for message, is_user in messages:
        msg_widget = MessageWidget(message, is_user, window)
        layout.addWidget(msg_widget)
    
    # 添加弹性空间
    layout.addStretch()
    
    window.show()
    sys.exit(app.exec_())