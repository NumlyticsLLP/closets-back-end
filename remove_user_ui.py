"""
Remove User Screen - Delete user accounts
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from database_desktop import get_all_users, remove_user


class RemoveUserScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.all_users = []  # Store all users for filtering
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🗑️ Remove User")
        self.setMinimumSize(500, 380)
        
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
        
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.remove_button = QPushButton("🗑️ REMOVE USER")
        self.remove_button.setMaximumWidth(250)
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
        self.remove_button.setEnabled(True)
        
        if not df.empty:
            for _, row in df.iterrows():
                display_text = f"{row['Name']} ({row['Email']})"
                self.user_combo.addItem(display_text, row['Email'])
        else:
            self.user_combo.addItem("No users found", None)
            self.remove_button.setEnabled(False)
    
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
            self.user_combo.addItem("No users found", None)
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
            self.user_combo.addItem("❌ No users found", None)
    
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
