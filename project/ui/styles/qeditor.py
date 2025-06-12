
# 滚动条设置margin可能会消失
scrollbar_style = """
    /* 垂直滚动条整体样式 */
    QScrollBar:vertical {
        border: none;
        background: #F9FAFB;
        width: 2px;
    }

    /* 水平滚动条整体样式 */
    QScrollBar:horizontal {
        border: none;
        background: #F9FAFB;
        height: 8px;
        margin: 0px;
    }

    /* 垂直滑块样式 */
    QScrollBar::handle:vertical {
        background: #d1d5ff;   
        border-radius: 4px;
        min-height: 20px;
        max-height:80px;
    }

    /* 水平滑块样式 */
    QScrollBar::handle:horizontal {
        background: #d1d5ff;
        border-radius: 4px;
        min-width: 20px;
    }

    /* 滑块悬停样式 */
    QScrollBar::handle:vertical:hover {
        background: #9ca3af;
    }

    QScrollBar::handle:horizontal:hover {
        background: #9ca3af;
    }

    /* 滑块按下样式 */
    QScrollBar::handle:vertical:pressed {
        background: #6B7280;
    }

    QScrollBar::handle:horizontal:pressed {
        background: #6B7280;
    }
"""


### QMenu是右键菜单
qeditor_qss = """
    QTextEdit {
        background: transparent;
        color: #374151;
        font-size: 14px;
        font-family: "SF Pro Text", "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.6;
        font-weight: 400;
        border: none;
        margin: 0px;
        selection-background-color: #bfdbfe;
        selection-color: balck;
    
    }
    QMenu {
        background-color: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 6px;
    }
    QMenu::item {
        background-color: transparent;
        padding: 10px 18px;
        margin: 3px;
        border-radius: 8px;
        color: #374151;
        font-size: 13px;
        font-weight: 500;
    }
    QMenu::item:hover {
        background-color: #bfdbfe;
        color: #111827;
    }
    QMenu::item:selected {
        background-color: #bfdbfe;
        color: #111827;
    }
"""