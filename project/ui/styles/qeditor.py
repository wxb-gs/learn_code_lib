# qeditor.py

# 滚动条设置margin可能会消失
scrollbar_style = """
/* 垂直滚动条整体样式 - 默认隐藏 */
QTextEdit QScrollBar:vertical {
    border: none;
    background: #F9FAFB; /* 修改背景色 */
    width: 0px;
    margin: 2px 0;
}

/* 水平滚动条整体样式 - 默认隐藏 */
QTextEdit QScrollBar:horizontal {
    border: none;
    background: #F9FAFB; /* 修改背景色 */
    height: 0px;
    margin: 0 2px;
}

/* 当QTextEdit被悬停时，显示滚动条 */
QTextEdit:hover QScrollBar:vertical {
    width: 5px;
}

QTextEdit:hover QScrollBar:horizontal {
    height: 6px;
}

/* 垂直滑块样式 */
QScrollBar::handle:vertical {
    background: rgba(156, 163, 175, 0.7);
    border-radius: 3px;
    min-height: 20px;
    margin: 0 1px;
}

/* 水平滑块样式 */
QScrollBar::handle:horizontal {
    background: rgba(156, 163, 175, 0.7);
    border-radius: 3px;
    min-width: 20px;
    margin: 1px 0;
}

/* 滑块悬停样式 */
QScrollBar::handle:vertical:hover {
    background: rgba(107, 114, 128, 0.9);
}

QScrollBar::handle:horizontal:hover {
    background: rgba(107, 114, 128, 0.9);
}

/* 滑块按下样式 */
QScrollBar::handle:vertical:pressed {
    background: rgba(75, 85, 99, 0.95);
}

QScrollBar::handle:horizontal:pressed {
    background: rgba(75, 85, 99, 0.95);
}

/* 滚动条轨道样式 */
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    height: 0px;
    width: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
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
        selection-color: black;
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