import sys
import time
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QProgressBar, QMainWindow, QPushButton, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QPalette
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
from chat_window1 import ChatInterface

class LoadingWorker(QThread):
    """加载工作线程"""
    progress_updated = pyqtSignal(int)
    loading_finished = pyqtSignal()
    
    def run(self):
        """模拟加载过程"""
        for i in range(101):
            time.sleep(0.05)  # 模拟加载时间
            self.progress_updated.emit(i)
        self.loading_finished.emit()

class LoadingScreen(QWidget):
    """加载界面类"""
    
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.background_pixmap = None
        self.loadBackground()
        self.initUI()
        self.startLoading()
    
    def loadBackground(self):
        """加载背景图片"""
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, './icon/load.png')
        
        if os.path.exists(image_path):
            self.background_pixmap = QPixmap(image_path)
            print(f"背景图片加载成功: {image_path}")
        else:
            print(f"背景图片未找到: {image_path}")
            self.background_pixmap = None
    
    def paintEvent(self, event):
        """绘制背景图片"""
        painter = QPainter(self)
        
        if self.background_pixmap:
            # 获取界面尺寸
            widget_size = self.size()
            
            # 直接将图片缩放到界面大小，填充整个界面
            scaled_pixmap = self.background_pixmap.scaled(
                widget_size.width(), 
                widget_size.height(), 
                Qt.IgnoreAspectRatio,  # 忽略宽高比，完全填充界面
                Qt.SmoothTransformation
            )
            
            # 绘制填充整个界面的图片
            painter.drawPixmap(0, 0, scaled_pixmap)
            
            # 添加半透明遮罩以确保文字可见
            painter.fillRect(self.rect(), QColor(0, 0, 0, 50))  # 半透明黑色遮罩
        else:
            # 如果没有背景图片，使用原来的渐变背景
            painter.fillRect(self.rect(), QColor(102, 126, 234))  # 备用背景色
        
        super().paintEvent(event)
    
    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle('智能问答系统 - 加载中...')
        self.setFixedSize(1000, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 居中显示
        self.center()
        
        # 由于使用背景图片，移除原来的渐变背景样式
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        
        # 标题标签
        self.title_label = QLabel('智能问答系统')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                font-family: '微软雅黑', 'Microsoft YaHei';
                background: transparent;
                padding: 20px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            }
        """)
        
        # 副标题
        self.subtitle_label = QLabel('AI-Powered Question Answering System')
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 18px;
                font-family: '微软雅黑', 'Microsoft YaHei';
                background: transparent;
                padding: 10px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }
        """)
        
        # 创建进度条容器
        progress_container = QWidget()
        progress_container.setFixedSize(500, 80)
        progress_container.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.15);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.4);
            }
        """)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 15px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                color: white;
                background: rgba(255, 255, 255, 0.2);
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }
            QProgressBar::chunk {
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6b6b, stop:0.5 #feca57, stop:1 #48dbfb);
            }
        """)
        
        # 进度条布局
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.setContentsMargins(20, 25, 20, 25)
        
        # 状态标签
        self.status_label = QLabel('正在初始化系统...')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.95);
                font-size: 16px;
                font-family: '微软雅黑', 'Microsoft YaHei';
                background: transparent;
                padding: 10px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }
        """)
        
        # 版权信息
        self.copyright_label = QLabel('© 2024 智能问答系统 - 版本 1.0')
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.copyright_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 12px;
                font-family: '微软雅黑', 'Microsoft YaHei';
                background: transparent;
                padding: 5px;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }
        """)
        
        # 添加组件到主布局
        main_layout.addStretch()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addSpacing(50)
        main_layout.addWidget(progress_container, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        main_layout.addStretch()
        main_layout.addWidget(self.copyright_label)
        
        self.setLayout(main_layout)
    
    def center(self):
        """将窗口居中显示"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def startLoading(self):
        """开始加载过程"""
        self.worker = LoadingWorker()
        self.worker.progress_updated.connect(self.updateProgress)
        self.worker.loading_finished.connect(self.onLoadingFinished)
        self.worker.start()
    
    def updateProgress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
        # 根据进度更新状态文本
        if value < 20:
            self.status_label.setText('正在初始化系统...')
        elif value < 40:
            self.status_label.setText('正在加载AI模型...')
        elif value < 60:
            self.status_label.setText('正在配置问答引擎...')
        elif value < 80:
            self.status_label.setText('正在连接知识库...')
        elif value < 100:
            self.status_label.setText('正在完成最后的配置...')
        else:
            self.status_label.setText('加载完成！')
    
    def onLoadingFinished(self):
        """加载完成后的处理"""
        QTimer.singleShot(500, self.showMainWindow)
    
    def showMainWindow(self):
        """显示主窗口"""
        self.main_window = ChatInterface()
        self.main_window.show()
        self.close()



def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName('智能问答系统')
    app.setApplicationVersion('1.0')
    
    # 创建并显示加载界面
    loading_screen = LoadingScreen()
    loading_screen.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()