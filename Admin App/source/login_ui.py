"""
Login Screen - Admin Authentication
"""
import json
import os
import sys
import traceback
import threading
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QFrame,
                              QFileDialog, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from database_desktop import verify_admin_credentials
from utils import resource_path


class DBConnectThread(QThread):
    """Background thread that tests the DB connection without blocking the UI."""
    success = pyqtSignal()
    failure = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            import mysql.connector
            connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                port=self.config['port'],
                connection_timeout=10,
                use_pure=True # always use pure-Python driver; C-extension can hang inside QThread
            )
            connection.close()
            self.success.emit()
        except Exception as e:
            traceback.print_exc()
            self.failure.emit(str(e))


class DatabaseCredentialsDialog(QWidget):
    """Dialog for selecting database credentials file and entering password"""
    
    SAVED_PATH_FILE = os.path.join(
        os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)),
        "saved_credentials_path.json"
    )

    def __init__(self, parent_app=None):
        super().__init__()
        self.credentials_file_path = None
        self.db_credentials = {}
        self.parent_app = parent_app
        self.init_ui()
        self._auto_load_saved_path()
        
    def init_ui(self):
        """Initialize the database credentials dialog UI"""
        self.setWindowTitle("Identity Manager - Connect")
        self.setMinimumSize(620, 880)

        # Dark luxury background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        self.setPalette(palette)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(50, 30, 50, 30)

        # ── Logo (same as dashboard top-left) ──────────────────────────
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = resource_path(os.path.join("assets", "Logo 1.png"))
        if os.path.exists(logo_path):
            from PyQt6.QtGui import QPixmap
            logo = QPixmap(logo_path)
            scaled = logo.scaledToHeight(110, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled)
        layout.addWidget(logo_label)

        layout.addSpacing(12)

        # ── Title ───────────────────────────────────────────────────────
        title = QLabel("Identity Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #BAA787; background: transparent; letter-spacing: 2px;")
        layout.addWidget(title)

        subtitle = QLabel("Connect to your database to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #6B5E4E; background: transparent;")
        layout.addWidget(subtitle)

        layout.addSpacing(28)

        # ── Password card ───────────────────────────────────────────────
        pwd_card = QFrame()
        pwd_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F4EE);
                border: 1px solid #BAA787;
                border-radius: 14px;
            }
        """)
        pwd_card_layout = QVBoxLayout(pwd_card)
        pwd_card_layout.setContentsMargins(24, 24, 24, 24)
        pwd_card_layout.setSpacing(0)

        password_label = QLabel("Database Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        password_label.setStyleSheet("color: #BAA787; background: transparent; letter-spacing: 1px;")
        pwd_card_layout.addWidget(password_label)
        pwd_card_layout.addSpacing(12)

        password_row = QHBoxLayout()
        password_row.setSpacing(0)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter database password")
        self.password_input.setMinimumHeight(46)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.returnPressed.connect(self.connect_database)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: none;
                border-radius: 8px 0px 0px 8px;
                background-color: rgba(186,167,135,0.12);
                color: #4D4D4D;
            }
            QLineEdit:focus {
                background-color: rgba(186,167,135,0.22);
            }
        """)
        password_row.addWidget(self.password_input, 1)

        self.show_password_btn = QPushButton("Show")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setFixedWidth(55)
        self.show_password_btn.setMinimumHeight(46)
        self.show_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_password_btn.clicked.connect(lambda checked: self.toggle_password_visibility(checked))
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(186,167,135,0.20);
                color: #BAA787;
                border: none;
                border-radius: 0px 8px 8px 0px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(186,167,135,0.45); }
            QPushButton:checked { background-color: #BAA787; color: #FFFFFF; }
        """)
        password_row.addWidget(self.show_password_btn)

        pwd_card_layout.addLayout(password_row)
        
        # File info display - separate boxes
        pwd_card_layout.addSpacing(24)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #D4C4A0; border: none; max-height: 1px;")
        divider.setFixedHeight(1)
        pwd_card_layout.addWidget(divider)

        pwd_card_layout.addSpacing(20)
        
        info_label = QLabel("Database Information")
        info_label.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        info_label.setStyleSheet("color: #BAA787; background: transparent;")
        pwd_card_layout.addWidget(info_label)
        pwd_card_layout.addSpacing(16)
        self.host_display = QLineEdit()
        self.host_display.setReadOnly(True)
        self.host_display.setPlaceholderText("Host : Port")
        self.host_display.setMinimumHeight(44)
        self.host_display.setFont(QFont("Segoe UI", 10))
        self.host_display.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                background-color: #F8F4EE;
                color: #4D4D4D;
            }
        """)
        pwd_card_layout.addWidget(self.host_display)
        
        pwd_card_layout.addSpacing(20)
        
        # Database field
        self.database_display = QLineEdit()
        self.database_display.setReadOnly(True)
        self.database_display.setPlaceholderText("Database Name")
        self.database_display.setMinimumHeight(44)
        self.database_display.setFont(QFont("Segoe UI", 10))
        self.database_display.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                background-color: #F8F4EE;
                color: #4D4D4D;
            }
        """)
        pwd_card_layout.addWidget(self.database_display)
        
        pwd_card_layout.addSpacing(20)
        
        # Username field
        self.username_display = QLineEdit()
        self.username_display.setReadOnly(True)
        self.username_display.setPlaceholderText("Username")
        self.username_display.setMinimumHeight(44)
        self.username_display.setFont(QFont("Segoe UI", 10))
        self.username_display.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                background-color: #F8F4EE;
                color: #4D4D4D;
            }
        """)
        pwd_card_layout.addWidget(self.username_display)
        
        layout.addWidget(pwd_card)

        layout.addSpacing(24)

        # ── Credentials File card ───────────────────────────────────────
        file_card = QFrame()
        file_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8F4EE);
                border: 1px solid #BAA787;
                border-radius: 14px;
            }
        """)
        file_card_layout = QVBoxLayout(file_card)
        file_card_layout.setContentsMargins(20, 18, 20, 18)
        file_card_layout.setSpacing(10)

        file_label = QLabel("Credentials File")
        file_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        file_label.setStyleSheet("color: #BAA787; background: transparent; letter-spacing: 1px;")
        file_card_layout.addWidget(file_label)

        file_row = QHBoxLayout()
        file_row.setSpacing(10)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setFixedWidth(90)
        self.browse_button.setMinimumHeight(42)
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        self.browse_button.clicked.connect(self.select_credentials_file)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #BAA787;
                color: #1A1A1A;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #D4C4A0; }
            QPushButton:pressed { background-color: #8B7355; color: #FFFFFF; }
        """)
        file_row.addWidget(self.browse_button)

        self.change_path_button = QPushButton("CHANGE PATH")
        self.change_path_button.setFixedWidth(110)
        self.change_path_button.setMinimumHeight(42)
        self.change_path_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_path_button.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
        self.change_path_button.clicked.connect(self.select_credentials_file)
        self.change_path_button.setStyleSheet("""
            QPushButton {
                background-color: #D4C4A0;
                color: #6B5E4E;
                border: 1px solid #BAA787;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #BAA787; color: #FFFFFF; }
            QPushButton:pressed { background-color: #8B7355; color: #FFFFFF; }
        """)
        self.change_path_button.setVisible(False)
        file_row.addWidget(self.change_path_button)

        file_card_layout.addLayout(file_row)
        layout.addWidget(file_card)

        layout.addSpacing(32)

        # ── Connect button ──────────────────────────────────────────────
        self.connect_button = QPushButton("CONNECT TO DATABASE")
        self.connect_button.clicked.connect(self.connect_database)
        self.connect_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.connect_button.setMinimumHeight(55)
        self.connect_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.connect_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BAA787, stop:1 #D4C4A0);
                color: #1A1A1A;
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
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
            QPushButton:disabled {
                background: #3A3A3A;
                color: #666666;
            }
        """)
        layout.addWidget(self.connect_button)

        layout.addSpacing(10)

        info_label = QLabel("Secured with enterprise-grade encryption")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setStyleSheet("color: #555555; background: transparent;")
        layout.addWidget(info_label)

        layout.addStretch(1)

    def _auto_load_saved_path(self):
        """Load the previously saved credentials file path on startup"""
        try:
            if os.path.exists(self.SAVED_PATH_FILE):
                with open(self.SAVED_PATH_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                saved = data.get('path', '')
                if saved and os.path.exists(saved):
                    self.credentials_file_path = saved
                    self.load_credentials_from_file(saved, silent=True)
        except Exception:
            pass

    def _save_credentials_path(self, filepath):
        """Persist the credentials file path for next launch"""
        try:
            with open(self.SAVED_PATH_FILE, 'w', encoding='utf-8') as f:
                json.dump({'path': filepath}, f)
        except Exception:
            pass

    def select_credentials_file(self):
        """Open file dialog to select credentials JSON file"""
        try:
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                "Select Database Credentials File",
                os.path.expanduser("~"),
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if filepath:
                self.credentials_file_path = filepath
                self._save_credentials_path(filepath)
                self.load_credentials_from_file(filepath)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error selecting file: {str(e)}")
    
    def load_credentials_from_file(self, filepath, silent=False):
        """Load credentials from the selected JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Check if file is empty
            if not content:
                self.db_credentials = {}
                self.host_display.setText("")
                self.database_display.setText("")
                self.username_display.setText("")
                self.change_path_button.setVisible(False)
                if not silent:
                    QMessageBox.warning(self, "Empty File", "The selected credentials file is empty!")
                return
            
            # Try to parse as JSON
            try:
                credentials = json.loads(content)
                
                if not isinstance(credentials, dict):
                    raise ValueError("JSON file must contain an object")
                
                # Extract required fields
                self.db_credentials = {
                    'host': credentials.get('host', ''),
                    'user': credentials.get('user', ''),
                    'database': credentials.get('database', ''),
                    'port': credentials.get('port', 3306),
                    'use_pure': credentials.get('usepure', True)
                }
                
                # Display file info in separate fields
                host = self.db_credentials.get('host', 'N/A')
                database = self.db_credentials.get('database', 'N/A')
                user = self.db_credentials.get('user', 'N/A')
                port = self.db_credentials.get('port', 3306)
                
                self.host_display.setText(f"{host}:{port}")
                self.database_display.setText(database)
                self.username_display.setText(user)
                
                # Show CHANGE FILE button
                self.change_path_button.setVisible(True)
                
                if not silent:
                    QMessageBox.information(self, "Success", "Credentials loaded successfully!\n\nNow enter the database password and click Connect.")
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {str(e)}")
        
        except Exception as e:
            self.db_credentials = {}
            self.host_display.setText("")
            self.database_display.setText("")
            self.username_display.setText("")
            self.change_path_button.setVisible(False)
            QMessageBox.critical(self, "Error", f"Error loading credentials: {str(e)}")
    
    def toggle_password_visibility(self, checked):
        """Toggle password field visibility"""
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def connect_database(self):
        """Connect to database with loaded credentials and password"""
        try:
            if not self.db_credentials:
                QMessageBox.warning(self, "Error", "Please load a credentials file first!")
                return

            password = self.password_input.text()
            if not password:
                QMessageBox.warning(self, "Error", "Please enter the database password!")
                return

            # Store credentials for database connection
            from config import DB_CONFIG
            DB_CONFIG.update({
                'host': self.db_credentials.get('host'),
                'user': self.db_credentials.get('user'),
                'password': password,
                'database': self.db_credentials.get('database'),
                'port': self.db_credentials.get('port', 3306)
            })

            # Disable connect button and show testing state
            self.connect_button.setEnabled(False)
            self.connect_button.setText("Connecting...")

            # Run the DB connection test in a background thread to avoid freezing/crashing Qt
            self._db_config_snapshot = dict(DB_CONFIG)
            self._db_thread = DBConnectThread(self._db_config_snapshot)
            self._db_thread.success.connect(self._on_connect_success)
            self._db_thread.failure.connect(self._on_connect_failure)
            self._db_thread.start()

        except Exception as e:
            traceback.print_exc()
            self.connect_button.setEnabled(True)
            self.connect_button.setText("CONNECT TO DATABASE")
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def _on_connect_success(self):
        """Called from main thread when DB connection succeeded."""
        self.connect_button.setEnabled(True)
        self.connect_button.setText("CONNECT TO DATABASE")
        QMessageBox.information(self, "Success", "Database connected successfully!")
        self.show_login_screen()
        self.hide()

    def _on_connect_failure(self, error_msg):
        """Called from main thread when DB connection failed."""
        self.connect_button.setEnabled(True)
        self.connect_button.setText("CONNECT TO DATABASE")
        QMessageBox.critical(self, "Connection Error", f"Could not connect to database:\n{error_msg}")
    
    def show_login_screen(self):
        """Show the dashboard after successful database connection"""
        try:
            from dashboard_ui import Dashboard
            
            user_data = {
                'name': 'Administrator',
                'role': 'Admin',
                'email': 'admin@system.local'
            }
            
            dashboard = Dashboard(user_data, pre_connected=True)
            
            if self.parent_app:
                self.parent_app.dashboard = dashboard
            
            dashboard.show()
        except Exception as e:
            traceback.print_exc()
            self.show()
            QMessageBox.critical(self, "Error", f"Error opening dashboard: {str(e)}")


