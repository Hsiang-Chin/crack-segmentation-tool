# -*- coding: utf-8 -*-

APP_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #eceff1;
}
QWidget {
    font-family: "Segoe UI", "Microsoft JhengHei UI", "PingFang TC", sans-serif;
    font-size: 12px;
    color: #212121;
}

/* ── Tab bar ── */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background-color: #cfd8dc;
    color: #37474f;
    padding: 7px 20px;
    border: 1px solid #b0bec5;
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    min-width: 120px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background-color: #1565c0;
    color: white;
    border-color: #1565c0;
}
QTabBar::tab:hover:!selected {
    background-color: #b0bec5;
}

/* ── Buttons ── */
QPushButton {
    background-color: #1976d2;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 5px 12px;
    font-weight: 600;
    font-size: 11px;
}
QPushButton:hover {
    background-color: #1565c0;
}
QPushButton:pressed {
    background-color: #0d47a1;
}
QPushButton:disabled {
    background-color: #b0bec5;
    color: #90a4ae;
}

/* ── Text inputs ── */
QLineEdit {
    background-color: white;
    border: 1.5px solid #90a4ae;
    border-radius: 4px;
    padding: 4px 8px;
    color: #212121;
    selection-background-color: #1976d2;
    selection-color: white;
}
QLineEdit:focus {
    border-color: #1976d2;
}
QLineEdit:read-only {
    background-color: #f5f5f5;
    color: #546e7a;
    border-style: dashed;
}

/* ── Spin / Double spin ── */
QSpinBox, QDoubleSpinBox {
    background-color: white;
    border: 1.5px solid #90a4ae;
    border-radius: 4px;
    padding: 2px 6px;
    color: #212121;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #1976d2;
}

/* ── Combo box ── */
QComboBox {
    background-color: white;
    border: 1.5px solid #90a4ae;
    border-radius: 4px;
    padding: 3px 8px;
    color: #212121;
}
QComboBox::drop-down {
    border: none;
    padding-right: 4px;
}
QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #90a4ae;
    selection-background-color: #1976d2;
    selection-color: white;
    color: #212121;
}

/* ── List widget ── */
QListWidget {
    background-color: white;
    border: 1.5px solid #90a4ae;
    border-radius: 4px;
    color: #212121;
}
QListWidget::item {
    padding: 3px 6px;
}
QListWidget::item:selected {
    background-color: #1976d2;
    color: white;
}
QListWidget::item:hover {
    background-color: #e3f2fd;
}

/* ── Progress bar ── */
QProgressBar {
    background-color: #e0e0e0;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #212121;
    font-size: 10px;
    min-height: 14px;
}
QProgressBar::chunk {
    background-color: #43a047;
    border-radius: 4px;
}

/* ── Labels ── */
QLabel {
    color: #212121;
    background-color: transparent;
}

/* ── Status bar ── */
QStatusBar {
    background-color: #e8eaf6;
    color: #212121;
    border-top: 1px solid #c5cae9;
    font-size: 11px;
}

/* ── LCD Number ── */
QLCDNumber {
    background-color: #263238;
    color: #76ff03;
    border: 1px solid #455a64;
    border-radius: 3px;
}

/* ── Separators ── */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #b0bec5;
}

/* ── Menu bar ── */
QMenuBar {
    background-color: #1565c0;
    color: white;
}

/* ── Scrollbar ── */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background-color: #90a4ae;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background-color: #607d8b; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background-color: #90a4ae;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background-color: #607d8b; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
"""
