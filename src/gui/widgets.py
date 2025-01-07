"""
Custom widget implementations for the password manager GUI.
"""
from PySide6.QtWidgets import (QPushButton, QTableWidget, QTableWidgetItem, 
                             QDialog, QVBoxLayout, QLineEdit, QLabel)
from PySide6.QtCore import Qt, Signal

class StyledButton(QPushButton):
    """Custom styled button with optional icon."""
    
    def __init__(self, text, icon=None, parent=None):
        """
        Initialize the button.
        
        Args:
            text (str): Button text
            icon (QStyle.StandardPixmap, optional): Icon to display
            parent (QWidget, optional): Parent widget
        """
        super().__init__(text, parent)
        if icon:
            self.setIcon(self.style().standardIcon(icon))

class CustomTableWidget(QTableWidget):
    """Custom table widget with enhanced functionality."""
    
    def __init__(self, parent=None):
        """Initialize the table widget."""
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

class LoginDialog(QDialog):
    """Dialog for master password authentication."""
    
    def __init__(self, parent=None):
        """Initialize the login dialog."""
        super().__init__(parent)
        self.setWindowTitle('Enter Master Password')
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog's UI components."""
        layout = QVBoxLayout(self)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Master Password')
        
        # Submit button
        submit_btn = StyledButton('Login')
        submit_btn.clicked.connect(self.accept)
        
        # Layout
        layout.addWidget(QLabel('Enter Master Password:'))
        layout.addWidget(self.password_input)
        layout.addWidget(submit_btn)

class AddAccountDialog(QDialog):
    """Dialog for adding or editing account details."""
    
    account_added = Signal(str, str, str, str)  # name, username, password, otp
    
    def __init__(self, parent=None, edit_mode=False, account_data=None):
        """
        Initialize the dialog.
        
        Args:
            parent (QWidget, optional): Parent widget
            edit_mode (bool): Whether dialog is for editing existing account
            account_data (dict, optional): Existing account data for editing
        """
        super().__init__(parent)
        self.edit_mode = edit_mode
        self.account_data = account_data
        self.setWindowTitle('Edit Account' if edit_mode else 'Add Account')
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog's UI components."""
        layout = QVBoxLayout(self)
        
        # Input fields
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Account Name')
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Password')
        
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText('OTP Secret (Optional)')
        
        # Pre-fill data if editing
        if self.edit_mode and self.account_data:
            self.name_input.setText(self.account_data['name'])
            self.username_input.setText(self.account_data['username'])
            self.password_input.setText(self.account_data['password'])
            if self.account_data.get('otp_secret'):
                self.otp_input.setText(self.account_data['otp_secret'])
        
        # Submit button
        submit_btn = StyledButton('Save' if self.edit_mode else 'Add')
        submit_btn.clicked.connect(self.handle_submit)
        
        # Layout
        layout.addWidget(QLabel('Account Name:'))
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel('Username:'))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel('Password:'))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel('OTP Secret (Optional):'))
        layout.addWidget(self.otp_input)
        layout.addWidget(submit_btn)

    def handle_submit(self):
        """Handle form submission."""
        name = self.name_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        otp = self.otp_input.text()
        
        if name and username and password:
            self.account_added.emit(name, username, password, otp)
            self.accept()
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Error', 'Please fill in all required fields.')
