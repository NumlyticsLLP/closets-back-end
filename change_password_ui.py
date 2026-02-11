"""
Change Password Screen - Update user passwords
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QMessageBox, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from database_desktop import get_all_users, change_password
from utils import gen_password
from file_storage_dialog import FileStorageDialog
from file_storage_utils import FileStorageManager
import pandas as pd
import os
import json
from datetime import datetime


class ChangePasswordScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.all_users = []  # Store all users for filtering
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🔑 Change Password")
        self.setMinimumSize(500, 420)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Top section with Logo
        top_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "Logo 1.png")
        if os.path.exists(logo_path):
            logo = QPixmap(logo_path)
            scaled_logo = logo.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Title
        title = QLabel("🔑 Change Password")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Search field
        search_label = QLabel("🔍 Search User")
        search_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        search_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type name or email to search...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setFont(QFont("Segoe UI", 10))
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #C5B39F;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
        """)
        self.search_input.textChanged.connect(self.filter_users)
        layout.addWidget(self.search_input)
        
        layout.addSpacing(15)
        
        # User selection
        user_label = QLabel("👤 Select User")
        user_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        user_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(user_label)
        
        self.user_combo = QComboBox()
        self.user_combo.setMinimumHeight(48)
        self.user_combo.setFont(QFont("Segoe UI", 11))
        self.user_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 18px;
                border: 2px solid #C5B39F;
                border-radius: 12px;
                background-color: #ffffff;
                color: #000000;
            }
            QComboBox:hover {
                border: 2px solid #BCAA8D;
                background-color: #fdfaf7;
            }
            QComboBox:focus {
                border: 2px solid #BCAA8D;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #BCAA8D;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #BCAA8D;
                border: 2px solid #C5B39F;
            }
        """)
        layout.addWidget(self.user_combo)
        
        layout.addSpacing(10)
        
        # Info label
        info_label = QLabel("🎲 A random password will be generated based on the user's name")
        info_label.setFont(QFont("Segoe UI", 10))
        info_label.setStyleSheet("color: #16a085; padding: 14px; background-color: #e8f8f5; border-radius: 10px; border: 1px solid #a7dcd1;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Generated password display (hidden initially)
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setMinimumHeight(50)
        self.password_display.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.password_display.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fdfaf7, stop:1 #E4D5C1);
                border: 2px solid #BCAA8D;
                border-radius: 12px;
                padding: 12px 18px;
                color: #000000;
            }
        """)
        self.password_display.setVisible(False)
        layout.addWidget(self.password_display)
        
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.change_button = QPushButton("🔄 CHANGE PASSWORD")
        self.change_button.setMaximumWidth(280)
        self.change_button.clicked.connect(self.handle_change_password)
        self.change_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_button.setMinimumHeight(54)
        self.change_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.change_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BCAA8D, stop:1 #D0BFA1);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #D0BFA1, stop:1 #E4D5C1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #A89673, stop:1 #BCAA8D);
            }
        """)
        button_layout.addWidget(self.change_button)
        
        self.close_button = QPushButton("❌ CLOSE")
        self.close_button.setMaximumWidth(200)
        self.close_button.clicked.connect(self.close)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setMinimumHeight(54)
        self.close_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: #000000;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #b0bec5;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Load users after buttons are created
        self.load_users()
        
    def load_users(self):
        df = get_all_users()
        self.all_users = df  # Store for filtering
        self.populate_from_df(df)
    
    def populate_from_df(self, df):
        """Populate combo box from DataFrame."""
        self.user_combo.clear()
        self.change_button.setEnabled(True)
        
        if not df.empty:
            for _, row in df.iterrows():
                display_text = f"{row['Name']} ({row['Email']})"
                self.user_combo.addItem(display_text, (row['Email'], row['Name']))
        else:
            self.user_combo.addItem("No users found", (None, None))
            self.change_button.setEnabled(False)
    
    def filter_users(self, search_text):
        """Filter users based on search text."""
        search_text = search_text.lower().strip()
        
        if not search_text:
            # If search is empty, show all users
            self.populate_from_df(self.all_users)
            return
        
        # Filter DataFrame based on search text
        if self.all_users.empty:
            self.user_combo.clear()
            self.user_combo.addItem("No users found", (None, None))
            return
        
        # Search in both Name and Email columns
        filtered_df = self.all_users[
            self.all_users['Name'].str.lower().str.contains(search_text, na=False) |
            self.all_users['Email'].str.lower().str.contains(search_text, na=False)
        ]
        
        if not filtered_df.empty:
            self.populate_from_df(filtered_df)
        else:
            self.user_combo.clear()
            self.user_combo.addItem("❌ No users found", (None, None))
    
    def handle_change_password(self):
        user_data = self.user_combo.currentData()
        
        if not user_data or not user_data[0]:
            QMessageBox.warning(self, "Error", "⚠️ Please select a user")
            return
        
        email, name = user_data
        
        # Generate new password
        new_password = gen_password(name)
        
        # Update password in database
        success, message = change_password(email, new_password)
        
        if success:
            # Show the new password
            self.password_display.setText(f"New Password: {new_password}")
            self.password_display.setVisible(True)
            
            # Show file storage options dialog
            storage_option, file_path = FileStorageDialog.get_storage_choice(
                parent=self,
                title="💾 Save Password Change",
                operation="save password change data"
            )
            
            if storage_option is None:
                # User cancelled file selection
                QMessageBox.information(self, "Info", 
                    f"✅ Password changed successfully!\n\n"
                    f"👤 User: {name}\n"
                    f"📧 Email: {email}\n"
                    f"🔑 New Password: {new_password}\n\n"
                    f"⚠️ No files saved (operation cancelled)")
                return
            
            try:
                # Prepare password change data
                password_data = FileStorageManager.prepare_password_change_data(
                    name, email, "N/A", new_password
                )
                
                # Save data using the storage manager
                save_success, save_message, files_created = FileStorageManager.save_user_data(
                    password_data, storage_option, file_path, "password_change"
                )
                
                if save_success:
                    # Show success message with file details
                    QMessageBox.information(self, "Success", 
                        f"✅ Password changed successfully!\n\n"
                        f"👤 User: {name}\n"
                        f"📧 Email: {email}\n"
                        f"🔑 New Password: {new_password}\n\n"
                        f"{save_message}")
                else:
                    # Database success but file save failed
                    QMessageBox.warning(self, "Partial Success", 
                        f"✅ Password changed successfully in database!\n\n"
                        f"👤 User: {name}\n"
                        f"📧 Email: {email}\n"
                        f"🔑 New Password: {new_password}\n\n"
                        f"⚠️ File save failed: {save_message}")
                
            except Exception as e:
                # Password was changed in database but file export failed
                QMessageBox.warning(
                    self, 
                    "Partial Success", 
                    f"✅ Password changed successfully in database!\n\n"
                    f"🔑 New Password: {new_password}\n\n"
                    f"⚠️ File export failed: {str(e)}\n\n"
                    f"The password change was saved to the database."
                )
                
        else:
            QMessageBox.warning(self, "Error", f"❌ {message}")
