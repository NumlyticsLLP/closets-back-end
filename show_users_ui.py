"""
Show Users Screen - View all user accounts
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                              QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QHBoxLayout, 
                              QMessageBox, QFileDialog, QDialog, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from database_desktop import get_all_users, get_user_by_id, update_user_info, get_all_records_from_table, get_current_table_info, get_all_audit_records, get_user_audit_trail, get_users_with_audit_dates
import pandas as pd
import os
import json
from datetime import datetime


class AuditTrailDialog(QDialog):
    """Dialog for viewing the audit trail (Slowly Changing Dimension - Type 2)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Audit Trail - SCD Type 2")
        self.setModal(True)
        self.setMinimumSize(1200, 700)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the audit trail dialog UI."""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("📋 Complete Audit Trail - User Changes History")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background-color: transparent;")
        layout.addWidget(title)
        
        # Info label
        info_label = QLabel("🔍 Type 2 Slowly Changing Dimension - Shows all user versions and changes over time")
        info_label.setFont(QFont("Segoe UI", 10))
        info_label.setStyleSheet("color: #555555; background-color: transparent;")
        layout.addWidget(info_label)
        
        # Audit Table
        self.audit_table = QTableWidget()
        self.audit_table.setStyleSheet("""
            QTableWidget {
                border: none;
                border-radius: 12px;
                gridline-color: #e8ecef;
                background-color: white;
                color: #000000;
            }
            QTableWidget::item {
                padding: 10px;
                color: #000000;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #d4e6f1;
                color: #000000;
                border: 2px solid #3498db;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16a085, stop:1 #1abc9c);
                color: #ffffff;
                padding: 12px;
                font-weight: bold;
                border: none;
                border-radius: 0px;
            }
        """)
        self.audit_table.setSelectionBehavior(self.audit_table.SelectionBehavior.SelectRows)
        self.audit_table.setSelectionMode(self.audit_table.SelectionMode.SingleSelection)
        self.load_audit_data()
        layout.addWidget(self.audit_table, 1)
        
        # Close button
        close_btn = QPushButton("❌ CLOSE")
        close_btn.setMaximumWidth(200)
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setMinimumHeight(48)
        close_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: #000000;
                border: none;
                border-radius: 12px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #b0bec5;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
            }
        """)
        layout.addWidget(close_btn)
    
    def load_audit_data(self):
        """Load and display audit trail from users_audit table with SCD Type 2 information."""
        try:
            # Get all audit records
            df = get_all_audit_records(limit=5000)
            
            if df.empty:
                QMessageBox.information(self, "No Data", "❌ No audit records found")
                return
            
            # Set up table
            self.audit_table.setRowCount(len(df))
            
            # Define columns to display
            display_columns = ['audit_id', 'userid', 'email', 'designername', 'role', 
                             'audit_action', 'effective_start_date', 'effective_end_date', 'is_current']
            
            # Filter to only include columns that exist
            available_columns = [col for col in display_columns if col in df.columns]
            self.audit_table.setColumnCount(len(available_columns))
            self.audit_table.setHorizontalHeaderLabels(available_columns)
            
            # Populate table
            for row_idx, (_, row) in enumerate(df.iterrows()):
                for col_idx, col_name in enumerate(available_columns):
                    value = row[col_name]
                    
                    # Format values
                    if col_name == 'effective_start_date':
                        if value:
                            value = str(value)[:19]  # Trim to YYYY-MM-DD HH:MM:SS
                    elif col_name == 'effective_end_date':
                        if value:
                            value = str(value)[:19]  # Trim to YYYY-MM-DD HH:MM:SS
                        else:
                            value = "CURRENT"  # Currently active version
                    elif col_name == 'is_current':
                        value = "✅ CURRENT" if value else "📜 HISTORICAL"
                    elif col_name == 'audit_action':
                        # Color code the action with emoji
                        if value == 'INSERT':
                            value = f"✨ INSERT"
                        elif value == 'UPDATE':
                            value = f"🔄 UPDATE"
                        elif value == 'DELETE':
                            value = f"🗑️  DELETE"
                    
                    item = QTableWidgetItem(str(value))
                    item.setFont(QFont("Segoe UI", 10))
                    
                    # Color code based on is_current status
                    if col_name == 'is_current' and value == "✅ CURRENT":
                        item.setBackground(QColor("#d4edda"))  # Light green for current
                    elif col_name == 'is_current' and value == "📜 HISTORICAL":
                        item.setBackground(QColor("#fff3cd"))  # Light yellow for historical
                    
                    self.audit_table.setItem(row_idx, col_idx, item)
            
            # Auto-resize columns
            header = self.audit_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            
            # Set row height
            self.audit_table.setRowHeight(0, 30)
            
            # Calculate statistics
            current_count = len(df[df['is_current'] == 1])
            historical_count = len(df) - current_count
            insert_count = len(df[df['audit_action'] == 'INSERT'])
            update_count = len(df[df['audit_action'] == 'UPDATE'])
            delete_count = len(df[df['audit_action'] == 'DELETE'])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error loading audit data:\n\n{str(e)}")


