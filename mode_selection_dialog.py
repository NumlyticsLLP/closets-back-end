"""
Mode Selection Dialog - Choose Test or Production mode at startup
"""

import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QMessageBox, QFrame, QApplication, QComboBox, QStyledItemDelegate)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSignal as Signal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt6.QtCore import QRect
from database_desktop import fetch_database_tables, fetch_table_columns


class ComboBoxItemDelegate(QStyledItemDelegate):
    """Custom delegate for combo box items to ensure proper text visibility."""
    
    def paint(self, painter, option, index):
        """Paint the combo box item with explicit black text."""
        # Set text color to black for all states
        option.palette.setColor(option.palette.ColorRole.Text, QColor("#000000"))
        option.palette.setColor(option.palette.ColorRole.ButtonText, QColor("#000000"))
        
        # Set highlight colors
        option.palette.setColor(option.palette.ColorRole.HighlightedText, QColor("#ffffff"))
        option.palette.setColor(option.palette.ColorRole.Highlight, QColor("#3498db"))
        
        # Draw with modified palette
        super().paint(painter, option, index)


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
        icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # Fallback to PNG if ICO not found
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
            scaled_logo = logo.scaledToHeight(110, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Header
        header_label = QLabel("🚀 Select Application Mode")
        header_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #000000; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Choose the environment mode and database configuration:")
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #000000; margin-bottom: 20px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Container for mode frames with horizontal centering
        frames_container = QVBoxLayout()
        frames_container.setSpacing(10)
        
        # Test Mode Frame
        self.create_mode_frame(
            frames_container,
            "🧪 TEST MODE",
            "Development and testing environment",
            "#e8f5e8",
            "#27ae60",
            "test"
        )
        
        # Production Mode Frame
        self.create_mode_frame(
            frames_container,
            "🏭 PRODUCTION MODE", 
            "Live production environment",
            "#fff3e0",
            "#e67e22",
            "production"
        )
        
        # Wrap frames container in horizontal centering layout
        frames_h_layout = QHBoxLayout()
        frames_h_layout.addStretch(1)
        frames_h_layout.addLayout(frames_container)
        frames_h_layout.addStretch(1)
        layout.addLayout(frames_h_layout)
        
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
        frame.setMaximumWidth(550)
        
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
        desc_label.setStyleSheet("color: #000000;")
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
        
        # Also save session configuration with table info
        session_config_file = f"session_table_config_{mode}.json"
        session_config = {
            'mode': mode,
            'connection_string': config.get('connection_string', ''),
            'username': config.get('username', ''),
            'password': config.get('password', ''),
            'database': config.get('database', ''),
            'table': config.get('table', ''),
            'columns': config.get('columns', [])
        }
        
        try:
            with open(session_config_file, 'w') as f:
                json.dump(session_config, f, indent=2)
        except Exception as e:
            print(f"Could not save session configuration: {e}")
    
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
        
        # Initialize column info dictionary
        self.table_columns_info = {}
        self.connection_string = ""
        self.username = ""
        self.password = ""
        
        self.setup_ui()
        self.load_saved_config()
        
    def setup_ui(self):
        """Setup the database configuration UI."""
        self.setMinimumSize(520, 550)
        self.resize(520, 550)
        self.setSizeGripEnabled(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        mode_icon = "🧪" if self.mode == "test" else "🏭"
        header_label = QLabel(f"{mode_icon} {self.mode.title()} Database Configuration")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #000000; margin-bottom: 15px;")
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
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                color: #000000;
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
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                color: #000000;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password
        pass_label = QLabel("🔐 Database Password:")
        pass_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        pass_label.setStyleSheet("color: #000000;")
        layout.addWidget(pass_label)
        
        # Password field with eye button
        password_container = QHBoxLayout()
        password_container.setSpacing(0)
        password_container.setContentsMargins(0, 0, 0, 0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Database password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setFont(QFont("Segoe UI", 10))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #3498db;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                color: #000000;
            }
        """)
        password_container.addWidget(self.password_input, 1)
        
        # Eye button for show/hide password
        self.show_password_btn = QPushButton("👁️")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setMaximumWidth(40)
        self.show_password_btn.setMinimumHeight(40)
        self.show_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #000000;
                border: none;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-radius: 4px;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """)
        password_container.addWidget(self.show_password_btn)
        
        layout.addLayout(password_container)
        
        # Table Selection Section
        table_label = QLabel("📊 Select Database Table:")
        table_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        table_label.setStyleSheet("color: #000000; margin-top: 15px;")
        layout.addWidget(table_label)
        
        # Table selection with fetch button
        table_container = QHBoxLayout()
        table_container.setSpacing(8)
        table_container.setContentsMargins(0, 0, 0, 0)
        
        self.table_combo = QComboBox()
        self.table_combo.setMinimumHeight(40)
        self.table_combo.setMaximumHeight(50)
        self.table_combo.setFont(QFont("Segoe UI", 10))
        self.table_combo.addItem("-- Select a table --")
        self.table_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
                color: #000000;
            }
            QComboBox:!editable {
                color: #000000;
                background-color: #ffffff;
            }
        """)
        
        # Configure the view for better dropdown display
        self._configure_combo_view(self.table_combo)
        table_container.addWidget(self.table_combo, 1)
        
        fetch_btn = QPushButton("🔄 Fetch Tables")
        fetch_btn.setMinimumHeight(40)
        fetch_btn.setMaximumWidth(140)
        fetch_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fetch_btn.clicked.connect(self.fetch_tables_from_database)
        fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
        """)
        table_container.addWidget(fetch_btn)
        
        layout.addLayout(table_container)
        
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
    
    def show_message_box(self, msg_type, title, text):
        """Show a message box with proper text visibility."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        
        # Set text color to black for better visibility
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #000000;
            }
            QMessageBox QPushButton {
                color: #ffffff;
                background-color: #3498db;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        if msg_type == "information":
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        elif msg_type == "critical":
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        msg_box.exec()
    
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
    
    def _configure_combo_view(self, combo_box):
        """Configure the combo box view for proper text visibility."""
        # Apply the delegate
        delegate = ComboBoxItemDelegate()
        combo_box.setItemDelegate(delegate)
        
        # Get and configure the view
        view = combo_box.view()
        if view:
            view.setMinimumHeight(200)
            view.setMinimumWidth(350)
            
            # Apply stylesheet to view
            view.setStyleSheet("""
                QAbstractItemView {
                    background-color: #ffffff;
                    color: #000000;
                    selection-background-color: #3498db;
                    selection-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 5px;
                }
                QAbstractItemView::item {
                    padding: 5px;
                    min-height: 25px;
                    color: #000000;
                    background-color: #ffffff;
                }
                QAbstractItemView::item:selected {
                    background-color: #3498db;
                    color: #ffffff;
                }
                QAbstractItemView::item:hover {
                    background-color: #d1e7f0;
                }
            """)
            
            # Configure palette
            palette = view.palette()
            palette.setColor(palette.ColorRole.Text, QColor("#000000"))
            palette.setColor(palette.ColorRole.Base, QColor("#ffffff"))
            palette.setColor(palette.ColorRole.Highlight, QColor("#3498db"))
            palette.setColor(palette.ColorRole.HighlightedText, QColor("#ffffff"))
            palette.setColor(palette.ColorRole.ButtonText, QColor("#000000"))
            view.setPalette(palette)
            
            # Ensure the item delegate is set on the view
            view.setItemDelegate(delegate)
    
    def fetch_tables_from_database(self):
        """Fetch tables from the database using the provided credentials."""
        connection_string = self.connection_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not connection_string:
            self.show_message_box("warning", "Error", "Please enter a connection string first")
            return
        
        if not username:
            self.show_message_box("warning", "Error", "Please enter a username first")
            return
        
        if not password:
            self.show_message_box("warning", "Error", "Please enter a password first")
            return
        
        # Show loading state
        self.table_combo.clear()
        self.table_combo.addItem("⏳ Loading tables...")
        self.table_combo.setEnabled(False)
        
        try:
            # Fetch tables from database
            tables = fetch_database_tables(connection_string, username, password)
            
            if tables:
                self.table_combo.clear()
                self.table_combo.addItem("-- Select a table --")
                for table in sorted(tables):
                    self.table_combo.addItem(table)
                # Ensure delegate and view configuration is applied after adding items
                self.table_combo.setItemDelegate(ComboBoxItemDelegate())
                self._configure_combo_view(self.table_combo)
                self.table_combo.setEnabled(True)
                
                # Store connection details and table columns for later use
                self.connection_string = connection_string
                self.username = username
                self.password = password
                self.table_columns_info = {}
                
                # Fetch columns for each table
                for table in tables:
                    columns = fetch_table_columns(connection_string, username, password, table)
                    self.table_columns_info[table] = columns
                
                self.show_message_box("information", "Success", f"Found {len(tables)} table(s) in the database")
            else:
                self.table_combo.clear()
                self.table_combo.addItem("No tables found")
                self.table_combo.setEnabled(False)
                self.show_message_box("warning", "No Tables", "No tables found in the specified database. Please check your credentials and database name.")
        except Exception as e:
            self.table_combo.clear()
            self.table_combo.addItem("Error fetching tables")
            self.table_combo.setEnabled(False)
            self.show_message_box("critical", "Connection Error", f"Failed to fetch tables:\n{str(e)}")
    
    def validate_and_accept(self):
        """Validate input and accept dialog."""
        connection_string = self.connection_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        selected_table = self.table_combo.currentText().strip()
        
        if not connection_string:
            self.show_message_box("warning", "Error", "Please enter a connection string")
            return
        
        if not username:
            self.show_message_box("warning", "Error", "Please enter a username")
            return
        
        if not password:
            self.show_message_box("warning", "Error", "Please enter a password")
            return
        
        if not selected_table or selected_table.startswith("--") or selected_table in ["No tables found", "Error fetching tables", "⏳ Loading tables..."]:
            self.show_message_box("warning", "Error", "Please select a valid table from the database")
            return
        
        self.accept()
    
    def get_configuration(self):
        """Get the configuration data."""
        selected_table = self.table_combo.currentText().strip()
        selected_columns = []
        
        # Get columns for the selected table if available
        if hasattr(self, 'table_columns_info') and selected_table in self.table_columns_info:
            selected_columns = self.table_columns_info[selected_table]
        
        return {
            'connection_string': self.connection_input.text().strip(),
            'username': self.username_input.text().strip(),
            'password': self.password_input.text().strip(),
            'table': selected_table,
            'columns': selected_columns,
            'database': self.connection_input.text().strip().split('/')[-1]  # Extract database name
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
                    
                    # Load selected table if available
                    saved_table = config.get('table', '')
                    if saved_table:
                        # Try to fetch tables and select the saved one
                        connection_string = config.get('connection_string', '')
                        username = config.get('username', '')
                        password = config.get('password', '')
                        
                        if connection_string and username and password:
                            try:
                                tables = fetch_database_tables(connection_string, username, password)
                                if tables:
                                    self.table_combo.clear()
                                    self.table_combo.addItem("-- Select a table --")
                                    for table in sorted(tables):
                                        self.table_combo.addItem(table)
                                    # Ensure delegate and view configuration is applied after adding items
                                    self.table_combo.setItemDelegate(ComboBoxItemDelegate())
                                    self._configure_combo_view(self.table_combo)
                                    # Select the saved table
                                    index = self.table_combo.findText(saved_table)
                                    if index >= 0:
                                        self.table_combo.setCurrentIndex(index)
                            except:
                                pass  # Silently fail to load saved table
            except:
                pass