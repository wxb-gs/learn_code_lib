# streaming_message_widget.py
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                            QTextEdit, QFrame, QSizePolicy, QScrollArea, 
                             QApplication)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, QTextStream, QIODevice
from PyQt5.QtGui import QPixmap, QTextCursor, QFont, QColor, QTextDocument
import re
import mistune
from PyQt5.QtCore import QSize, Qt, QTimer
from styles.qeditor import scrollbar_style, qeditor_qss
from pathlib import Path

MAX_HEIGHT = 650
MIN_HEIGHT = 28

USER_MAX_WIDTH = 460
AI_MAX_WIDTH = 680

SYS_PATH = Path(__file__).resolve().parent.parent / "icon/sys.png" 
USER_PATH = Path(__file__).resolve().parent.parent / "icon/user.png" 

class StreamingMessageWidget(QWidget):
    """支持流式输出的消息气泡组件"""

    def __init__(self, message="", is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.full_message = message
        self.current_message = ""
        self.setup_ui()

    def setup_ui(self):
        # 设置组件的尺寸策略
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignTop)

        # 创建头像
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar.setScaledContents(True)
        avatar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # 设置头像图片
        if self.is_user:
            # print(f"=================================={USER_PATH}=================")
            pixmap = QPixmap(str(USER_PATH))
        else:
            pixmap = QPixmap(str(SYS_PATH))

        # 如果图片加载失败，设置默认背景
        avatar.setPixmap(pixmap)
        avatar.setStyleSheet("""
            QLabel {
                border-radius: 18px;
                border: 2px solid #e5e7eb;
                background-color: white;
            }
        """)

        # 创建消息气泡容器
        message_container = QWidget()
        if self.is_user:
            # 对于用户消息，使用Preferred策略并设置最大宽度
            message_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            message_container.setMaximumWidth(USER_MAX_WIDTH)
        else:
            message_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            message_container.setMaximumWidth(AI_MAX_WIDTH)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 创建消息气泡
        self.message_bubble = QFrame()
        self.message_bubble.setMinimumWidth(60)
        self.message_bubble.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.message_bubble.enterEvent = self.show_scrollbars
        self.message_bubble.leaveEvent = self.hide_scrollbars

        # 消息气泡样式 - 更明显的背景对比，类似GPT风格
        if self.is_user:
            # 用户消息：蓝色渐变背景
            self.message_bubble.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #dbeafe, stop:1 #bfdbfe);
                    border-radius: 18px;
                    border: 2px solid #93c5fd;
                    padding: 0px;
                    margin: 0px;
                }
            """)
        else:
            # AI消息：灰色背景，更明显的边框
            self.message_bubble.setStyleSheet("""
                QFrame {
                    background-color: #f9fafb;
                    border-radius: 18px;
                    border: 2px solid #d1d5db;
                    padding: 0px;
                    margin: 0px;
                }
            """)
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(10, 14, 2, 14)
        bubble_layout.setSpacing(12)

        # 创建主要内容区域
        self.message_edit = QTextEdit()
        self.message_edit.setPlainText(self.current_message)
        self.message_edit.setReadOnly(True)
        self.message_edit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # 设置QTextEdit样式
        self.message_edit.setStyleSheet(scrollbar_style + qeditor_qss)

        self.message_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_edit.setLineWrapMode(QTextEdit.WidgetWidth)

        self.message_edit.insertHtml(self.html_text(self.full_message))

        # 连接信号，自动调整高度
        self.message_edit.textChanged.connect(self.adjust_height)

        bubble_layout.addWidget(self.message_edit)

        self.message_bubble.setLayout(bubble_layout)
        container_layout.addWidget(self.message_bubble)
        message_container.setLayout(container_layout)

        # 布局设置
        if self.is_user:
            layout.addStretch(1)  # 在左侧添加弹性空间
            layout.addWidget(message_container, 0, Qt.AlignTop)  # 不分配权重，让它根据内容调整
            layout.addWidget(avatar, 0, Qt.AlignTop)  # 头像固定大小
        else:
            layout.addWidget(avatar, 0, Qt.AlignTop)
            layout.addWidget(message_container, 2, Qt.AlignTop)
            layout.addStretch(1)

        self.setLayout(layout)

        # 延迟调整高度，确保组件完全初始化
        QTimer.singleShot(10, self.adjust_height)

        # 初始时隐藏滚动条
        self.hide_scrollbars(None)

    def show_scrollbars(self, event):
        self.message_edit.verticalScrollBar().setVisible(True)
        self.message_edit.horizontalScrollBar().setVisible(True)

    def hide_scrollbars(self, event):
        self.message_edit.verticalScrollBar().setVisible(False)
        self.message_edit.horizontalScrollBar().setVisible(False)

    def adjust_height(self):
        """根据内容自动调整QTextEdit高度"""
        def adjust_single_edit(edit_widget):
            if not edit_widget:
                return

            # 获取文档的理想高度
            doc = edit_widget.document()
            doc.setTextWidth(edit_widget.width())
            doc_height = doc.size().height()

            # 计算合适的高度 - 减少额外空间
            margins = edit_widget.contentsMargins()
            extra_height = margins.top() + margins.bottom() + 4  # 减少额外空间，从8改为4
            ideal_height = int(doc_height + extra_height)

            # 设置最小和最大高度限制
            min_height = MIN_HEIGHT
            max_height = MAX_HEIGHT
            final_height = max(min_height, min(ideal_height, max_height))

            edit_widget.setFixedHeight(final_height)

        # 调整主消息区域高度
        adjust_single_edit(self.message_edit)

        # 更新父级组件
        self.updateGeometry()

    def html_text(self, text):
            html = mistune.html(text)
            html = f"""
            <html>
            <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 14px;
                    background-color: #F9FAFB;
                    color: #333;
                }}
                pre code {{
                    background-color: #f4f4f4;
                    border: 1px solid #ccc;
                    padding: 5px;
                    display: block;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    font-family: Consolas, monospace;
                    color: #c7254e;
                }}
            </style>
            </head>
            <body>{html}</body>
            </html>
            """
            return html

    def append_text(self, text):
        """追加文本（用于流式输出）"""
        self.current_message += text
        html = self.html_text(self.current_message)
        self.message_edit.setHtml(html)
        self.message_edit.moveCursor(QTextCursor.End)
        # 调整高度
        self.adjust_height()

    def resizeEvent(self, event):
        """重写resizeEvent以确保在窗口大小变化时重新计算宽度"""
        super().resizeEvent(event)
        # 延迟调整，确保布局已经完成
        QTimer.singleShot(10, self.adjust_width)

    def adjust_width(self):
        """根据内容调整消息气泡的宽度"""
        if not self.is_user:
            return  # 只调整用户消息的宽度

        # 获取文档的理想宽度
        doc = self.message_edit.document()
        doc_width = doc.idealWidth()
        
        # 考虑边距和其他因素，计算消息气泡的理想宽度
        margins = self.message_edit.contentsMargins()
        bubble_margins = self.layout().contentsMargins()
        extra_width = margins.left() + margins.right() + bubble_margins.left() + bubble_margins.right() + 40  # 额外空间
        
        # 计算最终宽度，确保不超过最大宽度
        ideal_width = int(doc_width + extra_width)
        final_width = min(ideal_width, USER_MAX_WIDTH)
        
        # 设置消息容器的宽度
        message_container = self.layout().itemAt(1).widget()
        message_container.setFixedWidth(final_width)
        
        # 更新几何形状
        
        self.updateGeometry()
        self.adjust_height()