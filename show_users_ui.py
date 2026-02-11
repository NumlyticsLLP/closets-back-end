"""
Show Users Screen - View all user accounts
"""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                              QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QHBoxLayout, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from database_desktop import get_all_users
import pandas as pd
import os
import json
from datetime import datetime


class ShowUsersScreen(QWidget):
    CONFIG_FILE = "download_path_config.json"
    
    def __init__(self):
        super().__init__()
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
        self.setMinimumSize(800, 500)
        
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
            scaled_logo = logo.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation)
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
        self.search_input.setPlaceholderText("Search by name or email...")
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
            }
            QTableWidget::item:selected {
                background-color: #fdfaf7;
                color: #000000;
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
        self.load_users()
        layout.addWidget(self.table, 1)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
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
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def load_users(self):
        df = get_all_users()
        
        if df.empty:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("No users found"))
            return
        
        # Set up table
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)
        
        # Populate table
        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        # Adjust column widths
        header = self.table.horizontalHeader()
        for i in range(len(df.columns)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        # Store original data for filtering
        self.original_df = df
        
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
        """Download all users data as CSV file."""
        df = get_all_users()
        
        if df.empty:
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
            df.to_csv(filepath, index=False)
            QMessageBox.information(self, "Success", 
                f"✅ Users data downloaded successfully!\n\n"
                f"📂 Saved to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"❌ Failed to download CSV:\n\n{str(e)}")
    
    def filter_table(self, text):
        if not hasattr(self, 'original_df'):
            return
        
        text = text.lower()
        
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
