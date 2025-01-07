"""
Module containing style definitions for the GUI.
"""

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #1e1e1e;
    color: #ffffff;
}

QTableWidget {
    background-color: #2d2d2d;
    color: #ffffff;
    gridline-color: #3d3d3d;
    selection-background-color: #2196f3;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #2196f3;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 5px;
    border: 1px solid #3d3d3d;
}

QPushButton {
    background-color: #2196f3;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #1976d2;
}

QPushButton:pressed {
    background-color: #0d47a1;
}

QLineEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    padding: 8px;
    border-radius: 4px;
}

QLineEdit:focus {
    border: 1px solid #2196f3;
}

QLabel {
    color: #ffffff;
}

QMenu {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
}

QMenu::item {
    padding: 5px 20px;
}

QMenu::item:selected {
    background-color: #2196f3;
}

QMessageBox {
    background-color: #1e1e1e;
    color: #ffffff;
}

QDialog QLabel {
    color: #ffffff;
}
"""
