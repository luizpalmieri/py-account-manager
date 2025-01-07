"""
Unit tests for the database manager.
"""
import unittest
import os
import tempfile
import hashlib
from src.database.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""

    def setUp(self):
        """Set up test environment before each test."""
        self.test_db_fd, self.test_db_path = tempfile.mkstemp()
        self.master_password = "test_password"
        self.master_password_hash = hashlib.sha256(self.master_password.encode()).hexdigest()
        self.db = DatabaseManager(self.master_password_hash, self.test_db_path)

    def tearDown(self):
        """Clean up test environment after each test."""
        self.db.close()
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)

    def test_add_account(self):
        """Test adding an account."""
        # Add test account
        account_id = self.db.add_account("Test Service", "test_user", "test_pass", "test_otp")
        
        # Verify account was added
        accounts = self.db.get_accounts()
        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0]['name'], "Test Service")
        self.assertEqual(accounts[0]['username'], "test_user")
        self.assertEqual(accounts[0]['password'], "test_pass")
        self.assertEqual(accounts[0]['otp_secret'], "test_otp")

    def test_update_account(self):
        """Test updating an account."""
        # Add and then update test account
        account_id = self.db.add_account("Test Service", "test_user", "test_pass", "test_otp")
        self.db.update_account(account_id, "Updated Service", "updated_user", "updated_pass", "updated_otp")
        
        # Verify account was updated
        accounts = self.db.get_accounts()
        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0]['name'], "Updated Service")
        self.assertEqual(accounts[0]['username'], "updated_user")
        self.assertEqual(accounts[0]['password'], "updated_pass")
        self.assertEqual(accounts[0]['otp_secret'], "updated_otp")

    def test_delete_account(self):
        """Test deleting an account."""
        # Add and then delete test account
        account_id = self.db.add_account("Test Service", "test_user", "test_pass", "test_otp")
        self.db.delete_account(account_id)
        
        # Verify account was deleted
        accounts = self.db.get_accounts()
        self.assertEqual(len(accounts), 0)

    def test_invalid_master_password(self):
        """Test authentication with invalid master password."""
        wrong_password = "wrong_password"
        wrong_hash = hashlib.sha256(wrong_password.encode()).hexdigest()
        
        # Try to create new instance with wrong password
        with self.assertRaises(ValueError):
            new_db = DatabaseManager(wrong_hash, self.test_db_path)

    def test_encryption(self):
        """Test that sensitive data is properly encrypted."""
        # Add test account
        account_id = self.db.add_account("Test Service", "test_user", "test_pass", "test_otp")
        
        # Verify data is encrypted in database
        self.db.cursor.execute('SELECT password, otp_secret FROM accounts WHERE id=?', (account_id,))
        encrypted_data = self.db.cursor.fetchone()
        
        # Check that encrypted data is different from original
        self.assertNotEqual(encrypted_data[0], "test_pass")
        self.assertNotEqual(encrypted_data[1], "test_otp")
        
        # Verify data can be decrypted correctly
        accounts = self.db.get_accounts()
        self.assertEqual(accounts[0]['password'], "test_pass")
        self.assertEqual(accounts[0]['otp_secret'], "test_otp")

if __name__ == '__main__':
    unittest.main()
