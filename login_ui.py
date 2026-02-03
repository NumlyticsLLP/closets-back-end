"""
Login Screen - Admin Authentication
"""
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from database_desktop import verify_admin_credentials

logger = logging.getLogger(__name__)


class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("🔐 User Management System - Admin Login")
        self.setMinimumSize(450, 400)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 40, 50, 40)
        
        layout.addStretch(1)
        
        # Title
        title = QLabel("🔐 Admin Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("User Management System")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #7f8c8d; background: transparent;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(25)
        
        # Email field
        email_label = QLabel("📧 Email Address")
        email_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        email_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("admin@example.com")
        self.email_input.setMinimumHeight(50)
        self.email_input.setFont(QFont("Segoe UI", 11))
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:hover {
                border: 2px solid #fcb900;
                background-color: #fffef8;
            }
            QLineEdit:focus {
                border: 2px solid #fcb900;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self.email_input)
        
        layout.addSpacing(10)
        
        # Password field
        password_label = QLabel("🔒 Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        password_label.setStyleSheet("color: #2c3e50; background: transparent;")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setMinimumHeight(50)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:hover {
                border: 2px solid #fcb900;
                background-color: #fffef8;
            }
            QLineEdit:focus {
                border: 2px solid #fcb900;
                background-color: #ffffff;
            }
        """)
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(20)
        
        # Login button
        self.login_button = QPushButton("🚀 LOGIN")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setMinimumHeight(50)
        self.login_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fcb900, stop:1 #ffd700);
                color: #000000;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0a800, stop:1 #fcb900);
            }
        """)
        layout.addWidget(self.login_button)
        
        layout.addSpacing(15)
        
        # Info label
        info_label = QLabel("ℹ️ Only admin users can access the management system")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setFont(QFont("Segoe UI", 10))
        info_label.setStyleSheet("color: #7f8c8d; background: transparent;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch(1)
        
        # Security label
        security_label = QLabel("🔒 Protected by enterprise-grade encryption")
        security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_label.setFont(QFont("Segoe UI", 9))
        security_label.setStyleSheet("color: #95a5a6; background: transparent;")
        layout.addWidget(security_label)
        
    def handle_login(self):
        try:
            email = self.email_input.text().strip()
            password = self.password_input.text()
            
            logger.info("="*60)
            logger.info("Login button clicked")
            logger.info(f"Email entered: {email}")
            
            if not email or not password:
                logger.warning("Login failed: Empty email or password")
                QMessageBox.warning(self, "Error", "⚠️ Please enter both email and password")
                return
            
            logger.info("Authenticating user...")
            success, user_data = verify_admin_credentials(email, password)
            
            if success and user_data:
                logger.info(f"Login successful for: {user_data['name']}")
                logger.info("Opening dashboard...")
                
                from dashboard_ui import Dashboard
                self.dashboard = Dashboard(user_data)
                self.dashboard.show()
                
                logger.info("Dashboard window displayed")
                logger.info("Closing login window...")
                self.close()
                logger.info("Login window closed")
            else:
                logger.warning("Login failed: Invalid credentials")
                error_msg = user_data.get('error', 'Invalid email or password') if user_data else 'Invalid email or password'
                QMessageBox.warning(self, "Login Failed", f"❌ {error_msg}")
                
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"❌ An error occurred: {str(e)}")
