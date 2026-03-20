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
from utils import resource_path
import pandas as pd
import os
import json
from datetime import datetime


class AuditTrailDialog(QDialog):
    """Dialog for viewing the audit trail (Slowly Changing Dimension - Type 2)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audit Trail - SCD Type 2")
        self.setModal(True)
        self.setMinimumSize(1200, 700)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the audit trail dialog UI."""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("Complete Audit Trail - User Changes History")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #8B7355; background-color: transparent; letter-spacing: 1px;")
        layout.addWidget(title)
        
        # Info label
        #info_label = QLabel("Type 2 Slowly Changing Dimension - Shows all user versions and changes over time")
        #info_label.setFont(QFont("Segoe UI", 10))
        #info_label.setStyleSheet("color: #6B5E4E; background-color: transparent;")
        #layout.addWidget(info_label)
        
        # Audit Table
        self.audit_table = QTableWidget()
        self.audit_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                gridline-color: #EDE8E0;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QTableWidget::item {
                padding: 10px;
                color: #4D4D4D;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: rgba(186,167,135,0.20);
                color: #4D4D4D;
                border: 1px solid #BAA787;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F4EE, stop:1 #EDE8E0);
                color: #8B7355;
                padding: 12px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #BAA787;
            }
        """)
        self.audit_table.setSelectionBehavior(self.audit_table.SelectionBehavior.SelectRows)
        self.audit_table.setSelectionMode(self.audit_table.SelectionMode.SingleSelection)
        self.audit_sort_column = None
        self.audit_sort_ascending = True
        self.audit_table.horizontalHeader().sectionClicked.connect(self.sort_audit_by_column)
        self.load_audit_data()
        layout.addWidget(self.audit_table, 1)
        
        # Back button
        back_btn = QPushButton("BACK")
        back_btn.setMaximumWidth(200)
        back_btn.clicked.connect(self.close)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setMinimumHeight(48)
        back_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0EBE3;
                color: #6B5E4E;
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #BAA787;
                color: #FFFFFF;
                border: 1px solid #BAA787;
            }
            QPushButton:pressed {
                background-color: #8B7355;
            }
        """)
        layout.addWidget(back_btn)
    
    def load_audit_data(self):
        """Load and display audit trail from users_audit table with SCD Type 2 information."""
        try:
            # Get all audit records
            df = get_all_audit_records(limit=5000)
            
            if df.empty:
                QMessageBox.information(self, "No Data", "No audit records found")
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
                        if pd.notna(value):
                            value = str(value)[:19]  # Trim to YYYY-MM-DD HH:MM:SS
                        else:
                            value = ""
                    elif col_name == 'effective_end_date':
                        if pd.notna(value):
                            value = str(value)[:19]  # Trim to YYYY-MM-DD HH:MM:SS
                        else:
                           value = "NULL"  # Currently active version
                    elif col_name == 'is_current':
                        value = "Yes" if value else "No"
                    elif col_name == 'audit_action':
                        # Color code the action
                        if value == 'INSERT':
                            value = f"INSERT"
                        elif value == 'UPDATE':
                            value = f"UPDATE"
                        elif value == 'DELETE':
                            value = f"DELETE"
                    else:
                        # Convert all other values to string safely
                        if pd.isna(value):
                            value = ""
                        else:
                            value = str(value)
                    
                    item = QTableWidgetItem(str(value))
                    item.setFont(QFont("Segoe UI", 10))
                    
                    # Right-align numeric columns
                    if col_name in ['audit_id', 'userid']:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    else:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    
                    # Color code based on is_current status
                    if col_name == 'is_current' and value == "CURRENT":
                        item.setBackground(QColor("#E8F5E9"))  # Light green for current
                        item.setForeground(QColor("#2E7D32"))
                    elif col_name == 'is_current' and value == "HISTORICAL":
                        item.setBackground(QColor("#FFF8E1"))  # Light amber for historical
                        item.setForeground(QColor("#8B7355"))
                    
                    self.audit_table.setItem(row_idx, col_idx, item)
            
            # Auto-resize columns
            header = self.audit_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            
            # Set row height to match all-users table
            self.audit_table.verticalHeader().setDefaultSectionSize(60)
            
            # Calculate statistics
            current_count = len(df[df['is_current'] == 1])
            historical_count = len(df) - current_count
            insert_count = len(df[df['audit_action'] == 'INSERT'])
            update_count = len(df[df['audit_action'] == 'UPDATE'])
            delete_count = len(df[df['audit_action'] == 'DELETE'])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading audit data:\n\n{str(e)}")

    def sort_audit_by_column(self, col_index):
        """Sort audit table by clicked column header, toggling asc/desc."""
        if self.audit_table.rowCount() == 0:
            return

        col_name = self.audit_table.horizontalHeaderItem(col_index).text()

        if self.audit_sort_column == col_name:
            self.audit_sort_ascending = not self.audit_sort_ascending
        else:
            self.audit_sort_column = col_name
            self.audit_sort_ascending = True

        # Collect all rows as list of lists
        row_count = self.audit_table.rowCount()
        col_count = self.audit_table.columnCount()
        data = []
        for r in range(row_count):
            row_data = [self.audit_table.item(r, c).text() if self.audit_table.item(r, c) else "" for c in range(col_count)]
            data.append(row_data)

        # Try numeric sort, fall back to string sort
        try:
            data.sort(key=lambda row: float(row[col_index]) if row[col_index] not in ("", "NULL", "Yes", "No")  else float('-inf'),
                      reverse=not self.audit_sort_ascending)
        except (ValueError, TypeError):
            data.sort(key=lambda row: row[col_index].lower(), reverse=not self.audit_sort_ascending)

        # Repopulate table with sorted data (preserve background colours)
        for r, row_data in enumerate(data):
            for c, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFont(QFont("Segoe UI", 10))
                col_name_c = self.audit_table.horizontalHeaderItem(c).text()
                if col_name_c == 'is_current':
                    if value == "Yes":
                        item.setBackground(QColor("#E8F5E9"))
                        item.setForeground(QColor("#2E7D32"))
                    elif value == "No":
                        item.setBackground(QColor("#FFF8E1"))
                        item.setForeground(QColor("#8B7355"))
                self.audit_table.setItem(r, c, item)

        # Update header indicator
        arrow = " ▲" if self.audit_sort_ascending else " ▼"
        headers = [self.audit_table.horizontalHeaderItem(c).text().replace(" ▲", "").replace(" ▼", "") for c in range(col_count)]
        for c, h in enumerate(headers):
            self.audit_table.horizontalHeaderItem(c).setText(h + (arrow if c == col_index else ""))


