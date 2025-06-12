import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
from langchain_ollama import ChatOllama
from langchain.schema.messages import HumanMessage

llm = ChatOllama(model="qwen2.5:7b", streaming=True)


class ChatBot():
    # 通过信号通知界面新加token
    update_text = pyqtSignal(str)
    gen_end = pyqtSignal(bool)

    def __init__(self) -> None:
        return 

    def connect(self, func_update, func_end):
        self.update_text.connect(func_update)
        self.gen_end.connect(func_end)

    def disconnect(self):
        self.update_text.disconnect()
        self.gen_end.disconnect()

    # 回答内容
    def answer(self, question: str):
        # 发送用户消息
        human_msg = HumanMessage(content=self.message)

        # 逐步处理 token 并发信号更新 GUI
        for chunk in llm.stream([human_msg]):
            token = chunk.content
            self.update_text.emit(token)
        
        self.gen_end.emit(True)



class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LangChain ChatOllama 流式输出")
        self.resize(600, 400)

        self.layout = QVBoxLayout()
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        self.send_button = QPushButton("发送消息")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.setLayout(self.layout)

    def send_message(self):
        self.output_area.clear()
        message = "如何学习人工智能？"

        bot = ChatBot()
        bot.update_text.connect(self.append_output)


    def append_output(self, text):
        self.output_area.moveCursor(self.output_area.textCursor().End)
        self.output_area.insertPlainText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())
