"""
Add User Screen - Create new user accounts
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from database_desktop import add_user
from utils import gen_password
from file_storage_dialog import FileStorageDialog
from file_storage_utils import FileStorageManager
import pandas as pd
import os
import json
from datetime import datetime


class AddUserScreen(QWidget):
    CONFIG_FILE = "download_path_config.json"
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def load_saved_path(self):
        """Load saved download path from config file."""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('download_path', os.path.expanduser("~"))
        except:
            pass
        return os.path.expanduser("~")
    
    def save_path(self, path):
        """Save download path to config file."""
        try:
            config = {'download_path': path}
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except:
            pass
        
    def init_ui(self):
        self.setWindowTitle("➕ Add User")
        self.setMinimumSize(500, 480)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
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
        title = QLabel("➕ Add New User")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Name field
        name_label = QLabel("👤 Full Name")
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        name_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("John Doe")
        self.name_input.setMinimumHeight(48)
        self.name_input.setFont(QFont("Segoe UI", 11))
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid #C5B39F;
                border-radius: 12px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:hover {
                border: 2px solid #BCAA8D;
                background-color: #fdfaf7;
            }
            QLineEdit:focus {
                border: 2px solid #BCAA8D;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self.name_input)
        
        layout.addSpacing(10)
        
        # Email field
        email_label = QLabel("📧 Email Address")
        email_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        email_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("john.doe@example.com")
        self.email_input.setMinimumHeight(48)
        self.email_input.setFont(QFont("Segoe UI", 11))
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid #C5B39F;
                border-radius: 12px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:hover {
                border: 2px solid #BCAA8D;
                background-color: #fdfaf7;
            }
            QLineEdit:focus {
                border: 2px solid #BCAA8D;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self.email_input)
        
        layout.addSpacing(10)
        
        # Role field
        role_label = QLabel("🔰 Role")
        role_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        role_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(role_label)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setMinimumHeight(48)
        self.role_combo.setFont(QFont("Segoe UI", 11))
        self.role_combo.setStyleSheet("""
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
        layout.addWidget(self.role_combo)
        
        layout.addSpacing(15)
        
        # Info label
        info_label = QLabel("🎲 Password will be auto-generated based on the user's name")
        info_label.setFont(QFont("Segoe UI", 10))
        info_label.setStyleSheet("color: #16a085; padding: 14px; background-color: #e8f8f5; border-radius: 10px; border: 1px solid #a7dcd1;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.add_button = QPushButton("➕ ADD USER")
        self.add_button.setMaximumWidth(250)
        self.add_button.clicked.connect(self.handle_add_user)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setMinimumHeight(54)
        self.add_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.add_button.setStyleSheet("""
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
        button_layout.addWidget(self.add_button)
        
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
        
    def handle_add_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        role = self.role_combo.currentText()
        
        if not name or not email:
            QMessageBox.warning(self, "Error", "⚠️ Please fill in all fields")
            return
        
        # Generate password
        password = gen_password(name)
        
        # Add user to database
        success, message = add_user(name, email, password, role)
        
        if success:
            # Show file storage options dialog
            storage_option, file_path = FileStorageDialog.get_storage_choice(
                parent=self,
                title="💾 Save User Data",
                operation="save user credentials"
            )
            
            if storage_option is None:
                # User cancelled file selection
                QMessageBox.information(self, "Info", 
                    f"✅ User added successfully!\n\n"
                    f"👤 Name: {name}\n"
                    f"📧 Email: {email}\n"
                    f"🔑 Password: {password}\n\n"
                    f"⚠️ No files saved (operation cancelled)")
                self.name_input.clear()
                self.email_input.clear()
                self.role_combo.setCurrentIndex(0)
                return
            
            # Prepare user data
            user_data = FileStorageManager.prepare_user_data(name, email, password, role)
            
            # Save data using the storage manager
            save_success, save_message, files_created = FileStorageManager.save_user_data(
                user_data, storage_option, file_path, "user"
            )
            
            if save_success:
                # Show success message with file details
                QMessageBox.information(self, "Success", 
                    f"✅ User added successfully!\n\n"
                    f"👤 Name: {name}\n"
                    f"📧 Email: {email}\n"
                    f"🔑 Password: {password}\n\n"
                    f"{save_message}")
            else:
                # Database success but file save failed
                QMessageBox.warning(self, "Partial Success", 
                    f"✅ User added successfully to database!\n\n"
                    f"👤 Name: {name}\n"
                    f"📧 Email: {email}\n"
                    f"🔑 Password: {password}\n\n"
                    f"⚠️ File save failed: {save_message}")
            
            # Clear fields
            self.name_input.clear()
            self.email_input.clear()
            self.role_combo.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", f"❌ {message}")
            QMessageBox.warning(self, "Error", f"❌ {message}")