class EditUserDialog(QDialog):
    """Dialog for editing user information."""
    
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.user_data = user_data
        self.setWindowTitle("Edit User Information")
        self.setModal(True)
        self.setMinimumSize(450, 300)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the edit dialog UI."""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("Edit User Information")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #8B7355; background-color: transparent; letter-spacing: 1px;")
        layout.addWidget(title)
        
        # User ID (Read-only)
        id_label = QLabel("User ID:")
        id_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        id_label.setStyleSheet("color: #6B5E4E; background-color: transparent;")
        layout.addWidget(id_label)
        
        id_display = QLineEdit()
        id_display.setText(str(self.user_data['id']))
        id_display.setReadOnly(True)
        id_display.setMinimumHeight(40)
        id_display.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                background-color: #F8F4EE;
                color: #9A8A7A;
            }
        """)
        layout.addWidget(id_display)
        
        # Name
        name_label = QLabel("Name:")
        name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        name_label.setStyleSheet("color: #6B5E4E; background-color: transparent;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.user_data.get('name', ''))
        self.name_input.setMinimumHeight(40)
        self.name_input.setFont(QFont("Segoe UI", 10))
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QLineEdit:focus {
                border: 2px solid #BAA787;
                background-color: #FDFAF7;
            }
        """)
        layout.addWidget(self.name_input)
        
        # Email
        email_label = QLabel("Email:")
        email_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        email_label.setStyleSheet("color: #6B5E4E; background-color: transparent;")
        layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setText(self.user_data.get('email', ''))
        self.email_input.setMinimumHeight(40)
        self.email_input.setFont(QFont("Segoe UI", 10))
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QLineEdit:focus {
                border: 2px solid #BAA787;
                background-color: #FDFAF7;
            }
        """)
        layout.addWidget(self.email_input)
        
        # Role
        role_label = QLabel("Role:")
        role_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        role_label.setStyleSheet("color: #6B5E4E; background-color: transparent;")
        layout.addWidget(role_label)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setCurrentText(self.user_data.get('role', 'user'))
        self.role_combo.setMinimumHeight(40)
        self.role_combo.setFont(QFont("Segoe UI", 10))
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QComboBox:focus {
                border: 2px solid #BAA787;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #BAA787;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #4D4D4D;
                selection-background-color: #BAA787;
                selection-color: #FFFFFF;
            }
        """)
        layout.addWidget(self.role_combo)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0EBE3;
                color: #6B5E4E;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #BAA787;
                color: #FFFFFF;
                border: 1px solid #BAA787;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setMinimumHeight(40)
        save_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BAA787, stop:1 #D4C4A0);
                color: #1A1A1A;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #D4C4A0, stop:1 #E8DCC8);
            }
            QPushButton:pressed {
                background: #8B7355;
                color: #FFFFFF;
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
        self.setWindowTitle("Active Users")
        self.setMinimumSize(900, 600)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Top section with Logo
        top_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = resource_path(os.path.join("assets", "Logo 1.png"))
        if os.path.exists(logo_path):
            logo = QPixmap(logo_path)
            scaled_logo = logo.scaledToHeight(90, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Title
        title = QLabel("All Users")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #8B7355; background: transparent; letter-spacing: 2px;")
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        search_label.setStyleSheet("color: #6B5E4E; background: transparent;")
        search_label.setMinimumWidth(80)
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by ID, name or email...")
        self.search_input.setMinimumHeight(46)
        self.search_input.setFont(QFont("Segoe UI", 11))
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QLineEdit:hover {
                border: 1px solid #BAA787;
            }
            QLineEdit:focus {
                border: 2px solid #BAA787;
                background-color: #FDFAF7;
            }
        """)
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input, 1)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                gridline-color: #EDE8E0;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QTableWidget::item {
                padding: 12px;
                color: #4D4D4D;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: rgba(186,167,135,0.20);
                color: #4D4D4D;
                border: 1px solid #BAA787;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F4EE, stop:1 #EDE8E0);
                color: #8B7355;
                padding: 14px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #BAA787;
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
        edit_btn = QPushButton("EDIT USER")
        edit_btn.setMaximumWidth(200)
        edit_btn.clicked.connect(self.edit_selected_user)
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setMinimumHeight(52)
        edit_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #F8F4EE;
                color: #8B7355;
                border: 1px solid #BAA787;
                border-radius: 12px;
                padding: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #BAA787;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #8B7355;
                color: #FFFFFF;
            }
        """)
        button_layout.addWidget(edit_btn)
        
        # Download CSV button
        download_btn = QPushButton("DOWNLOAD CSV")        
        download_btn.setMaximumWidth(220)        
        download_btn.clicked.connect(self.download_csv)
        download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        download_btn.setMinimumHeight(52)
        download_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        download_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BAA787, stop:1 #D4C4A0);
                color: #1A1A1A;
                border: none;
                border-radius: 12px;
                padding: 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #D4C4A0, stop:1 #E8DCC8);
            }
            QPushButton:pressed {
                background: #8B7355;
                color: #FFFFFF;
            }
        """)
        button_layout.addWidget(download_btn)
        
        # Audit Trail button
        audit_btn = QPushButton("AUDIT TRAIL")
        audit_btn.setMaximumWidth(220)
        audit_btn.clicked.connect(self.show_audit_trail)
        audit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        audit_btn.setMinimumHeight(52)
        audit_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        audit_btn.setStyleSheet("""
            QPushButton {
                background-color: #F0F8F4;
                color: #2E7D32;
                border: 1px solid #81C784;
                border-radius: 12px;
                padding: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2E7D32;
                color: #FFFFFF;
                border: 1px solid #2E7D32;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)
        button_layout.addWidget(audit_btn)
        
        layout.addLayout(button_layout)
        # Change Password button
        change_pwd_btn = QPushButton("CHANGE PASSWORD")
        change_pwd_btn.setMaximumWidth(250)
        change_pwd_btn.clicked.connect(self.open_change_password)
        change_pwd_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_pwd_btn.setMinimumHeight(52)
        change_pwd_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        change_pwd_btn.setStyleSheet("""
            QPushButton {
            background-color: #FFF8E1;
            color: #8B7355;
            border: 1px solid #BAA787;
            border-radius: 12px;
            padding: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
        background-color: #BAA787;
        color: #FFFFFF;
        border: 1px solid #8B7355;
        }
        QPushButton:pressed {
        background-color: #8B7355;
        color: #FFFFFF;
        }
                                     """)
        button_layout.addWidget(change_pwd_btn)

        
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
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("No data found"))
            return
        
        # Store original DataFrame for filtering
        self.original_df = df.copy()
        
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
        columns_to_hide = ['audit_user', 'effective_start_date', 'effective_end_date', 'audit_action', 'is_current']
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
            QMessageBox.warning(self, "No Selection", "Please select a user to edit")
            return
        
        row = selected_rows[0].row()
        self.edit_user_at_row(row)
    
    def edit_user_at_row(self, row):
        """Edit user at specified row."""
        try:
            # Get userid from the audit table row
            # The table shows audit data, so we need to find userid column
            if self.original_df is None or self.original_df.empty:
                QMessageBox.critical(self, "Error", "No user data loaded")
                return
            
            # Get the row from the original_df (which is already sorted and indexed)
            if row >= len(self.original_df):
                QMessageBox.critical(self, "Error", "Invalid row selection")
                return
            
            # Get userid from the current row in original_df
            user_row = self.original_df.iloc[row]
            
            if 'userid' not in self.original_df.columns:
                QMessageBox.critical(self, "Error", "Could not find userid column in data")
                return
            
            user_id = int(user_row['userid'])
            
            # Get user data from users table
            user_data = get_user_by_id(user_id)
            if not user_data:
                QMessageBox.critical(self, "Error", f"Could not retrieve user information for ID {user_id}")
                return
            
            # Show edit dialog
            dialog = EditUserDialog(self, user_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                edit_data = dialog.get_data()
                
                # Validate input
                if not edit_data['name'].strip():
                    QMessageBox.warning(self, "Invalid Input", "Name cannot be empty")
                    return
                
                if not edit_data['email'].strip():
                    QMessageBox.warning(self, "Invalid Input", "Email cannot be empty")
                    return
                
                # Update user in database
                success, message = update_user_info(
                    edit_data['id'],
                    edit_data['name'],
                    edit_data['email'],
                    edit_data['role']
                )
                
                if success:
                    QMessageBox.information(self, "Success", message)
                    # Reload the table
                    self.load_users()
                    # Clear search filter
                    self.search_input.clear()
                else:
                    QMessageBox.critical(self, "Error", message)
        
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Invalid user ID format:\n\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit user:\n\n{str(e)}")
    
    def download_csv(self):
        """Download the users data exactly as shown in the table."""
        if self.table.rowCount() == 0 or self.table.columnCount() == 0:
            QMessageBox.warning(self, "Error", "No users to download")
            return

        # Ask user to select download directory
        default_path = self.load_saved_path()
        download_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            default_path,
            QFileDialog.Option.ShowDirsOnly
        )

        if not download_dir:
            return  # User cancelled

        self.save_path(download_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_users_{timestamp}.csv"
        filepath = os.path.join(download_dir, filename)

        try:
            # Read data directly from the visible table (includes formatted dates)
            headers = [self.table.horizontalHeaderItem(col).text()
                       for col in range(self.table.columnCount())]
            rows = []
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                rows.append(row_data)

            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

            QMessageBox.information(self, "Success",
                f"Users data downloaded successfully!\n\nSaved to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error",
                f"Failed to download CSV:\n\n{str(e)}")
    
    def filter_table(self, text):
        """Filter table by name or ID - shows message if search doesn't match any users."""
        if self.original_df is None:
            return
        
        if self.original_df.empty:
            return
        
        text = text.strip()
        text_lower = text.lower()
        
        # Apply filtering
        if text:
            # Check if search is numeric (ID search)
            is_numeric = text.isdigit()
            
            if is_numeric:
                # Search by exact userid match (audit table uses 'userid')
                if 'userid' in self.original_df.columns:
                    filtered_df = self.original_df[self.original_df['userid'].astype(str) == text]
                else:
                    filtered_df = pd.DataFrame()
            else:
                # Search by designername (audit table uses 'designername')
                if 'designername' in self.original_df.columns:
                    filtered_df = self.original_df[self.original_df['designername'].astype(str).str.lower().str.contains(text_lower, na=False, regex=False)]
                else:
                    filtered_df = pd.DataFrame()
        else:
            # Show all when search is empty
            filtered_df = self.original_df.copy()
        
        # Handle empty results
        if filtered_df.empty:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(['Result'])
            no_result = QTableWidgetItem('No matching users found')
            no_result.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(0, 0, no_result)
            return
        
        # Sort by userid in descending order (newest first)
        if 'userid' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('userid', ascending=False)
        
        filtered_df = filtered_df.reset_index(drop=True)  # Reset index to sequential
        
        # Filter out columns we don't want to display in the UI
        columns_to_hide = ['audit_user', 'effective_start_date', 'effective_end_date', 'audit_action', 'is_current']
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
    
    def sort_by_column(self, column_index):
        """Sort table by clicked column header."""
        if self.original_df is None or self.original_df.empty:
            return
        
        # Get column name from table header and strip arrow if present
        column_name = self.table.horizontalHeaderItem(column_index).text()
        column_name = column_name.replace(" ▲", "").replace(" ▼", "")
        
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
            columns_to_hide = ['audit_user', 'effective_start_date', 'effective_end_date', 'is_current']
            display_sorted_df = sorted_df.drop(columns=[col for col in columns_to_hide if col in sorted_df.columns])
            
            # Clear and repopulate table
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            self.table.setColumnCount(len(display_sorted_df.columns))
            self.table.setRowCount(len(display_sorted_df))
            
            # Set headers with sort arrow - remove arrows from all headers first
            headers = list(display_sorted_df.columns)
            arrow = " ▲" if self.current_sort_ascending else " ▼"
            for idx, h in enumerate(headers):
                # Remove any existing arrows and add new arrow for sorted column
                clean_header = h.replace(" ▲", "").replace(" ▼", "")
                if clean_header == column_name:
                    headers[idx] = clean_header + arrow
                else:
                    headers[idx] = clean_header
            self.table.setHorizontalHeaderLabels(headers)
            
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
        except Exception as e:
            pass
    
    def show_audit_trail(self):
        """Display the audit trail (users_audit table) in a new dialog."""
        # Create audit dialog
        audit_dialog = AuditTrailDialog(parent=self)
        audit_dialog.exec()
    def open_change_password(self):
        """Open the Change Password screen."""
        from change_password_ui import ChangePasswordScreen
        self.change_password_window = ChangePasswordScreen()
        self.change_password_window.show()