class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.db_config = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Password Generator - Admin Login")
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
        
        layout.addSpacing(10)
        layout.setSpacing(15)
        layout.setContentsMargins(50, 40, 50, 40)
        
        layout.addStretch(1)
        
        # Title
        title = QLabel("Admin Login")
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
        email_label = QLabel("Email Address")
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
        password_label = QLabel("Password")
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
        self.show_password_btn = QPushButton("Show")
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
        
        self.login_button = QPushButton("LOGIN")
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
        info_label = QLabel("Only admin users can access the management system")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setFont(QFont("Segoe UI", 10))
        info_label.setStyleSheet("color: #7f8c8d; background: transparent;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch(1)
        
        # Security label
        security_label = QLabel("Protected by enterprise-grade encryption")
        security_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_label.setFont(QFont("Segoe UI", 9))
        security_label.setStyleSheet("color: #95a5a6; background: transparent;")
        layout.addWidget(security_label)
        
    def handle_login(self):
        try:
            email = self.email_input.text().strip()
            password = self.password_input.text()
            
            if not email or not password:
                QMessageBox.warning(self, "Error", "Please enter both email and password")
                return
            
            success, user_data = verify_admin_credentials(email, password)
            
            if success and user_data:
                from dashboard_ui import Dashboard
                self.dashboard = Dashboard(user_data)
                self.dashboard.show()
                
                self.close()
            else:
                error_msg = user_data.get('error', 'Invalid email or password') if user_data else 'Invalid email or password'
                QMessageBox.warning(self, "Login Failed", f"{error_msg}")
            
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def toggle_password_visibility(self):
        """Toggle password field visibility."""
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("Hide")
            self.show_password_btn.setToolTip("Hide password")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("Show")
            self.show_password_btn.setToolTip("Show password")