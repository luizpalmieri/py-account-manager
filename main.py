import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QTableWidget, QPushButton, QDialog, QFormLayout,
                           QLineEdit, QMessageBox, QTableWidgetItem, QHeaderView,
                           QMenu, QStyle, QHBoxLayout, QLabel, QFrame)
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QAction, QIcon, QColor, QPalette
import pyotp
from database import Database
import hashlib
import time

DARK_STYLE = """
QMainWindow, QDialog, QMessageBox {
    background-color: #1e1e1e;
    color: #ffffff;
}
QTableWidget {
    background-color: #2d2d2d;
    color: #ffffff;
    gridline-color: #3d3d3d;
    border: none;
    border-radius: 8px;
}
QTableWidget::item {
    padding: 8px;
}
QTableWidget::item:selected {
    background-color: #0d47a1;
    color: #ffffff;
}
QHeaderView::section {
    background-color: #2d2d2d;
    color: #ffffff;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #3d3d3d;
}
QLineEdit {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
    padding: 8px;
    border-radius: 4px;
}
QLabel {
    color: #ffffff;
}
QMenu {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #3d3d3d;
}
QMenu::item:selected {
    background-color: #0d47a1;
}
"""

class CustomTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        menu = QMenu()
        
        copy_cell = menu.addAction("Copy Value")
        copy_cell_raw = menu.addAction("Copy Raw Value")
        copy_row = menu.addAction("Copy Row (Tab separated)")
        copy_row_csv = menu.addAction("Copy Row (CSV format)")
        menu.addSeparator()
        delete_row = menu.addAction("Delete")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action == copy_cell:
            self.copy_cell_content()
        elif action == copy_cell_raw:
            self.copy_cell_content(raw=True)
        elif action == copy_row:
            self.copy_row_content(format="tab")
        elif action == copy_row_csv:
            self.copy_row_content(format="csv")
        elif action == delete_row:
            self.parent().parent().delete_account(self.currentRow())
            
    def copy_cell_content(self, raw=False):
        current_item = self.currentItem()
        if current_item:
            if raw and current_item.column() == 3:  # OTP column
                # Copy only the OTP digits
                text = current_item.text().split()[0]
                QApplication.clipboard().setText(text)
            else:
                # For password column, get the actual password
                if current_item.column() == 2:  # Password column
                    text = current_item.data(Qt.ItemDataRole.UserRole)
                else:
                    text = current_item.text()
                QApplication.clipboard().setText(text)
            
    def copy_row_content(self, format="tab"):
        current_row = self.currentRow()
        if current_row >= 0:
            row_data = []
            for col in range(self.columnCount()):
                item = self.item(current_row, col)
                if item:
                    if col == 2:  # Password column
                        value = item.data(Qt.ItemDataRole.UserRole)
                    elif col == 3:  # OTP column
                        value = item.text().split()[0] if item.text() != 'N/A' else 'N/A'
                    else:
                        value = item.text()
                    row_data.append(value)
            
            if format == "csv":
                # Escape commas and quotes in values
                escaped_data = []
                for value in row_data:
                    if ',' in value or '"' in value:
                        value = f'"{value.replace('"', '""')}"'
                    escaped_data.append(value)
                text = ','.join(escaped_data)
            else:  # tab format
                text = '\t'.join(row_data)
                
            QApplication.clipboard().setText(text)

class StyledButton(QPushButton):
    def __init__(self, text, icon_name=None):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3880;
            }
        """)
        if icon_name:
            self.setIcon(self.style().standardIcon(icon_name))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login - Password Manager')
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel('Welcome to Password Manager')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #2196f3; margin-bottom: 20px;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('Enter your master password')
        form_layout.addRow('Master Password:', self.password_input)
        layout.addLayout(form_layout)
        
        login_button = StyledButton('Login')
        login_button.clicked.connect(self.accept)
        layout.addWidget(login_button)
        
        self.setLayout(layout)
        self.setMinimumWidth(400)

class AddAccountDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Add New Account')
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.otp_input = QLineEdit()
        
        self.name_input.setPlaceholderText('e.g., Gmail, Twitter')
        self.username_input.setPlaceholderText('Your username or email')
        self.password_input.setPlaceholderText('Your password')
        self.otp_input.setPlaceholderText('Optional: OTP secret key')
        
        form_layout.addRow('Account Name:', self.name_input)
        form_layout.addRow('Username:', self.username_input)
        form_layout.addRow('Password:', self.password_input)
        form_layout.addRow('OTP Secret:', self.otp_input)
        
        layout.addLayout(form_layout)
        
        buttons_layout = QHBoxLayout()
        save_button = StyledButton('Save')
        cancel_button = QPushButton('Cancel')
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
        """)
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        self.setMinimumWidth(400)

