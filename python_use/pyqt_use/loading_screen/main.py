from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QSizePolicy,
    QDesktopWidget,
    QGraphicsDropShadowEffect,
    QSpacerItem,
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QBasicTimer
import sys
from time import sleep

from loadwin_ui import Ui_loadwin  # 根据自己的目录设置文件路径
from Ui_mainwin import Ui_mainwin  # 根据自己的目录设置文件路径


class LoadWin(QWidget, Ui_loadwin):  # 启动画面类
    def __init__(self):
        super(LoadWin, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("加载界面")
        screen = QDesktopWidget().screenGeometry()
        # 设置窗口为屏幕的60%宽、40%高
        self.resize(int(screen.width() * 0.5), int(screen.height() * 0.6))
        # 保持宽高比缩放（根据实际需求选择）
        self.setMinimumSize(400, 300)  # 最小尺寸限制
        # self.setWindowFlags(Qt.FramelessWindowHint)  # 保持无边框设置[9](@ref)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.label_logo.setStyleSheet("background: transparent;")
        # 设置启动窗背景色和进度信息的字体样式等
        self.setStyleSheet(
            """
            #label_info {
                color: red;
                font-family: '微软雅黑';
                font-size: 18px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
            #progressBar {
                min-height: 15px;
                max-height: 20px;
                border-radius: 8px;
            }
        """
        )
        # 进度条样式（添加渐变和动画效果）
        self.progressBar.setStyleSheet(
            """
            QProgressBar {
                margin: 0 10px;
                border: 2px solid #3A3A3A;
                border-radius: 8px;
                background: #2D2D2D;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #00FF88, 
                    stop:1 #00AAFF
                );
                border-radius: 6px;
                margin: 1px;
                border: 1px solid rgba(255,255,255,30%);
            }
        """
        )
        # 添加进度动画
        self.progressBar.setFormat("%p%")  # 显示百分比[10]
        self.gridLayout.setContentsMargins(0, 0, 0, 10)
        self.gridLayout.setVerticalSpacing(5)  # 控件垂直间距
        # self.label_logo.setSizePolicy(
        #     QSizePolicy.Expanding, QSizePolicy.Expanding  # 双方向自适应[7](@ref)
        # )
        self.progressBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # 加载图片
        self.label_logo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        pix = QPixmap("./load_logo.png")
        # target_height = int(self.height() * 0.5)  # 动态高度
        # target_width = int(self.width() * 0.95)
        scaled_pix = pix.scaled(
            self.width(),
            self.label_logo.height(),
            Qt.KeepAspectRatioByExpanding,  # 扩展模式保持比例
            # Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation,
        )
        self.label_logo.setPixmap(scaled_pix)
        self.label_logo.setAlignment(Qt.AlignCenter)
        # 图片添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.black)
        shadow.setOffset(3, 3)
        self.label_logo.setGraphicsEffect(shadow)

        # 进度，定时
        self.timer = QBasicTimer()  # 定时器对象
        self.maxNum = 20
        self.step = 0  # 进度值
        self.proess_run()
        self.ret = None

    # 第一步执行流程
    def proess_run(self):  # 启动进度线程
        self.cal = LoadThread()  # 线程对象
        # 绑定接受信号的槽函数，当具体节点时，就会触发发送对应消息
        self.cal.part_signal.connect(self.process_set_max)
        self.cal.data_signal.connect(self.show_step)
        self.cal.show_signal.connect(self.valid_show_main_win)
        self.cal.start()  # 调用线程run

    def process_set_max(self, max_value):
        self.maxNum = max_value

        # 第一次开始计时
        if self.step == 0:
            self.timer.start(50, self)  # 启动QBasicTimer, 每20毫秒调用一次回调函数
            self.label_info.setText("等待主页加载...")

    def show_step(self, str):
        self.label_info.setText(str)

    def valid_show_main_win(self):
        show_main_win()

    def timerEvent(self, *args, **kwargs):  # QBasicTimer的事件回调函数
        self.progressBar.setValue(self.step)  # 设置进度条的值
        if self.step < 100:
            self.step += 1
            self.step = min(self.step, self.maxNum)
        else:
            self.cal.set_ret()


class LoadThread(QThread):  # 自定义计算线程类 -----------
    part_signal = pyqtSignal(int)  # 进度信号
    data_signal = pyqtSignal(str)  # 数据传输信号
    show_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.ret = None

    # 启动线程
    def run(self):
        # 该消息发送后，启用process_set_part函数
        self.part_signal.emit(5)
        self.data_signal.emit("正在加载中。。。")
        sleep(1)
        self.part_signal.emit(20)
        self.data_signal.emit("加载大模型中。。。")
        sleep(2)
        self.part_signal.emit(40)
        self.data_signal.emit("加载数据库中。。。")
        sleep(3)
        self.data_signal.emit("加载嵌入模型中。。。")
        self.part_signal.emit(99)
        sleep(4)
        self.part_signal.emit(100)
        self.data_signal.emit("加载完毕, 即将跳转")
        sleep(1)

        while True:
            if self.ret:
                self.show_signal.emit()  # 加载完毕, 关闭页面，确保在主线程操作
                break

    # 建立标志
    def set_ret(self):
        self.ret = True


class MainWin(QWidget, Ui_mainwin):  # 主页界面类 -----------
    def __init__(self):
        super(MainWin, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("主界面")

    def set_data(self, mes="xxxxx"):
        self.lineEdit.setText(mes)


# 显示主界面
def show_main_win():
    w.close()
    zhu.set_data("xxxxx")
    zhu.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LoadWin()
    zhu = MainWin()
    w.show()
    sys.exit(app.exec())
