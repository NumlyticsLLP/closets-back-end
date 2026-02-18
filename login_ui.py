"""
Login Screen - Admin Authentication with Mode Support
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from database_desktop import verify_admin_credentials, get_current_mode, get_mode_info


class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.current_mode = None
        self.db_config = None
        self.init_ui()
        
    def init_ui(self):
        # Get mode information
        mode_info = get_mode_info()
        mode = mode_info.get('mode', 'unknown')
        mode_icon = "🧪" if mode == "test" else "🏭" if mode == "production" else "🔧"
        
        self.setWindowTitle(f"🔐 Password Generator - Admin Login ({mode.title()} Mode)")
        self.setMinimumSize(450, 500)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Mode indicator frame
        self.add_mode_indicator(layout, mode_info)
        
        layout.addSpacing(10)
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
        self.email_input.setPlaceholderText("Enter admin email")
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
        
        # Password field with eye button
        password_container = QHBoxLayout()
        password_container.setSpacing(0)
        password_container.setContentsMargins(0, 0, 0, 0)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setMinimumHeight(50)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px 12px 18px;
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
        password_container.addWidget(self.password_input, 1)
        
        # Eye button for show/hide password
        self.show_password_btn = QPushButton("👁️")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setMaximumWidth(50)
        self.show_password_btn.setMinimumHeight(50)
        self.show_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #000000;
                border: none;
                padding: 12px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        password_container.addWidget(self.show_password_btn)
        
        password_widget = QWidget()
        password_widget.setLayout(password_container)
        layout.addWidget(password_widget)
        
        layout.addSpacing(20)
        
        # Login button centered
        login_container = QHBoxLayout()
        login_container.addStretch(1)
        
        self.login_button = QPushButton("🚀 LOGIN")
        self.login_button.setMaximumWidth(300)
        self.login_button.setMinimumWidth(200)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setMinimumHeight(55)
        self.login_button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fcb900, stop:1 #ffd700);
                color: #000000;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0a800, stop:1 #fcb900);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #d4a700, stop:1 #e0a800);
            }
        """)
        login_container.addWidget(self.login_button)
        login_container.addStretch(1)
        
        layout.addLayout(login_container)
        
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
            
            if not email or not password:
                QMessageBox.warning(self, "Error", "⚠️ Please enter both email and password")
                return
            
            success, user_data = verify_admin_credentials(email, password)
            
            if success and user_data:
                from dashboard_ui import Dashboard
                self.dashboard = Dashboard(user_data)
                self.dashboard.show()
                
                self.close()
            else:
                error_msg = user_data.get('error', 'Invalid email or password') if user_data else 'Invalid email or password'
                QMessageBox.warning(self, "Login Failed", f"❌ {error_msg}")
            
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"❌ An error occurred: {str(e)}")
    
    def add_mode_indicator(self, layout, mode_info):
        """Add mode indicator showing current environment and database info."""
        mode = mode_info.get('mode', 'unknown')
        host = mode_info.get('host', 'unknown')
        database = mode_info.get('database', 'unknown')
        user = mode_info.get('user', 'unknown')
        
        # Determine colors and icons based on mode
        if mode == 'test':
            mode_icon = "🧪"
            mode_color = "#27ae60"
            bg_color = "#e8f5e8"
        elif mode == 'production':
            mode_icon = "🏭"
            mode_color = "#e67e22"
            bg_color = "#fff3e0"
        else:
            mode_icon = "🔧"
            mode_color = "#95a5a6"
            bg_color = "#f8f9fa"
        
        # Create mode indicator frame
        mode_frame = QFrame()
        mode_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        mode_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {mode_color};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        
        mode_layout = QVBoxLayout(mode_frame)
        mode_layout.setSpacing(5)
        mode_layout.setContentsMargins(10, 8, 10, 8)
        
        # Mode title
        mode_title = QLabel(f"{mode_icon} {mode.upper()} MODE")
        mode_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        mode_title.setStyleSheet(f"color: {mode_color}; background: transparent;")
        mode_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_layout.addWidget(mode_title)
        
        # Database info
        db_info = QLabel(f"📊 {database}@{host} | 👤 {user}")
        db_info.setFont(QFont("Segoe UI", 9))
        db_info.setStyleSheet("color: #34495e; background: transparent;")
        db_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_layout.addWidget(db_info)
        
        layout.addWidget(mode_frame)    
    def toggle_password_visibility(self):
        """Toggle password field visibility."""
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🚫")
            self.show_password_btn.setToolTip("Hide password")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁️")
            self.show_password_btn.setToolTip("Show password")