class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.authenticate()
        
    def authenticate(self):
        while True:
            dialog = LoginDialog()
            if dialog.exec():
                master_password = dialog.password_input.text()
                master_password_hash = hashlib.sha256(master_password.encode()).hexdigest()
                try:
                    self.setup_ui(master_password_hash)
                    break
                except ValueError as e:
                    QMessageBox.critical(self, 'Error', 'Invalid master password. Please try again.')
            else:
                sys.exit()
            
    def setup_ui(self, master_password_hash):
        self.setWindowTitle('Password Manager')
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(DARK_STYLE)
        
        # Initialize database
        self.db = Database(master_password_hash)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('Password Manager')
        title.setStyleSheet('font-size: 24px; font-weight: bold; color: #2196f3;')
        header_layout.addWidget(title)
        header_layout.addStretch()
        add_button = StyledButton('Add Account', QStyle.StandardPixmap.SP_FileIcon)
        header_layout.addWidget(add_button)
        layout.addLayout(header_layout)
        
        # Table
        self.table = CustomTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Account', 'Username', 'Password', 'OTP'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Prevent direct editing of password and OTP cells
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Connect signals
        add_button.clicked.connect(self.add_account)
        self.table.itemDoubleClicked.connect(self.handle_item_double_click)
        
        # Setup OTP timer
        self.otp_timer = QTimer()
        self.otp_timer.timeout.connect(self.update_otp_codes)
        self.otp_timer.start(1000)  # Update every second
        
        self.load_accounts()

    def handle_item_double_click(self, item):
        row = item.row()
        col = item.column()
        
        if col in [0, 1]:  # Only allow editing account name and username
            dialog = QDialog(self)
            dialog.setWindowTitle('Edit Value')
            dialog.setStyleSheet(DARK_STYLE)
            layout = QVBoxLayout(dialog)
            
            input_field = QLineEdit()
            input_field.setText(item.text())
            layout.addWidget(input_field)
            
            buttons = QHBoxLayout()
            save_btn = StyledButton('Save')
            cancel_btn = QPushButton('Cancel')
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
            """)
            
            buttons.addWidget(cancel_btn)
            buttons.addWidget(save_btn)
            layout.addLayout(buttons)
            
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            if dialog.exec():
                new_value = input_field.text()
                item.setText(new_value)
                
                # Update database
                account = self.db.get_accounts()[row]
                if col == 0:
                    self.db.update_account(account['id'], new_value, account['username'], 
                                         account['password'], account['otp_secret'])
                else:
                    self.db.update_account(account['id'], account['name'], new_value,
                                         account['password'], account['otp_secret'])
        
        elif col == 2:  # Password column
            dialog = QDialog(self)
            dialog.setWindowTitle('Edit Password')
            dialog.setStyleSheet(DARK_STYLE)
            layout = QVBoxLayout(dialog)
            
            # Current password field
            current_layout = QHBoxLayout()
            current_password = QLineEdit()
            current_password.setEchoMode(QLineEdit.EchoMode.Password)
            current_password.setText(item.data(Qt.ItemDataRole.UserRole))
            current_password.setPlaceholderText('Current Password')
            
            show_current = QPushButton()
            show_current.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
            show_current.setCheckable(True)
            show_current.clicked.connect(lambda: self.toggle_password_visibility(current_password))
            
            current_layout.addWidget(current_password)
            current_layout.addWidget(show_current)
            layout.addLayout(current_layout)
            
            # New password field
            new_layout = QHBoxLayout()
            new_password = QLineEdit()
            new_password.setEchoMode(QLineEdit.EchoMode.Password)
            new_password.setPlaceholderText('New Password')
            
            show_new = QPushButton()
            show_new.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
            show_new.setCheckable(True)
            show_new.clicked.connect(lambda: self.toggle_password_visibility(new_password))
            
            new_layout.addWidget(new_password)
            new_layout.addWidget(show_new)
            layout.addLayout(new_layout)
            
            buttons = QHBoxLayout()
            save_btn = StyledButton('Save')
            cancel_btn = QPushButton('Cancel')
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
            """)
            
            buttons.addWidget(cancel_btn)
            buttons.addWidget(save_btn)
            layout.addLayout(buttons)
            
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)
            
            if dialog.exec():
                new_value = new_password.text()
                if new_value:  # Only update if new password is not empty
                    item.setData(Qt.ItemDataRole.UserRole, new_value)
                    item.setText('••••••••')
                    
                    # Update database
                    account = self.db.get_accounts()[row]
                    self.db.update_account(account['id'], account['name'], account['username'],
                                         new_value, account['otp_secret'])

    def toggle_password_visibility(self, password_field):
        if password_field.echoMode() == QLineEdit.EchoMode.Password:
            password_field.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            password_field.setEchoMode(QLineEdit.EchoMode.Password)

    def load_accounts(self):
        accounts = self.db.get_accounts()
        self.table.setRowCount(len(accounts))
        
        for row, account in enumerate(accounts):
            name_item = QTableWidgetItem(account['name'])
            name_item.setForeground(QColor('#ffffff'))
            self.table.setItem(row, 0, name_item)
            
            username_item = QTableWidgetItem(account['username'])
            username_item.setForeground(QColor('#ffffff'))
            self.table.setItem(row, 1, username_item)
            
            password_item = QTableWidgetItem('••••••••')
            password_item.setData(Qt.ItemDataRole.UserRole, account['password'])
            password_item.setForeground(QColor('#ffffff'))
            self.table.setItem(row, 2, password_item)
            
            if account['otp_secret']:
                totp = pyotp.TOTP(account['otp_secret'])
                otp_code = totp.now()
                remaining = 30 - (int(time.time()) % 30)
                otp_item = QTableWidgetItem(f'{otp_code}')
                otp_item.setData(Qt.ItemDataRole.UserRole, account['otp_secret'])
                otp_item.setForeground(QColor('#ffffff'))
                
                # Add remaining time as tooltip
                otp_item.setToolTip(f'Refreshes in {remaining} seconds')
                
                self.table.setItem(row, 3, otp_item)
            else:
                otp_item = QTableWidgetItem('N/A')
                otp_item.setForeground(QColor('#808080'))
                self.table.setItem(row, 3, otp_item)
            
    def update_otp_codes(self):
        for row in range(self.table.rowCount()):
            otp_item = self.table.item(row, 3)
            if otp_item and otp_item.text() != 'N/A':
                otp_secret = otp_item.data(Qt.ItemDataRole.UserRole)
                if otp_secret:
                    totp = pyotp.TOTP(otp_secret)
                    otp_code = totp.now()
                    remaining = 30 - (int(time.time()) % 30)
                    
                    # Update only the OTP code, keep it clean
                    otp_item.setText(f'{otp_code}')
                    otp_item.setToolTip(f'Refreshes in {remaining} seconds')
                    
                    # Visual feedback when OTP refreshes
                    if remaining == 30:
                        otp_item.setBackground(QColor('#1565c0'))
                        QTimer.singleShot(1000, lambda item=otp_item: item.setBackground(QColor('#2d2d2d')))

    def add_account(self):
        dialog = AddAccountDialog()
        if dialog.exec():
            name = dialog.name_input.text()
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            otp_secret = dialog.otp_input.text()
            
            if name and username and password:
                self.db.add_account(name, username, password, otp_secret)
                self.load_accounts()
            else:
                QMessageBox.warning(self, 'Error', 'Please fill in all required fields')
                
    def delete_account(self, row):
        account_id = self.db.get_accounts()[row]['id']
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                   'Are you sure you want to delete this account?',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_account(account_id)
            self.load_accounts()
            
    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = PasswordManager()
    window.show()
    sys.exit(app.exec())
