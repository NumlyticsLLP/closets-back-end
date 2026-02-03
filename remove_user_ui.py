"""
Remove User Screen - Delete user accounts
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from database_desktop import get_all_users, remove_user


class RemoveUserScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🗑️ Remove User")
        self.setMinimumSize(500, 380)
        
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
        title = QLabel("🗑️ Remove User")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(15)
        
        # Warning
        warning = QLabel("⚠️ Warning: This action cannot be undone!")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        warning.setStyleSheet("color: #c0392b; background-color: #fadbd8; padding: 16px; border-radius: 10px; border: 1px solid #e74c3c;")
        layout.addWidget(warning)
        
        layout.addSpacing(20)
        
        # User selection
        user_label = QLabel("👤 Select User to Remove")
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
        
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.remove_button = QPushButton("🗑️ REMOVE USER")
        self.remove_button.clicked.connect(self.handle_remove_user)
        self.remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_button.setMinimumHeight(54)
        self.remove_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #ff6b5a;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(self.remove_button)
        
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
                self.user_combo.addItem(display_text, row['Email'])
        else:
            self.user_combo.addItem("No users found", None)
            self.remove_button.setEnabled(False)
    
    def handle_remove_user(self):
        email = self.user_combo.currentData()
        
        if not email:
            QMessageBox.warning(self, "Error", "⚠️ Please select a user")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"🗑️ Are you sure you want to remove this user?\n\n{self.user_combo.currentText()}\n\nThis action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = remove_user(email)
            
            if success:
                QMessageBox.information(self, "Success", "✅ User removed successfully!")
                # Refresh combo box
                self.user_combo.clear()
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", f"❌ {message}")
