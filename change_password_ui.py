"""
Change Password Screen - Update user passwords
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from database_desktop import get_all_users, change_password
from utils import gen_password
import pandas as pd
from datetime import datetime


class ChangePasswordScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🔑 Change Password")
        self.setMinimumSize(500, 420)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Title
        title = QLabel("🔑 Change Password")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
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
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                color: #000000;
            }
            QComboBox:hover {
                border: 2px solid #fcb900;
                background-color: #fffef8;
            }
            QComboBox:focus {
                border: 2px solid #fcb900;
                background-color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #000000;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #fcb900;
                border: 2px solid #e0e0e0;
            }
        """)
        self.load_users()
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
                    stop:0 #fffef8, stop:1 #fff9e6);
                border: 2px solid #fcb900;
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
        self.change_button.clicked.connect(self.handle_change_password)
        self.change_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_button.setMinimumHeight(54)
        self.change_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.change_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fcb900, stop:1 #ffd700);
                color: #000000;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffd700, stop:1 #ffe44d);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0a800, stop:1 #fcb900);
            }
        """)
        button_layout.addWidget(self.change_button)
        
        self.close_button = QPushButton("❌ CLOSE")
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
        
    def load_users(self):
        df = get_all_users()
        if not df.empty:
            for _, row in df.iterrows():
                display_text = f"{row['Name']} ({row['Email']})"
                self.user_combo.addItem(display_text, (row['Email'], row['Name']))
        else:
            self.user_combo.addItem("No users found", (None, None))
            self.change_button.setEnabled(False)
    
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
            
            # Export to Excel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"password_changed_{timestamp}.xlsx"
            
            df = pd.DataFrame([{
                "Name": name,
                "Email": email,
                "New Password": new_password,
                "Changed": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "Success", 
                f"✅ Password changed successfully!\n\n"
                f"📝 New credentials saved to: {filename}\n\n"
                f"New Password: {new_password}")
        else:
            QMessageBox.warning(self, "Error", f"❌ {message}")
