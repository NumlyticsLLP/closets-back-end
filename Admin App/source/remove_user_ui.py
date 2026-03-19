"""
Remove User Screen - Delete user accounts
"""
import os
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QComboBox, QPushButton, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from database_desktop import get_all_users, remove_user, get_all_records_from_table, get_current_table_info
from utils import resource_path


class RemoveUserScreen(QWidget):
    def __init__(self):
        super().__init__()
        # Load table configuration
        self.table_config = get_current_table_info()
        self.all_users = [] # Store all users for filtering
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Remove User")
        self.setMinimumSize(500, 380)
        
        # Set background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#FFFFFF"))
        self.setPalette(palette)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)
        
        layout.addStretch(1)
        
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
        
        # Content container with width constraint
        content_container = QHBoxLayout()
        content_container.addStretch(1)
        
        # Content layout (form fields)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Remove User")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #8B7355; background: transparent; letter-spacing: 2px;")
        content_layout.addWidget(title)
        
        content_layout.addSpacing(15)
        
        # Warning
        warning = QLabel("Warning: This action cannot be undone!")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        warning.setStyleSheet("color: #922B21; background-color: #FDECEA; padding: 16px; border-radius: 10px; border: 1px solid #E07070;")
        content_layout.addWidget(warning)
        
        content_layout.addSpacing(20)
        
        # Search field
        search_label = QLabel(" Search User")
        search_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        search_label.setStyleSheet("color: #6B5E4E; background: transparent; letter-spacing: 1px;")
        content_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type name or email to search...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setFont(QFont("Segoe UI", 10))
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 1px solid #D4C4A0;
                border-radius: 8px;
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
        self.search_input.textChanged.connect(self.filter_users)
        content_layout.addWidget(self.search_input)
        
        content_layout.addSpacing(15)
        
        # User selection
        user_label = QLabel("Select User to Remove")
        user_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        user_label.setStyleSheet("color: #6B5E4E; background: transparent; letter-spacing: 1px;")
        content_layout.addWidget(user_label)
        
        self.user_combo = QComboBox()
        self.user_combo.setMinimumHeight(48)
        self.user_combo.setFont(QFont("Segoe UI", 11))
        self.user_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 18px;
                border: 1px solid #D4C4A0;
                border-radius: 12px;
                background-color: #FFFFFF;
                color: #4D4D4D;
            }
            QComboBox:hover {
                border: 1px solid #BAA787;
            }
            QComboBox:focus {
                border: 2px solid #BAA787;
                background-color: #FDFAF7;
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
                border: 1px solid #BAA787;
            }
        """)
        content_layout.addWidget(self.user_combo)
        
        content_layout.addStretch(2)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.remove_button = QPushButton("REMOVE USER")
        self.remove_button.setMaximumWidth(250)
        self.remove_button.clicked.connect(self.handle_remove_user)
        self.remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_button.setMinimumHeight(54)
        self.remove_button.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #FDECEA;
                color: #922B21;
                border: 1px solid #E07070;
                border-radius: 12px;
                padding: 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #C0392B;
                color: #FFFFFF;
                border: 1px solid #C0392B;
            }
            QPushButton:pressed {
                background-color: #922B21;
            }
        """)
        button_layout.addWidget(self.remove_button)
        
        content_layout.addLayout(button_layout)
        
        # Close content container
        content_container.addLayout(content_layout)
        content_container.addStretch(1)
        
        layout.addLayout(content_container)
        
        layout.addStretch(1)
        
        # Load users after buttons are created
        self.load_users()
        
    def load_users(self):
        """Load users from the default users table."""
        # Load from default users table
        df = get_all_users()
        self.all_users = df # Store for filtering
        self.populate_from_df(df)
    
    def populate_from_df(self, df):
        """Populate combo box from DataFrame, sorted by ID."""
        self.user_combo.clear()
        self.remove_button.setEnabled(True)
        
        if not df.empty:
            # Sort by ID if available (check uppercase first)
            if 'ID' in df.columns:
                df_sorted = df.sort_values('ID')
            elif 'id' in df.columns:
                df_sorted = df.sort_values('id')
            else:
                df_sorted = df
            
            for _, row in df_sorted.iterrows():
                # Construct display text - database uses 'ID', 'Name', 'Email' (capitalized)
                if 'ID' in df.columns and 'Name' in df.columns and 'Email' in df.columns:
                    display_text = f"[ID: {row['ID']}] {row['Name']} ({row['Email']})"
                    self.user_combo.addItem(display_text, row['Email'])
                elif 'id' in df.columns and 'name' in df.columns and 'email' in df.columns:
                    display_text = f"[ID: {row['id']}] {row['name']} ({row['email']})"
                    self.user_combo.addItem(display_text, row['email'])
                elif 'Name' in df.columns and 'Email' in df.columns:
                    display_text = f"{row['Name']} ({row['Email']})"
                    self.user_combo.addItem(display_text, row['Email'])
                else:
                    # Fallback for custom tables
                    cols = df.columns.tolist()
                    if len(cols) >= 3:
                        display_text = f"[ID: {row[cols[0]]}] {row[cols[1]]} ({row[cols[2]]})"
                        self.user_combo.addItem(display_text, str(row[cols[0]]))
                    elif len(cols) >= 2:
                        display_text = f"{row[cols[1]]} ({row[cols[0]]})"
                        self.user_combo.addItem(display_text, str(row[cols[0]]))
                    else:
                        display_text = str(row[cols[0]])
                        self.user_combo.addItem(display_text, str(row[cols[0]]))
        else:
            self.user_combo.addItem("No users found", None)
            self.remove_button.setEnabled(False)
    
    def filter_users(self, search_text):
        """Filter users by name or ID - simple and accurate."""
        search_text = search_text.strip()
        search_lower = search_text.lower()
        
        if not search_text:
            # If search is empty, show all users
            self.populate_from_df(self.all_users)
            return
        
        # Filter DataFrame based on search text
        if self.all_users.empty:
            self.user_combo.clear()
            self.user_combo.addItem("No users found", None)
            return
        
        # Check if search is numeric (ID search)
        is_numeric = search_text.isdigit()
        
        if is_numeric:
            # Search by exact ID match (database uses 'ID' uppercase)
            if 'ID' in self.all_users.columns:
                mask = self.all_users['ID'].astype(str) == search_text
            elif 'id' in self.all_users.columns:
                mask = self.all_users['id'].astype(str) == search_text
            else:
                mask = pd.Series([False] * len(self.all_users))
        else:
            # Search by name (partial match) - database uses 'Name' capitalized
            if 'Name' in self.all_users.columns:
                mask = self.all_users['Name'].astype(str).str.lower().str.contains(search_lower, na=False, regex=False)
            elif 'name' in self.all_users.columns:
                mask = self.all_users['name'].astype(str).str.lower().str.contains(search_lower, na=False, regex=False)
            else:
                mask = pd.Series([False] * len(self.all_users))
        
        filtered_df = self.all_users[mask]
        
        if not filtered_df.empty:
            self.populate_from_df(filtered_df)
        else:
            self.user_combo.clear()
            if is_numeric:
                self.user_combo.addItem(f"No user with ID '{search_text}'", None)
            else:
                self.user_combo.addItem(f"No user named '{search_text}'", None)
    
    def handle_remove_user(self):
        email = self.user_combo.currentData()
        
        if not email:
            QMessageBox.warning(self, "Error", "Please select a user")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to remove this user?\n\n{self.user_combo.currentText()}\n\nThis action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete from default users table (audit logging handled in remove_user function)
            success, message = remove_user(email)
            
            if success:
                QMessageBox.information(self, "Success", "User removed successfully!")
                # Refresh combo box
                self.user_combo.clear()
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", f"{message}")
