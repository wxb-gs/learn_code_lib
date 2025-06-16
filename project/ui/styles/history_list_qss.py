                # background-color: #FAFAFA;
history_list_styles = """
            QListWidget {
                border: none;
                border-top: 1px solid #e8eaed;
                padding: 8px 0px;
                font-family: "Microsoft YaHei UI", "PingFang SC", "SF Pro Display", sans-serif;
                outline: none;
            }

            QListWidget::item {
                background-color: transparent;
                border: 1px solid #e8eaed;
                border-radius: 8px;
                padding: 12px 16px;
                margin: 2px 8px;
                font-size: 14px;
                color: #3c4043;
                min-height: 20px;
            }

            QListWidget::item:hover {
                background-color: #EBEDEE;
            }

            QListWidget::item:selected {
                background-color: #e8f0fe;
                color: #1a73e8;
                font-weight: 500;
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
            """