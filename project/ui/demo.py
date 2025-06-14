class ChatPanel:
    """聊天面板主类"""
    
    def __init__(self):
        self.is_ai_responding = False
        self.voice_recorder = VoiceRecorder()
        self.setup_voice_signals()
    
    def setup_voice_signals(self):
        """设置语音识别信号连接"""
        self.voice_recorder.text_recognized.connect(self.append_voice_text)
        self.voice_recorder.recording_started.connect(self.on_recording_started)
        self.voice_recorder.recording_stopped.connect(self.on_recording_stopped)
        self.voice_recorder.error_occurred.connect(self.on_voice_error)
    
    def create_right_panel(self):
        """创建右侧聊天面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # 顶部工具栏
        toolbar_widget = QWidget()
        toolbar_widget.setFixedHeight(60)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        toolbar.setContentsMargins(20, 12, 20, 12)

        # 状态指示器
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                padding: 6px 12px;
                border-radius: 12px;
                color: #5f6368;
                background-color: #f8f9fa;
            }
            """)

        toolbar.addWidget(self.status_label)
        toolbar.addStretch()
        toolbar_widget.setLayout(toolbar)

        # 聊天显示区域
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                border-radius: 3px;
                margin: 0px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #dadce0;
                border-radius: 3px;
                min-height: 20px;
                border: none;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #bdc1c6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
            }
            """)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(16)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_widget.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_widget)

        # 美化的输入区域
        input_container = QWidget()
        input_container.setFixedHeight(120)
        input_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafafa, stop:1 #ffffff);
                border-top: 1px solid #e8eaed;
                border-bottom: 1px solid #f0f0f0;
            }
            """)

        # 主输入布局
        main_input_layout = QVBoxLayout()
        main_input_layout.setContentsMargins(24, 16, 24, 16)
        main_input_layout.addStretch()
        
        # 输入控件的水平布局
        input_layout = QHBoxLayout()
        input_layout.setSpacing(16)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # 输入框容器
        input_wrapper = QWidget()
        input_wrapper.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e8eaed;
                border-radius: 26px;
            }
            QWidget:hover {
                border-color: #dadce0;
            }
            """)
        
        input_wrapper_layout = QHBoxLayout()
        input_wrapper_layout.setContentsMargins(16, 4, 16, 4)
        input_wrapper_layout.setSpacing(0)

        self.input_text = QTextEdit()
        self.input_text.setMaximumHeight(52)
        self.input_text.setMinimumHeight(52)
        self.input_text.setPlaceholderText("💬 输入您的消息...")
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: none;
                padding: 12px 4px;
                font-size: 14px;
                font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
                background-color: transparent;
                color: #3c4043;
                line-height: 1.5;
                selection-background-color: #1a73e8;
                selection-color: white;
            }
            QTextEdit:focus {
                background-color: transparent;
                outline: none;
            }
            """)

        input_wrapper_layout.addWidget(self.input_text)
        input_wrapper.setLayout(input_wrapper_layout)

        # 使用新的动画录音按钮
        self.record_btn = AnimatedRecordButton()
        self.record_btn.clicked.connect(self.toggle_recording)

        # 发送按钮
        self.send_btn = QPushButton("")
        self.send_btn.setFixedSize(52, 52)
        self.send_btn.setIcon(QIcon("./icon/send.png"))
        self.send_btn.setIconSize(QSize(24, 24))
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4285f4, stop:1 #1a73e8);
                color: white;
                border: none;
                border-radius: 26px;
                font-size: 14px;
                font-weight: 600;
                font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a95f5, stop:1 #1557b0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1557b0, stop:1 #1144a3);
            }
            QPushButton:disabled {
                background-color: #f1f3f4;
                color: #9aa0a6;
            }
            """)
        self.send_btn.clicked.connect(self.send_message)

        # 清除记录按钮
        clear_btn = QPushButton("")
        clear_btn.setFixedSize(52, 52)
        clear_btn.setIcon(QIcon("./icon/del1.png"))
        clear_btn.setIconSize(QSize(22, 22))
        clear_btn.setToolTip("清除聊天记录")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #5f6368;
                border: 1px solid #e8eaed;
                border-radius: 26px;
                font-size: 14px;
                font-weight: 500;
                font-family: "Microsoft YaHei UI", "PingFang SC", sans-serif;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border: 1px solid #dadce0;
                color: #d93025;
            }
            QPushButton:pressed {
                background-color: #f1f3f4;
            }
            """)
        clear_btn.clicked.connect(self.clear_current_chat)

        # 添加控件到布局
        input_layout.addWidget(input_wrapper, 1)
        input_layout.addWidget(self.record_btn)
        input_layout.addWidget(self.send_btn)
        input_layout.addWidget(clear_btn)

        main_input_layout.addLayout(input_layout)
        main_input_layout.addStretch()
        input_container.setLayout(main_input_layout)

        # 组装右侧面板
        right_layout.addWidget(toolbar_widget)
        right_layout.addWidget(self.chat_scroll, 1)
        right_layout.addWidget(input_container)
        right_widget.setLayout(right_layout)

        # 绑定回车键发送
        self.input_text.keyPressEvent = self.input_key_press_event

        # 右侧面板整体样式
        right_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
            """)

        return right_widget

    def toggle_recording(self):
        """切换录音状态"""
        if not self.voice_recorder.is_recording:
            self.voice_recorder.start_recording()
        else:
            self.voice_recorder.stop_recording()

    def on_recording_started(self):
        """录音开始回调"""
        self.record_btn.start_recording_animation()
        self.status_label.setText("🎙️ 正在录音...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                padding: 6px 12px;
                border-radius: 12px;
                color: #ea4335;
                background-color: #fef7f7;
                border: 1px solid #fce8e6;
            }
            """)

    def on_recording_stopped(self):
        """录音停止回调"""
        self.record_btn.stop_recording_animation()
        self.status_label.setText("")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                padding: 6px 12px;
                border-radius: 12px;
                color: #5f6368;
                background-color: #f8f9fa;
            }
            """)

    def on_voice_error(self, error_msg):
        """语音错误回调"""
        print(f"语音错误: {error_msg}")
        self.status_label.setText("❌ 语音识别出错")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
                padding: 6px 12px;
                border-radius: 12px;
                color: #d93025;
                background-color: #fce8e6;
                border: 1px solid #fce8e6;
            }
            """)

    def append_voice_text(self, text):
        """将识别的文本追加到输入框"""
        current_text = self.input_text.toPlainText()
        if current_text and not current_text.endswith(' '):
            new_text = current_text + " " + text
        else:
            new_text = current_text + text
            
        self.input_text.setPlainText(new_text)
        
        # 将光标移到最后
        cursor = self.input_text.textCursor()
        cursor.movePosition(cursor.End)
        self.input_text.setTextCursor(cursor)

    def input_key_press_event(self, event):
        """处理输入框按键事件"""
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            if not self.is_ai_responding:
                self.send_message()
        else:
            QTextEdit.keyPressEvent(self.input_text, event)

    def send_message(self):
        """发送消息 - 需要实现"""
        pass

    def clear_current_chat(self):
        """清除当前聊天 - 需要实现"""
        pass