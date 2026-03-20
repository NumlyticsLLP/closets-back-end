"""
Add User Screen - Create new user accounts
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QComboBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from database_desktop import add_user, get_all_users, get_all_records_from_table, get_current_table_info
from utils import gen_password, resource_path
import os
from datetime import datetime


class AddUserScreen(QWidget):
    
    def __init__(self):
        super().__init__()
        # Load table configuration
        self.table_config = get_current_table_info()
        self.last_credentials = None
        self.init_ui()


        
    def init_ui(self):
        self.setWindowTitle(" Add User")
        self.setMinimumSize(500, 480)
        
        # Dark luxury background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 30, 40, 30)
        
        layout.addStretch(1)
        
        # Top section with Logo
        top_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = resource_path(os.path.join("assets", "Logo 1.png"))
        if os.path.exists(logo_path):
            logo = QPixmap(logo_path)
            scaled_logo = logo.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Content container with width constraint
        content_container = QHBoxLayout()
        content_container.addStretch(1)
        
        # Content layout (form fields)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel(" Add New User")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #BAA787; background: transparent; letter-spacing: 2px;")
        content_layout.addWidget(title)
        
        content_layout.addSpacing(20)
        
        # Name field
        name_label = QLabel("Full Name")
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        name_label.setStyleSheet("color: #6B5E4E; background: transparent; letter-spacing: 1px;")
        content_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("John Doe")
        self.name_input.setMinimumHeight(48)
        self.name_input.setFont(QFont("Segoe UI", 11))
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QLineEdit:hover {
                border: 1px solid #BAA787;
            }
            QLineEdit:focus {
                border: 2px solid #BAA787;
                background-color: #FDFAF7;
            }
        """)
        content_layout.addWidget(self.name_input)
        
        content_layout.addSpacing(10)
        
        # Email field
        email_label = QLabel("Email Address")
        email_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        email_label.setStyleSheet("color: #6B5E4E; background: transparent; letter-spacing: 1px;")
        content_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("john.doe@example.com")
        self.email_input.setMinimumHeight(48)
        self.email_input.setFont(QFont("Segoe UI", 11))
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QLineEdit:hover {
                border: 1px solid #BAA787;
            }
            QLineEdit:focus {
                border: 2px solid #BAA787;
                background-color: #FDFAF7;
            }
        """)
        content_layout.addWidget(self.email_input)
        
        content_layout.addSpacing(10)
        
        # Role field
        role_label = QLabel(" Role")
        role_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        role_label.setStyleSheet("color: #6B5E4E; background: transparent; letter-spacing: 1px;")
        content_layout.addWidget(role_label)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setMinimumHeight(48)
        self.role_combo.setFont(QFont("Segoe UI", 11))
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 18px;
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QComboBox:hover {
                border: 1px solid #BAA787;
            }
            QComboBox:focus {
                border: 2px solid #BAA787;
                background-color: #FDFAF7;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #BAA787;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #4D4D4D;
                selection-background-color: #BAA787;
                selection-color: #FFFFFF;
                border: 1px solid #BAA787;
            }
        """)
        content_layout.addWidget(self.role_combo)
        
        content_layout.addSpacing(15)
        
        # Info label
        info_label = QLabel(" Password will be auto-generated based on the user's name")
        info_label.setFont(QFont("Segoe UI", 10))
        info_label.setStyleSheet("color: #8B7355; padding: 14px; background-color: #F8F4EE; border-radius: 10px; border: 1px solid #D4C4A0;")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)
        
        content_layout.addSpacing(20)
        
        content_layout.addStretch(2)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.add_button = QPushButton(" ADD USER")
        self.add_button.setMaximumWidth(250)
        self.add_button.clicked.connect(self.handle_add_user)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setMinimumHeight(54)
        self.add_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BAA787, stop:1 #D4C4A0);
                color: #1A1A1A;
                border: none;
                border-radius: 12px;
                padding: 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #D4C4A0, stop:1 #E8DCC8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8B7355, stop:1 #BAA787);
                color: #FFFFFF;
            }
        """)
        button_layout.addWidget(self.add_button)
                # Copy Data button (hidden initially, shown after successful add)
        self.copy_button = QPushButton("\U0001F4CB Copy Data")
        self.copy_button.setMaximumWidth(200)
        self.copy_button.clicked.connect(self.copy_credentials_to_clipboard)
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setMinimumHeight(54)
        self.copy_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #F0EBE3;
                color: #8B7355;
                border: 1px solid #BAA787;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #BAA787;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #8B7355;
                color: #FFFFFF;
            }
        """)
        self.copy_button.setVisible(False)
        button_layout.addWidget(self.copy_button)

        
        content_layout.addLayout(button_layout)
        
        # Custom tables are now supported with generic CRUD operations
        
        # Close content container
        content_container.addLayout(content_layout)
        content_container.addStretch(1)
        
        layout.addLayout(content_container)
        
        layout.addStretch(1)
        
    def handle_add_user(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        role = self.role_combo.currentText()
    

        
        if not name or not email:
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        # Generate password
        password = gen_password(name)
        
        # Add user to default users table (audit logging handled in add_user function)
        success, message = add_user(email, name, password, role)
        if success:
            # Store credentials for copy button
            self.last_credentials = f"Name: {name}\nEmail: {email}\nPassword: {password}\nRole: {role}"
            
            # Show copy button
            self.copy_button.setVisible(True)
            
            # Show success message (no auto-copy)
            QMessageBox.information(self, "Success", 
                f"User added successfully!\n\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Password: {password}\n"
                f"Role: {role}\n\n"
                f"Click 'Copy Data' to copy credentials to clipboard.")

            
            # Clear fields
            self.name_input.clear()
            self.email_input.clear()
            self.role_combo.setCurrentIndex(0)
        else:
            QMessageBox.warning(self, "Error", f" {message}")


    def copy_credentials_to_clipboard(self):
        """Copy last added user credentials to clipboard."""
        if self.last_credentials:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.last_credentials)
            QMessageBox.information(self, "Copied", "User credentials copied to clipboard!")


        

            


