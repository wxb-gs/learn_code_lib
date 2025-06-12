import mistune
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
from langchain_ollama import ChatOllama
from langchain.schema.messages import HumanMessage
# import markdown


# 初始化 LLM
llm = ChatOllama(model="qwen2.5:7b", streaming=True)


class ChatBot(QObject):
    update_text = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def connect(self, func_update):
        self.update_text.connect(func_update)

    def disconnect(self):
        self.update_text.disconnect()

    def answer(self, question: str):
        human_msg = HumanMessage(content=question)

        for chunk in llm.stream([human_msg]):
            token = chunk.content
            self.update_text.emit(token)


class ChatBotThread(QThread):
    finished = pyqtSignal()

    def __init__(self, question: str, bot: ChatBot):
        super().__init__()
        self.question = question
        self.bot = bot

    def run(self):
        self.bot.answer(self.question)
        self.finished.emit()


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LangChain ChatOllama 流式输出")
        self.resize(700, 500)

        self.layout = QVBoxLayout()
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                background-color: #fefefe;
                padding: 10px;
            }
        """)
        self.layout.addWidget(self.output_area)

        self.send_button = QPushButton("发送消息")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)
        self.markdown_buffer = ""

    def thread_finished(self):
        print("线程执行完毕")
        # 可在这里处理最终格式化、滚动条等

    def send_message(self):
        self.output_area.clear()
        self.markdown_buffer = ""  # 清空缓存
        message = "如何学习人工智能？"

        bot = ChatBot()
        bot.update_text.connect(self.append_output)

        bot_thread = ChatBotThread(message, bot)
        self.bot_thread = bot_thread
        bot_thread.finished.connect(self.thread_finished)
        bot_thread.start()

    def append_output(self, text):
        self.markdown_buffer += text
        html = mistune.html(self.markdown_buffer)
        # 你可以自定义 HTML 结构和样式
        html = f"""
        <html>
        <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
                background-color: #ffffff;
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
        self.output_area.setHtml(html)
        self.output_area.moveCursor(QTextCursor.End)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())