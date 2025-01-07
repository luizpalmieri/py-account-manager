"""
Main window implementation for the password manager GUI.
"""
import sys
import hashlib
import pyotp
from typing import Optional, Dict
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QApplication,
                              QMessageBox, QMenu, QStyle, QHBoxLayout, QLabel)
from PySide6.QtCore import QTimer, Qt

from src.database.database_manager import DatabaseManager
from src.gui.widgets import StyledButton, CustomTableWidget, LoginDialog, AddAccountDialog
from src.gui.styles import DARK_STYLE

class PasswordManager(QMainWindow):
    """Main window class for the password manager application."""
    
    def __init__(self):
        """Initialize the password manager window."""
        super().__init__()
        self.db: Optional[DatabaseManager] = None
        self.authenticate()
        
    def authenticate(self) -> None:
        """Handle user authentication with master password."""
        while True:
            dialog = LoginDialog()
            if dialog.exec():
                master_password = dialog.password_input.text()
                master_password_hash = hashlib.sha256(master_password.encode()).hexdigest()
                try:
                    self.setup_ui(master_password_hash)
                    break
                except ValueError:
                    QMessageBox.critical(self, 'Error', 'Invalid master password. Please try again.')
            else:
                sys.exit()
            
    def setup_ui(self, master_password_hash: str) -> None:
        """
        Setup the main window UI.
        
        Args:
            master_password_hash (str): Hash of the master password
        """
        self.setWindowTitle('Password Manager')
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(DARK_STYLE)
        
        # Initialize database
        self.db = DatabaseManager(master_password_hash)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self._setup_header(layout)
        
        # Table
        self.table = CustomTableWidget()
        self._setup_table()
        layout.addWidget(self.table)
        
        # Load accounts and start OTP timer
        self.load_accounts()
        self._setup_otp_timer()

    def _setup_header(self, layout: QVBoxLayout) -> None:
        """Setup the header section with title and add button."""
        header_layout = QHBoxLayout()
        
        title = QLabel('Password Manager')
        title.setStyleSheet('font-size: 24px; font-weight: bold; color: #2196f3;')
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_button = StyledButton('Add Account', QStyle.SP_FileIcon)
        add_button.clicked.connect(self.add_account)
        header_layout.addWidget(add_button)
        
        layout.addLayout(header_layout)

    def _setup_table(self) -> None:
        """Setup the accounts table."""
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Account', 'Username', 'Password', 'OTP'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(CustomTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(CustomTableWidget.SelectRows)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

    def _setup_otp_timer(self) -> None:
        """Setup timer for OTP updates."""
        self.otp_timer = QTimer()
        self.otp_timer.timeout.connect(self.update_otp_codes)
        self.otp_timer.start(1000)

    def _show_context_menu(self, position) -> None:
        """
        Show context menu for table items.
        
        Args:
            position: Position where to show the menu
        """
        menu = QMenu()
        copy_value = menu.addAction("Copy Value")
        copy_raw = menu.addAction("Copy Raw Value")
        copy_row_tab = menu.addAction("Copy Row (Tab separated)")
        copy_row_csv = menu.addAction("Copy Row (CSV format)")
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        if not action:
            return
            
        row = self.table.currentRow()
        col = self.table.currentColumn()
        
        if action == delete_action:
            self._handle_delete_action(row)
        elif action in (copy_value, copy_raw, copy_row_tab, copy_row_csv):
            self._handle_copy_action(action, row, col)

    def _handle_delete_action(self, row: int) -> None:
        """
        Handle deletion of an account.
        
        Args:
            row (int): Row index to delete
        """
        if row >= 0:
            reply = QMessageBox.question(
                self, 'Confirm Deletion',
                'Are you sure you want to delete this account?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                account_id = self.table.item(row, 0).data(Qt.UserRole)
                self.db.delete_account(account_id)
                self.load_accounts()

    def _handle_copy_action(self, action, row: int, col: int) -> None:
        """
        Handle copying of account information.
        
        Args:
            action: The selected menu action
            row (int): Row index
            col (int): Column index
        """
        clipboard = QApplication.clipboard()
        
        if row >= 0:
            if action.text() == "Copy Value":
                clipboard.setText(self.table.item(row, col).text())
            elif action.text() == "Copy Raw Value":
                clipboard.setText(self.table.item(row, col).data(Qt.UserRole))
            elif action.text() == "Copy Row (Tab separated)":
                row_data = []
                for c in range(self.table.columnCount()):
                    row_data.append(self.table.item(row, c).data(Qt.UserRole))
                clipboard.setText('\t'.join(row_data))
            elif action.text() == "Copy Row (CSV format)":
                row_data = []
                for c in range(self.table.columnCount()):
                    value = self.table.item(row, c).data(Qt.UserRole)
                    if ',' in value:
                        value = f'"{value}"'
                    row_data.append(value)
                clipboard.setText(','.join(row_data))

    def add_account(self) -> None:
        """Handle adding a new account."""
        dialog = AddAccountDialog(self)
        dialog.account_added.connect(self._handle_account_added)
        dialog.exec()

    def _handle_account_added(self, name: str, username: str, password: str, otp: str) -> None:
        """
        Handle new account information from dialog.
        
        Args:
            name (str): Account name
            username (str): Username
            password (str): Password
            otp (str): OTP secret
        """
        self.db.add_account(name, username, password, otp)
        self.load_accounts()

    def load_accounts(self) -> None:
        """Load accounts from database into table."""
        accounts = self.db.get_accounts()
        self.table.setRowCount(len(accounts))
        
        for row, account in enumerate(accounts):
            self._update_table_row(row, account)

    def _update_table_row(self, row: int, account: Dict) -> None:
        """
        Update a single table row with account information.
        
        Args:
            row (int): Row index
            account (Dict): Account information
        """
        # Account name
        name_item = QTableWidgetItem(account['name'])
        name_item.setData(Qt.UserRole, account['id'])
        self.table.setItem(row, 0, name_item)
        
        # Username
        username_item = QTableWidgetItem(account['username'])
        username_item.setData(Qt.UserRole, account['username'])
        self.table.setItem(row, 1, username_item)
        
        # Password (masked)
        password_item = QTableWidgetItem('••••••••')
        password_item.setData(Qt.UserRole, account['password'])
        self.table.setItem(row, 2, password_item)
        
        # OTP
        if account['otp_secret']:
            totp = pyotp.TOTP(account['otp_secret'])
            otp_value = totp.now()
            otp_item = QTableWidgetItem(otp_value)
            otp_item.setData(Qt.UserRole, account['otp_secret'])
            self.table.setItem(row, 3, otp_item)
        else:
            otp_item = QTableWidgetItem('')
            otp_item.setData(Qt.UserRole, '')
            self.table.setItem(row, 3, otp_item)

    def update_otp_codes(self) -> None:
        """Update OTP codes in the table."""
        for row in range(self.table.rowCount()):
            otp_item = self.table.item(row, 3)
            if otp_item and otp_item.data(Qt.UserRole):
                totp = pyotp.TOTP(otp_item.data(Qt.UserRole))
                otp_item.setText(totp.now())
