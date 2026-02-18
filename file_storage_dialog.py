"""
File Storage Options Dialog - Provides options for storing data in new or existing files
"""

import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFileDialog, QMessageBox, QFrame, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class FileStorageDialog(QDialog):
    # Signal emitted when user makes a choice: (option_type, file_path)
    # option_type: "new" or "existing"
    # file_path: selected path for the file/folder
    storage_choice_made = pyqtSignal(str, str)
    
    def __init__(self, parent=None, title="Choose File Storage Option", operation="save data"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.operation = operation  # "save data", "save user", "save password", etc.
        self.selected_option = None
        self.selected_path = None
        
        self.setup_ui()
        self.load_last_paths()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.resize(500, 350)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #fdfbfb, stop:1 #ebedee);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("📁 File Storage Options")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(f"Choose how you want to {self.operation}:")
        desc_label.setFont(QFont("Segoe UI", 11))
        desc_label.setStyleSheet("color: #34495e; margin-bottom: 20px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Option 1: New File
        self.create_option_frame(
            layout,
            "🆕 Store in New File",
            "Create a new file at a location you choose",
            "#e8f5e8",
            "#27ae60",
            self.select_new_file_location
        )
        
        layout.addSpacing(10)
        
        # Option 2: Existing File
        self.create_option_frame(
            layout,
            "📄 Store in Existing File",
            "Add to an existing file that you select",
            "#fff3e0",
            "#f39c12",
            self.select_existing_file
        )
        
        layout.addStretch()
        
        # Cancel button
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMaximumWidth(120)
        cancel_btn.setStyleSheet("""
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
        cancel_btn.clicked.connect(self.reject)
        
        cancel_layout.addWidget(cancel_btn)
        cancel_layout.addStretch()
        layout.addLayout(cancel_layout)
        
    def create_option_frame(self, parent_layout, title, description, bg_color, accent_color, click_handler):
        """Create an option frame with title, description and click handler."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {accent_color};
                border-radius: 12px;
                padding: 20px;
            }}
            QFrame:hover {{
                border: 3px solid {accent_color};
                background-color: {bg_color};
            }}
        """)
        frame.setMinimumHeight(100)
        frame.mousePressEvent = lambda event: click_handler()
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(8)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {accent_color};")
        frame_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Segoe UI", 10))
        desc_label.setStyleSheet("color: #34495e;")
        desc_label.setWordWrap(True)
        frame_layout.addWidget(desc_label)
        
        # Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        select_btn = QPushButton("Select")
        select_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        select_btn.setMinimumHeight(35)
        select_btn.setMaximumWidth(100)
        select_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {accent_color};
                opacity: 0.8;
            }}
        """)
        select_btn.clicked.connect(click_handler)
        
        btn_layout.addWidget(select_btn)
        frame_layout.addLayout(btn_layout)
        
        parent_layout.addWidget(frame)
        
    def select_new_file_location(self):
        """Handle selection of new file location."""
        # Get last used path for new files
        default_path = self.get_last_path("new_file_path")
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "📁 Select Folder for New File",
            default_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.selected_option = "new"
            self.selected_path = directory
            self.save_last_path("new_file_path", directory)
            
            # Emit signal and accept dialog
            self.storage_choice_made.emit("new", directory)
            self.accept()
            
    def select_existing_file(self):
        """Handle selection of existing file."""
        # Get last used path for existing files
        default_path = self.get_last_path("existing_file_path")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "📄 Select Existing File to Update",
            default_path,
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if file_path:
            self.selected_option = "existing"
            self.selected_path = file_path
            # Save the directory for future use
            self.save_last_path("existing_file_path", os.path.dirname(file_path))
            
            # Emit signal and accept dialog
            self.storage_choice_made.emit("existing", file_path)
            self.accept()
            
    def get_last_path(self, path_type):
        """Get the last used path for the specified type."""
        config_file = "file_storage_paths.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get(path_type, os.path.expanduser('~/Downloads'))
        except:
            pass
        return os.path.expanduser('~/Downloads')
        
    def save_last_path(self, path_type, path):
        """Save the last used path for the specified type."""
        config_file = "file_storage_paths.json"
        try:
            config = {}
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            
            config[path_type] = path
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
            
    def load_last_paths(self):
        """Load last used paths on dialog startup."""
        # This method can be extended if we want to pre-populate any UI elements
        pass
        
    @staticmethod
    def get_storage_choice(parent=None, title="Choose File Storage Option", operation="save data"):
        """
        Static method to show the dialog and get user choice.
        Returns: (option_type, file_path) tuple or (None, None) if cancelled
        """
        dialog = FileStorageDialog(parent, title, operation)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            return dialog.selected_option, dialog.selected_path
        else:
            return None, None