class EditUserDialog(QDialog):
    """Dialog for editing user information."""
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("✏️ Edit User Information")
        self.setModal(True)
        self.setMinimumSize(450, 300)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the edit dialog UI."""
        # Set dialog background to white
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("Edit User Information")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background-color: transparent;")
        layout.addWidget(title)
        
        # User ID (Read-only)
        id_label = QLabel("👤 User ID:")
        id_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        id_label.setStyleSheet("color: #000000; background-color: transparent;")
        layout.addWidget(id_label)
        
        id_display = QLineEdit()
        id_display.setText(str(self.user_data['id']))
        id_display.setReadOnly(True)
        id_display.setMinimumHeight(40)
        id_display.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f5f5f5;
                color: #000000;
            }
        """)
        layout.addWidget(id_display)
        
        # Name
        name_label = QLabel("📝 Name:")
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        name_label.setStyleSheet("color: #000000; background-color: transparent;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.user_data.get('name', ''))
        self.name_input.setMinimumHeight(40)
        self.name_input.setFont(QFont("Segoe UI", 10))
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self.name_input)
        
        # Email
        email_label = QLabel("📧 Email:")
        email_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        email_label.setStyleSheet("color: #000000; background-color: transparent;")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setText(self.user_data.get('email', ''))
        self.email_input.setMinimumHeight(40)
        self.email_input.setFont(QFont("Segoe UI", 10))
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #0066cc;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self.email_input)
        
        # Role
        role_label = QLabel("🔐 Role:")
        role_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        role_label.setStyleSheet("color: #000000; background-color: transparent;")
        layout.addWidget(role_label)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setCurrentText(self.user_data.get('role', 'user'))
        self.role_combo.setMinimumHeight(40)
        self.role_combo.setFont(QFont("Segoe UI", 10))
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QComboBox:focus {
                border: 2px solid #0066cc;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #e0e0e0;
            }
        """)
        layout.addWidget(self.role_combo)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #b3b3b3;
            }
            QPushButton:pressed {
                background-color: #999999;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("✅ Save Changes")
        save_btn.setMinimumHeight(40)
        save_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def get_data(self):
        """Return the edited data."""
        return {
            'id': self.user_data['id'],
            'name': self.name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'role': self.role_combo.currentText()
        }


class ShowUsersScreen(QWidget):
    CONFIG_FILE = "download_path_config.json"
    
    def __init__(self):
        super().__init__()
        # Note: Using hardcoded users table (no custom tables)
        self.original_df = None  # Initialize dataframe for filtering
        self.init_ui()
    
    def load_saved_path(self):
        """Load saved download path from config file."""
        try:
            if os.path.exists(self.CONFIG_FILE):
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('download_path', os.path.expanduser("~"))
        except:
            pass
        return os.path.expanduser("~")
    
    def save_path(self, path):
        """Save download path to config file."""
        try:
            config = {'download_path': path}
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except:
            pass

    def init_ui(self):
        self.setWindowTitle("👥 All Users")
        self.setMinimumSize(900, 600)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Top section with Logo
        top_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "Logo 1.png")
        if os.path.exists(logo_path):
            logo = QPixmap(logo_path)
            scaled_logo = logo.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Title
        title = QLabel("👥 All Users")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Search:")
        search_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        search_label.setStyleSheet("color: #2c3e50; background: transparent;")
        search_label.setMinimumWidth(80)
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, name or email...")
        self.search_input.setMinimumHeight(46)
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid #C5B39F;
                border-radius: 12px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:hover {
                border: 2px solid #BCAA8D;
                background-color: #fdfaf7;
            }
            QLineEdit:focus {
                border: 2px solid #BCAA8D;
                background-color: #ffffff;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input, 1)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                border-radius: 12px;
                gridline-color: #e8ecef;
                background-color: white;
                color: #000000;
            }
            QTableWidget::item {
                padding: 12px;
                color: #000000;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #d4e6f1;
                color: #000000;
                border: 2px solid #3498db;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BCAA8D, stop:1 #D0BFA1);
                color: #ffffff;
                padding: 14px;
                font-weight: bold;
                border: none;
                border-radius: 0px;
            }
        """)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.setRowHeight(0, 60)  # Increase row height for better readability
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)
        self.load_users()
        layout.addWidget(self.table, 1)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Edit button
        edit_btn = QPushButton("✏️ EDIT USER")
        edit_btn.setMaximumWidth(200)
        edit_btn.clicked.connect(self.edit_selected_user)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setMinimumHeight(52)
        edit_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        button_layout.addWidget(edit_btn)
        
        # Change Path button
        change_path_btn = QPushButton("📂 CHANGE PATH")
        change_path_btn.setMaximumWidth(200)
        change_path_btn.clicked.connect(self.change_download_path)
        change_path_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_path_btn.setMinimumHeight(52)
        change_path_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        change_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #5dade2;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(change_path_btn)
        
        # Download CSV button
        download_btn = QPushButton("📥 DOWNLOAD CSV")        
        download_btn.setMaximumWidth(220)        
        download_btn.clicked.connect(self.download_csv)
        download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        download_btn.setMinimumHeight(52)
        download_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        download_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BCAA8D, stop:1 #D0BFA1);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #D0BFA1, stop:1 #E4D5C1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #A89673, stop:1 #BCAA8D);
            }
        """)
        button_layout.addWidget(download_btn)
        
        # Audit Trail button
        audit_btn = QPushButton("📋 AUDIT TRAIL")
        audit_btn.setMaximumWidth(220)
        audit_btn.clicked.connect(self.show_audit_trail)
        audit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        audit_btn.setMinimumHeight(52)
        audit_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        audit_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
            QPushButton:pressed {
                background-color: #117a65;
            }
        """)
        button_layout.addWidget(audit_btn)
        
        # Close button
        close_btn = QPushButton("❌ CLOSE")        
        close_btn.setMaximumWidth(200)        
        close_btn.clicked.connect(self.close)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setMinimumHeight(52)
        close_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        close_btn.setStyleSheet("""
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
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def format_date(self, date_value):
        """Format date to readable format with detailed time info."""
        try:
            if date_value is None or str(date_value) == 'NaT':
                return "N/A"
            
            # Convert to datetime if string
            if isinstance(date_value, str):
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00') if 'T' in date_value else date_value)
            else:
                date_obj = date_value
            
            # Calculate difference
            now = datetime.now(date_obj.tzinfo) if date_obj.tzinfo else datetime.now()
            diff = now - date_obj
            
            # Format time and date
            time_str = date_obj.strftime('%H:%M')
            date_str = date_obj.strftime('%Y-%m-%d')
            
            # Return formatted string with relative time and actual date/time
            if diff.days == 0:
                return f"Today at {time_str} ({date_str})"
            elif diff.days == 1:
                return f"1 day ago at {time_str} ({date_str})"
            elif diff.days < 7:
                return f"{diff.days} days ago at {time_str} ({date_str})"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"{weeks} week{'s' if weeks > 1 else ''} ago at {time_str} ({date_str})"
            else:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago at {time_str} ({date_str})"
        except Exception as e:
            return str(date_value)

    def format_updated_date(self, date_value):
        """Format updated date with detailed time info."""
        try:
            if date_value is None or str(date_value) == 'NaT':
                return "Never Updated"
            
            # Convert to datetime if string
            if isinstance(date_value, str):
                date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00') if 'T' in date_value else date_value)
            else:
                date_obj = date_value
            
            # Calculate difference
            now = datetime.now(date_obj.tzinfo) if date_obj.tzinfo else datetime.now()
            diff = now - date_obj
            
            # Format time and date
            time_str = date_obj.strftime('%H:%M')
            date_str = date_obj.strftime('%Y-%m-%d')
            
            # Return formatted string with special indicator for recent updates and detailed time info
            if diff.days == 0:
                return f"Recently updated at {time_str} (Today {date_str})"
            elif diff.days == 1:
                return f"Updated 1 day ago at {time_str} ({date_str})"
            elif diff.days < 7:
                return f"Updated {diff.days} days ago at {time_str} ({date_str})"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"Updated {weeks} week{'s' if weeks > 1 else ''} ago at {time_str} ({date_str})"
            else:
                months = diff.days // 30
                return f"Updated {months} month{'s' if months > 1 else ''} ago at {time_str} ({date_str})"
        except Exception as e:
            return str(date_value)
    
    def load_users(self):
        """Load users from audit table with aggregated created and updated dates."""
        # Clear any existing table data first
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        # Load from users_audit table with aggregated dates
        df = get_users_with_audit_dates()
        
        if df.empty:
            print("DEBUG load_users: DataFrame is empty!")
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("No data found"))
            return
        
        print(f"DEBUG load_users: Loaded {len(df)} current users, Columns: {list(df.columns)}")
        
        # Store original DataFrame for filtering
        self.original_df = df.copy()
        print(f"DEBUG load_users: original_df set with {len(self.original_df)} rows")
        
        # Sort by userid in descending order (newest first)
        df = df.sort_values('userid', ascending=False)
        df = df.reset_index(drop=True)  # Reset index to sequential for proper table population
        
        # Format date columns - created_date and updated_date
        if 'created_date' in df.columns:
            try:
                df['created_date'] = df['created_date'].apply(self.format_date)
            except:
                pass
        
        if 'updated_date' in df.columns:
            try:
                df['updated_date'] = df['updated_date'].apply(self.format_updated_date)
            except:
                pass
        
        # Filter out columns we don't want to display in the UI
        columns_to_hide = ['audit_user', 'effective_start_date', 'effective_end_date', 'audit_action']
        display_df = df.drop(columns=[col for col in columns_to_hide if col in df.columns])
        
        # Set up table - clear completely first
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        # Now set proper dimensions
        self.table.setColumnCount(len(display_df.columns))
        self.table.setHorizontalHeaderLabels(display_df.columns)
        self.table.setRowCount(len(display_df))
        
        # Populate table - use enumerate to ensure sequential row indices
        for row_idx, (_, row) in enumerate(display_df.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # Allow text wrapping for better visibility
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)
        
        # Adjust column widths for better readability
        header = self.table.horizontalHeader()
        # Auto-adjust column widths
        for col_idx in range(len(display_df.columns)):
            header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Stretch)
            # Set wider width for date/timestamp columns
            if 'created' in display_df.columns[col_idx].lower() or 'updated' in display_df.columns[col_idx].lower():
                self.table.setColumnWidth(col_idx, 320)
            else:
                self.table.setColumnWidth(col_idx, 150)
        
        # Set uniform row height for all rows
        self.table.verticalHeader().setDefaultSectionSize(60)
    
    def on_cell_double_clicked(self, row, column):
        """Handle double-click on table cell to edit user."""
        self.edit_user_at_row(row)
    
    def edit_selected_user(self):
        """Edit the selected user from table."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "⚠️ No Selection", "Please select a user to edit")
            return
        
        row = selected_rows[0].row()
        self.edit_user_at_row(row)
    
    def edit_user_at_row(self, row):
        """Edit user at specified row."""
        try:
            # Get userid from the audit table row
            # The table shows audit data, so we need to find userid column
            if self.original_df is None or self.original_df.empty:
                QMessageBox.critical(self, "❌ Error", "No user data loaded")
                return
            
            # Get the row from the original_df (which is already sorted and indexed)
            if row >= len(self.original_df):
                QMessageBox.critical(self, "❌ Error", "Invalid row selection")
                return
            
            # Get userid from the current row in original_df
            user_row = self.original_df.iloc[row]
            
            if 'userid' not in self.original_df.columns:
                QMessageBox.critical(self, "❌ Error", "Could not find userid column in data")
                return
            
            user_id = int(user_row['userid'])
            print(f"DEBUG: Editing user with ID {user_id} from row {row}")
            
            # Get user data from users table
            user_data = get_user_by_id(user_id)
            if not user_data:
                QMessageBox.critical(self, "❌ Error", f"Could not retrieve user information for ID {user_id}")
                return
            
            # Show edit dialog
            dialog = EditUserDialog(self, user_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                edit_data = dialog.get_data()
                
                # Validate input
                if not edit_data['name'].strip():
                    QMessageBox.warning(self, "⚠️ Invalid Input", "Name cannot be empty")
                    return
                
                if not edit_data['email'].strip():
                    QMessageBox.warning(self, "⚠️ Invalid Input", "Email cannot be empty")
                    return
                
                # Update user in database
                success, message = update_user_info(
                    edit_data['id'],
                    edit_data['name'],
                    edit_data['email'],
                    edit_data['role']
                )
                
                if success:
                    QMessageBox.information(self, "✅ Success", message)
                    # Reload the table
                    self.load_users()
                    # Clear search filter
                    self.search_input.clear()
                else:
                    QMessageBox.critical(self, "❌ Error", message)
        
        except ValueError as e:
            QMessageBox.critical(self, "❌ Error", f"Invalid user ID format:\n\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Failed to edit user:\n\n{str(e)}")
    
    def change_download_path(self):
        """Allow user to change the default download path."""
        current_path = self.load_saved_path()
        
        download_dir = QFileDialog.getExistingDirectory(
            self,
            "📁 Select New Default Download Folder",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if download_dir:
            self.save_path(download_dir)
            QMessageBox.information(self, "Success", 
                f"✅ Default download path updated!\n\n"
                f"📂 New path:\n{download_dir}")
    
    def download_csv(self):
        """Download all users data as CSV file with formatted dates as shown in UI."""
        # Use the original_df which has formatted dates
        if not hasattr(self, 'original_df') or self.original_df.empty:
            QMessageBox.warning(self, "Error", "⚠️ No users to download")
            return
        
        # Use saved path as default
        default_path = self.load_saved_path()
        
        # Ask user to select download directory
        download_dir = QFileDialog.getExistingDirectory(
            self,
            "📁 Select Download Folder",
            default_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not download_dir:
            return  # User cancelled
        
        # Save this path for future use
        self.save_path(download_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_users_{timestamp}.csv"
        filepath = os.path.join(download_dir, filename)
        
        try:
            # Use original_df which has formatted dates as shown in UI
            self.original_df.to_csv(filepath, index=False)
            QMessageBox.information(self, "Success", 
                f"✅ Users data downloaded successfully!\n\n"
                f"📂 Saved to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"❌ Failed to download CSV:\n\n{str(e)}")
    
    def filter_table(self, text):
        """Filter table by name or ID - shows message if search doesn't match any users."""
        # Debug: Check if original_df is available
        if self.original_df is None:
            print("DEBUG: original_df is None")
            return
        
        if self.original_df.empty:
            print("DEBUG: original_df is empty")
            return
        
        text = text.strip()
        text_lower = text.lower()
        
        print(f"DEBUG: Searching for '{text}', Columns: {list(self.original_df.columns)}")
        
        # Apply filtering
        if text:
            # Check if search is numeric (ID search)
            is_numeric = text.isdigit()
            print(f"DEBUG: Is numeric: {is_numeric}")
            
            if is_numeric:
                # Search by exact userid match (audit table uses 'userid')
                if 'userid' in self.original_df.columns:
                    filtered_df = self.original_df[self.original_df['userid'].astype(str) == text]
                    print(f"DEBUG: Found {len(filtered_df)} results with userid={text}")
                else:
                    print("DEBUG: No userid column found")
                    filtered_df = pd.DataFrame()
            else:
                # Search by designername (audit table uses 'designername')
                if 'designername' in self.original_df.columns:
                    filtered_df = self.original_df[self.original_df['designername'].astype(str).str.lower().str.contains(text_lower, na=False, regex=False)]
                    print(f"DEBUG: Found {len(filtered_df)} results with designername containing '{text}'")
                else:
                    print("DEBUG: No designername column found")
                    filtered_df = pd.DataFrame()
        else:
            # Show all when search is empty
            filtered_df = self.original_df.copy()
            print(f"DEBUG: Empty search, showing all {len(filtered_df)} users")
        
        # Handle empty results
        if filtered_df.empty:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(['Result'])
            no_result = QTableWidgetItem('❌ No matching users found')
            no_result.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(0, 0, no_result)
            return
        
        # Sort by userid in descending order (newest first)
        if 'userid' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('userid', ascending=False)
        
        filtered_df = filtered_df.reset_index(drop=True)  # Reset index to sequential
        
        # Filter out columns we don't want to display in the UI
        columns_to_hide = ['audit_user', 'effective_start_date', 'effective_end_date', 'audit_action']
        display_filtered_df = filtered_df.drop(columns=[col for col in columns_to_hide if col in filtered_df.columns])
        
        # Clear and repopulate table
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
        # Now set proper dimensions
        self.table.setColumnCount(len(display_filtered_df.columns))
        self.table.setHorizontalHeaderLabels(display_filtered_df.columns)
        self.table.setRowCount(len(display_filtered_df))
        
        # Populate filtered data
        for row_idx, (_, row) in enumerate(display_filtered_df.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, col_idx, item)
        
        # Adjust column widths
        header = self.table.horizontalHeader()
        for col_idx in range(len(display_filtered_df.columns)):
            header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Stretch)
        
        print(f"DEBUG: Table updated with {len(filtered_df)} rows")
    
    def sort_by_column(self, column_index):
        """Sort table by clicked column header."""
        if self.original_df is None or self.original_df.empty:
            return
        
        # Get column name from table header
        column_name = self.table.horizontalHeaderItem(column_index).text()
        
        # Toggle sort order (ascending/descending)
        if not hasattr(self, 'current_sort_column'):
            self.current_sort_column = column_name
            self.current_sort_ascending = True
        elif self.current_sort_column == column_name:
            # Same column clicked, toggle sort order
            self.current_sort_ascending = not self.current_sort_ascending
        else:
            # Different column, start with ascending
            self.current_sort_column = column_name
            self.current_sort_ascending = True
        
        # Sort the original dataframe
        try:
            sorted_df = self.original_df.sort_values(by=column_name, ascending=self.current_sort_ascending)
            sorted_df = sorted_df.reset_index(drop=True)
            
            # Filter out columns we don't want to display in the UI
            columns_to_hide = ['audit_user', 'effective_start_date', 'effective_end_date', 'audit_action']
            display_sorted_df = sorted_df.drop(columns=[col for col in columns_to_hide if col in sorted_df.columns])
            
            # Clear and repopulate table
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.table.setColumnCount(len(display_sorted_df.columns))
            self.table.setHorizontalHeaderLabels(display_sorted_df.columns)
            self.table.setRowCount(len(display_sorted_df))
            
            # Populate sorted data
            for row_idx, (_, row) in enumerate(display_sorted_df.iterrows()):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row_idx, col_idx, item)
            
            # Adjust column widths
            header = self.table.horizontalHeader()
            for col_idx in range(len(display_sorted_df.columns)):
                header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Stretch)
            
            print(f"DEBUG: Sorted by {column_name} ({'ascending' if self.current_sort_ascending else 'descending'})")
        except Exception as e:
            print(f"DEBUG: Error sorting by {column_name}: {e}")
    
    def show_audit_trail(self):
        """Display the audit trail (users_audit table) in a new dialog."""
        # Create audit dialog
        audit_dialog = AuditTrailDialog(parent=self)
        audit_dialog.exec()

