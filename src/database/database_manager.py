"""
Database manager module for handling all database operations.
"""
import sqlite3
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations including encryption and account management."""
    
    def __init__(self, master_password_hash: str, db_path: str = 'passwords.db'):
        """
        Initialize database connection and setup.
        
        Args:
            master_password_hash (str): Hash of the master password
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.master_password_hash = master_password_hash
        
        self._setup_database()
        self._validate_or_initialize_master_password()
        self._setup_encryption()
        
    def _setup_database(self) -> None:
        """Create necessary database tables if they don't exist."""
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    otp_secret TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database setup failed: {e}")
            raise

    def _validate_or_initialize_master_password(self) -> None:
        """Validate existing master password or initialize if first time."""
        try:
            self.cursor.execute('SELECT value FROM config WHERE key = "master_password_hash"')
            stored_hash = self.cursor.fetchone()
            
            if stored_hash is None:
                self._initialize_master_password()
            else:
                self._validate_master_password(stored_hash[0])
        except sqlite3.Error as e:
            logger.error(f"Master password validation failed: {e}")
            raise

    def _initialize_master_password(self) -> None:
        """Initialize master password and salt for first time setup."""
        try:
            self.cursor.execute('INSERT INTO config (key, value) VALUES (?, ?)',
                              ('master_password_hash', self.master_password_hash))
            salt = os.urandom(16)
            self.cursor.execute('INSERT INTO config (key, value) VALUES (?, ?)',
                              ('salt', base64.b64encode(salt).decode()))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Master password initialization failed: {e}")
            raise

    def _validate_master_password(self, stored_hash: str) -> None:
        """
        Validate the provided master password against stored hash.
        
        Args:
            stored_hash (str): The hash stored in the database
            
        Raises:
            ValueError: If the master password is invalid
        """
        if stored_hash != self.master_password_hash:
            logger.warning("Invalid master password attempt")
            raise ValueError("Invalid master password")

    def _setup_encryption(self) -> None:
        """Setup encryption using the master password and stored salt."""
        try:
            self.cursor.execute('SELECT value FROM config WHERE key = "salt"')
            result = self.cursor.fetchone()
            
            if result:
                salt = base64.b64decode(result[0])
            else:
                salt = os.urandom(16)
                self.cursor.execute('INSERT INTO config (key, value) VALUES (?, ?)',
                                  ('salt', base64.b64encode(salt).decode()))
                self.conn.commit()

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_password_hash.encode()))
            self.fernet = Fernet(key)
        except Exception as e:
            logger.error(f"Encryption setup failed: {e}")
            raise

    def add_account(self, name: str, username: str, password: str, 
                   otp_secret: Optional[str] = None) -> int:
        """
        Add a new account to the database.
        
        Args:
            name (str): Account name/service
            username (str): Username for the account
            password (str): Password for the account
            otp_secret (str, optional): OTP secret key
            
        Returns:
            int: ID of the newly created account
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            encrypted_password = self.fernet.encrypt(password.encode()).decode()
            encrypted_otp = (self.fernet.encrypt(otp_secret.encode()).decode() 
                           if otp_secret else None)
            
            self.cursor.execute('''
                INSERT INTO accounts (name, username, password, otp_secret)
                VALUES (?, ?, ?, ?)
            ''', (name, username, encrypted_password, encrypted_otp))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add account {name}: {e}")
            raise

    def get_accounts(self) -> List[Dict]:
        """
        Retrieve all accounts from the database.
        
        Returns:
            List[Dict]: List of account dictionaries
        """
        try:
            self.cursor.execute('SELECT * FROM accounts')
            accounts = self.cursor.fetchall()
            decrypted_accounts = []
            
            for account in accounts:
                try:
                    decrypted_account = self._decrypt_account(account)
                    if decrypted_account:
                        decrypted_accounts.append(decrypted_account)
                except Exception as e:
                    logger.error(f"Failed to decrypt account {account[1]}: {e}")
                    continue
                    
            return decrypted_accounts
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve accounts: {e}")
            raise

    def _decrypt_account(self, account: tuple) -> Optional[Dict]:
        """
        Decrypt a single account's sensitive information.
        
        Args:
            account (tuple): Account tuple from database
            
        Returns:
            Optional[Dict]: Decrypted account information or None if decryption fails
        """
        try:
            decrypted_password = self.fernet.decrypt(account[3].encode()).decode()
            decrypted_otp = (self.fernet.decrypt(account[4].encode()).decode() 
                            if account[4] else None)
            
            return {
                'id': account[0],
                'name': account[1],
                'username': account[2],
                'password': decrypted_password,
                'otp_secret': decrypted_otp,
                'created_at': account[5],
                'updated_at': account[6]
            }
        except Exception as e:
            logger.error(f"Decryption failed for account {account[1]}: {e}")
            return None

    def update_account(self, id: int, name: str, username: str, 
                      password: str, otp_secret: Optional[str] = None) -> None:
        """
        Update an existing account.
        
        Args:
            id (int): Account ID
            name (str): New account name
            username (str): New username
            password (str): New password
            otp_secret (str, optional): New OTP secret
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            encrypted_password = self.fernet.encrypt(password.encode()).decode()
            encrypted_otp = (self.fernet.encrypt(otp_secret.encode()).decode() 
                           if otp_secret else None)
            
            self.cursor.execute('''
                UPDATE accounts 
                SET name=?, username=?, password=?, otp_secret=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (name, username, encrypted_password, encrypted_otp, id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to update account {name}: {e}")
            raise

    def delete_account(self, id: int) -> None:
        """
        Delete an account from the database.
        
        Args:
            id (int): Account ID to delete
            
        Raises:
            sqlite3.Error: If database operation fails
        """
        try:
            self.cursor.execute('DELETE FROM accounts WHERE id=?', (id,))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to delete account {id}: {e}")
            raise

    def close(self) -> None:
        """Close the database connection."""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            logger.error(f"Failed to close database connection: {e}")
            raise
