"""
Dashboard Screen - Main Navigation Hub
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from database_desktop import get_user_count, get_today_users_count


class StatCard(QFrame):
    """Custom stat card widget with proper sizing."""
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setup_ui(title, value)
        
    def setup_ui(self, title, value):
        self.setStyleSheet("""
            StatCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fcb900, stop:1 #ffd700);
                border: none;
                border-radius: 18px;
            }
        """)
        self.setMinimumSize(210, 140)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(8)
        
        # Value label
        self.value_label = QLabel(str(value))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_font = QFont("Segoe UI", 42, QFont.Weight.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(self.value_label, 2)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 14, QFont.Weight.DemiBold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #000000; background: transparent;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label, 1)


class NavButton(QPushButton):
    """Custom navigation button with proper sizing."""
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setText(f"{title}\n{subtitle}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(75)
        self.setStyleSheet("""
            NavButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fcb900, stop:1 #ffd700);
                color: #000000;
                padding: 18px;
                border: none;
                border-radius: 14px;
                text-align: center;
                font-weight: bold;
            }
            NavButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffd700, stop:1 #ffe44d);
            }
            NavButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0a800, stop:1 #fcb900);
            }
        """)


class Dashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("🔐 User Management System - Dashboard")
        self.setMinimumSize(700, 550)
        
        # Set background color directly
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(30, 25, 30, 25)
        
        # Header
        header = QLabel("🔐 User Management System")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setStyleSheet("color: #000000; background: transparent;")
        main_layout.addWidget(header)
        
        # User info
        user_info = QLabel(f"👤 Logged in as: {self.user_data['name']} ({self.user_data['role']})")
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_font = QFont("Segoe UI", 12, QFont.Weight.DemiBold)
        user_info.setFont(user_font)
        user_info.setStyleSheet("color: #2c3e50; background: transparent;")
        main_layout.addWidget(user_info)
        
        main_layout.addSpacing(15)
        
        # Stats section with padding
        stats_container = QHBoxLayout()
        stats_container.addSpacing(150)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(40)
        
        total_users = get_user_count()
        self.stat1 = StatCard("👥 Total Users", total_users)
        stats_layout.addWidget(self.stat1)
        
        today_users = get_today_users_count()
        self.stat2 = StatCard("✨ Added Today", today_users)
        stats_layout.addWidget(self.stat2)
        
        stats_container.addLayout(stats_layout)
        stats_container.addSpacing(150)
        
        main_layout.addLayout(stats_container)
        
        main_layout.addSpacing(15)
        
        # Navigation label
        nav_label = QLabel("📋 Navigation")
        nav_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        nav_label.setFont(nav_font)
        nav_label.setStyleSheet("color: #000000; background: transparent;")
        main_layout.addWidget(nav_label)
        
        main_layout.addSpacing(8)
        
        # Navigation buttons vertical layout with horizontal padding
        nav_container = QHBoxLayout()
        nav_container.addSpacing(250)
        
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(18)
        
        self.add_btn = NavButton("➕ Add Users", "Create new user accounts")
        self.add_btn.clicked.connect(self.open_add_users)
        nav_layout.addWidget(self.add_btn)
        
        self.show_btn = NavButton("👥 Show Users", "View all user accounts")
        self.show_btn.clicked.connect(self.open_show_users)
        nav_layout.addWidget(self.show_btn)
        
        self.change_btn = NavButton("🔑 Change Password", "Update user passwords")
        self.change_btn.clicked.connect(self.open_change_password)
        nav_layout.addWidget(self.change_btn)
        
        self.remove_btn = NavButton("🗑️ Remove User", "Delete user accounts")
        self.remove_btn.clicked.connect(self.open_remove_user)
        nav_layout.addWidget(self.remove_btn)
        
        nav_container.addLayout(nav_layout)
        nav_container.addSpacing(250)
        
        main_layout.addLayout(nav_container)
        
        main_layout.addStretch(1)
        
        # Logout button with padding
        logout_container = QHBoxLayout()
        logout_container.addSpacing(250)
        
        logout_btn = QPushButton("🚪 LOGOUT")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setMinimumHeight(60)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                padding: 16px;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff6b5a;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        logout_container.addWidget(logout_btn)
        logout_container.addSpacing(250)
        
        main_layout.addLayout(logout_container)
        
        # Security label
        security = QLabel("🔒 Secured with enterprise-grade encryption")
        security.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_font = QFont("Segoe UI", 9)
        security.setFont(security_font)
        security.setStyleSheet("color: #7f8c8d; background: transparent;")
        main_layout.addWidget(security)
    
    def open_add_users(self):
        from add_user_ui import AddUserScreen
        self.add_window = AddUserScreen()
        self.add_window.show()
    
    def open_show_users(self):
        from show_users_ui import ShowUsersScreen
        self.show_window = ShowUsersScreen()
        self.show_window.show()
    
    def open_change_password(self):
        from change_password_ui import ChangePasswordScreen
        self.change_window = ChangePasswordScreen()
        self.change_window.show()
    
    def open_remove_user(self):
        from remove_user_ui import RemoveUserScreen
        self.remove_window = RemoveUserScreen()
        self.remove_window.show()
    
    def logout(self):
        from login_ui import LoginScreen
        self.login_window = LoginScreen()
        self.login_window.show()
        self.close()
