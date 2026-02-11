"""
Mode Selection Dialog - Choose Test or Production mode at startup
"""

import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QMessageBox, QFrame, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap


class ModeSelectionDialog(QDialog):
    # Signal emitted when mode is selected: (mode, connection_string, username, password)
    mode_selected = pyqtSignal(str, str, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mode Selection")
        self.setModal(True)
        self.selected_mode = None
        self.connection_data = {}
        
        # Make dialog resizable
        self.setSizeGripEnabled(True)
        
        self.setup_ui()
        self.load_saved_configurations()
        
    def setup_ui(self):
        """Setup the mode selection UI."""
        self.setMinimumSize(650, 500)
        self.resize(650, 500)
        self.setStyleSheet("""
            QDialog {
                background: #ffffff;
            }
        """)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "Logo without text.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Top section with Logo
        top_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "Logo 1.png")
        if os.path.exists(logo_path):
            logo = QPixmap(logo_path)
            scaled_logo = logo.scaledToHeight(70, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Header
        header_label = QLabel("🚀 Select Application Mode")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Choose the environment mode and database configuration:")
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #34495e; margin-bottom: 20px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Test Mode Frame
        self.create_mode_frame(
            layout,
            "🧪 TEST MODE",
            "Development and testing environment",
            "#e8f5e8",
            "#27ae60",
            "test"
        )
        
        layout.addSpacing(10)
        
        # Production Mode Frame
        self.create_mode_frame(
            layout,
            "🏭 PRODUCTION MODE", 
            "Live production environment",
            "#fff3e0",
            "#e67e22",
            "production"
        )
        
        layout.addStretch()
        
        # Exit button
        exit_layout = QHBoxLayout()
        exit_layout.addStretch()
        
        exit_btn = QPushButton("❌ Exit Application")
        exit_btn.setFont(QFont("Segoe UI", 10))
        exit_btn.setMinimumHeight(40)
        exit_btn.setMaximumWidth(150)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        exit_btn.clicked.connect(self.close_application)
        
        exit_layout.addWidget(exit_btn)
        exit_layout.addStretch()
        layout.addLayout(exit_layout)
        
    def create_mode_frame(self, parent_layout, title, description, bg_color, accent_color, mode):
        """Create a mode selection frame."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {accent_color};
                border-radius: 12px;
                padding: 20px;
                margin: 5px;
            }}
            QFrame:hover {{
                border: 3px solid {accent_color};
            }}
        """)
        frame.setMinimumHeight(140)
        frame.setMinimumWidth(550)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {accent_color}; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        frame_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #34495e;")
        desc_label.setWordWrap(True)
        desc_label.setMinimumHeight(30)
        frame_layout.addWidget(desc_label)
        
        # Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        select_btn = QPushButton("Configure & Select")
        select_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        select_btn.setMinimumHeight(40)
        select_btn.setMinimumWidth(160)
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {accent_color};
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                background-color: {accent_color};
                opacity: 0.7;
            }}
        """)
        select_btn.clicked.connect(lambda: self.configure_mode(mode))
        
        btn_layout.addWidget(select_btn)
        frame_layout.addLayout(btn_layout)
        
        parent_layout.addWidget(frame)
        
    def configure_mode(self, mode):
        """Show configuration dialog for the selected mode."""
        dialog = DatabaseConfigDialog(self, mode)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_configuration()
            self.selected_mode = mode
            self.connection_data = config
            
            # Save configuration
            self.save_configuration(mode, config)
            
            # Emit signal and accept
            self.mode_selected.emit(
                mode,
                config['connection_string'],
                config['username'],
                config['password']
            )
            self.accept()
    
    def close_application(self):
        """Close the entire application."""
        QApplication.quit()
    
    def save_configuration(self, mode, config):
        """Save mode configuration for future use."""
        config_file = "mode_configurations.json"
        configurations = {}
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    configurations = json.load(f)
            except:
                pass
        
        configurations[mode] = config
        
        try:
            with open(config_file, 'w') as f:
                json.dump(configurations, f, indent=2)
        except Exception as e:
            print(f"Could not save configuration: {e}")
    
    def load_saved_configurations(self):
        """Load previously saved configurations."""
        config_file = "mode_configurations.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}


class DatabaseConfigDialog(QDialog):
    """Database configuration dialog for each mode."""
    
    def __init__(self, parent=None, mode="test"):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle(f"Configure {mode.title()} Database")
        self.setModal(True)
        
        self.setup_ui()
        self.load_saved_config()
        
    def setup_ui(self):
        """Setup the database configuration UI."""
        self.setMinimumSize(520, 450)
        self.resize(520, 450)
        self.setSizeGripEnabled(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        mode_icon = "🧪" if self.mode == "test" else "🏭"
        header_label = QLabel(f"{mode_icon} {self.mode.title()} Database Configuration")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Connection String
        conn_label = QLabel("🔗 Database Connection String:")
        conn_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        conn_label.setStyleSheet("color: #000000;")
        layout.addWidget(conn_label)
        
        self.connection_input = QLineEdit()
        self.connection_input.setPlaceholderText("e.g., localhost:3306/database_name")
        self.connection_input.setMinimumHeight(40)
        self.connection_input.setFont(QFont("Segoe UI", 10))
        self.connection_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.connection_input)
        
        # Username
        user_label = QLabel("👤 Database Username:")
        user_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        user_label.setStyleSheet("color: #000000;")
        layout.addWidget(user_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Database username")
        self.username_input.setMinimumHeight(40)
        self.username_input.setFont(QFont("Segoe UI", 10))
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password
        pass_label = QLabel("🔐 Database Password:")
        pass_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        pass_label.setStyleSheet("color: #000000;")
        layout.addWidget(pass_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Database password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setFont(QFont("Segoe UI", 10))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.password_input)
        
        # Show password checkbox
        self.show_password_btn = QPushButton("👁️ Show Password")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setMaximumWidth(120)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:checked {
                background-color: #e74c3c;
            }
        """)
        layout.addWidget(self.show_password_btn)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton(f"✅ Save & Use {self.mode.title()}")
        save_btn.setMinimumHeight(40)
        color = "#27ae60" if self.mode == "test" else "#e67e22"
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        save_btn.clicked.connect(self.validate_and_accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_password_visibility(self):
        """Toggle password field visibility."""
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈 Hide Password")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁️ Show Password")
    
    def validate_and_accept(self):
        """Validate input and accept dialog."""
        connection_string = self.connection_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not connection_string:
            QMessageBox.warning(self, "Error", "Please enter a connection string")
            return
        
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username")
            return
        
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return
        
        self.accept()
    
    def get_configuration(self):
        """Get the configuration data."""
        return {
            'connection_string': self.connection_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text().strip()
        }
    
    def load_saved_config(self):
        """Load saved configuration for this mode."""
        config_file = "mode_configurations.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    configurations = json.load(f)
                
                if self.mode in configurations:
                    config = configurations[self.mode]
                    self.connection_input.setText(config.get('connection_string', ''))
                    self.username_input.setText(config.get('username', ''))
                    self.password_input.setText(config.get('password', ''))
            except:
                pass