"""
Dashboard Screen - Main Navigation Hub
"""
import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QFrame, QGridLayout, QMessageBox, QDialog, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QRect, QSize, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush, QPen, QIcon
from database_desktop import get_user_count, get_today_users_count, get_current_mode, reload_session_config


class ToggleModeSwitch(QWidget):
    """Custom iOS-style toggle switch for mode selection."""
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = get_current_mode()
        self.is_animating = False
        self.setMinimumSize(140, 70)
        self.setMaximumSize(140, 70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Hover effect
        self.is_hovered = False
        
    def mousePressEvent(self, event):
        """Handle toggle switch click."""
        if not self.is_animating:
            self.clicked.emit()
        
    def enterEvent(self, event):
        """Handle mouse enter."""
        self.is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        """Handle mouse leave."""
        self.is_hovered = False
        self.update()
        
    def paintEvent(self, event):
        """Paint the iOS-style toggle switch."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        radius = height // 2
        
        # Main background track
        track_rect = QRect(0, 0, width, height)
        
        if self.current_mode == "test":
            # Green for test mode (active)
            bg_color = QColor("#27ae60")
            inactive_color = QColor("#c0c0c0")
            circle_x = 2
        else:
            # Gray with white circle on right for production
            bg_color = QColor("#c0c0c0")
            inactive_color = QColor("#c0c0c0")
            circle_x = width - height + 2
            
        # Draw background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, radius, radius)
        
        # Draw white circle (thumb)
        circle_size = height - 4
        circle_y = 2
        circle_rect = QRect(circle_x, circle_y, circle_size, circle_size)
        
        # Add shadow effect on hover
        if self.is_hovered:
            shadow_rect = QRect(circle_rect.x() + 1, circle_rect.y() + 1, 
                              circle_rect.width(), circle_rect.height())
            painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
            painter.drawEllipse(shadow_rect)
        
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#e0e0e0"), 1))
        painter.drawEllipse(circle_rect)
        
        # Draw labels on the switch
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        if self.current_mode == "test":
            # TEST is active (on green side)
            painter.setPen(QColor("#ffffff"))
            left_text_rect = QRect(0, 0, width // 2 - 5, height)
            painter.drawText(left_text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, "PRO")
            
            # PRO is inactive (on gray side)
            painter.setPen(QColor("#808080"))
            right_text_rect = QRect(width // 2 + 5, 0, width // 2 - 5, height)
            painter.drawText(right_text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, "TEST")
        else:
            # TEST is inactive (on gray side)
            painter.setPen(QColor("#808080"))
            left_text_rect = QRect(0, 0, width // 2 - 5, height)
            painter.drawText(left_text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, "PRO")
            
            # PRO is active (on gray side)
            painter.setPen(QColor("#ffffff"))
            right_text_rect = QRect(width // 2 + 5, 0, width // 2 - 5, height)
            painter.drawText(right_text_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, "TEST")


class StatCard(QFrame):
    """Custom stat card widget with proper sizing."""
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setup_ui(title, value)
        
    def setup_ui(self, title, value):
        self.setStyleSheet("""
            StatCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BCAA8D, stop:1 #D0BFA1);
                border: none;
                border-radius: 18px;
            }
        """)
        self.setMinimumSize(180, 120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(8)
        
        # Value label
        self.value_label = QLabel(str(value))
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_font = QFont("Segoe UI", 42, QFont.Weight.Bold)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet("color: #000000; background: transparent;")
        layout.addWidget(self.value_label, 2)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 14, QFont.Weight.DemiBold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #000000; background: transparent;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label, 1)


class NavButton(QPushButton):
    """Custom navigation button with proper sizing."""
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setText(f"{title}\n{subtitle}")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(75)
        self.setStyleSheet("""
            NavButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #BCAA8D, stop:1 #D0BFA1);
                color: #000000;
                padding: 18px;
                border: none;
                border-radius: 14px;
                text-align: center;
                font-weight: bold;
            }
            NavButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #D0BFA1, stop:1 #E4D5C1);
            }
            NavButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #A89673, stop:1 #BCAA8D);
            }
        """)


class Dashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        
        # Initialize button references
        self.connect_btn = None
        self.mode_toggle_btn = None
        self.nav_label = None
        self.add_btn = None
        self.show_btn = None
        self.change_btn = None
        self.remove_btn = None
        self.nav_container_layout = None
        
        self.check_initial_connection()
        self.init_ui()
        
    def check_initial_connection(self):
        """Always start disconnected - user must click Connection to connect."""
        self.is_connected = False
        
    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("🔐 Identity Manager")
        self.setMinimumSize(700, 550)

        # Set window icon from ICO/PNG so taskbar always shows it
        _base = os.path.dirname(__file__)
        for _ico in ("app_icon.ico", os.path.join("assets", "Logo without text.png"), os.path.join("assets", "Logo 1.png")):
            _path = os.path.join(_base, _ico)
            if os.path.exists(_path):
                _icon = QIcon(_path)
                if not _icon.isNull():
                    self.setWindowIcon(_icon)
                    break
        
        # Set background color directly
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(30, 25, 30, 25)
        
        # Always show dashboard layout with data from connection (or zero initially)
        self.setup_dashboard_screen(main_layout)
        
    def setup_dashboard_screen(self, main_layout):
        """Setup the main dashboard screen with navigation."""
        # Add stretch at top to center content vertically when maximized
        main_layout.addStretch(1)
        
        # Top section with Logo and Header
        top_layout = QHBoxLayout()
        
        # Logo in upper left
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "Logo 1.png")
        if os.path.exists(logo_path):
            logo = QPixmap(logo_path)
            scaled_logo = logo.scaledToHeight(110, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        top_layout.addWidget(logo_label)
        top_layout.addStretch()
        
        # Top right button - Connection or Toggle based on connection status
        if not self.is_connected:
            # Show Connection button (store as instance variable)
            self.connect_btn = QPushButton("🔗\nConnection")
            self.connect_btn.setMaximumWidth(120)
            self.connect_btn.setMinimumHeight(80)
            self.connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.connect_btn.clicked.connect(self.show_initial_connection_dialog)
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 10px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """)
            top_layout.addWidget(self.connect_btn)
            self.mode_toggle_btn = None  # Initialize as None when not connected
        else:
            # Show Mode toggle switch
            self.mode_toggle_btn = ToggleModeSwitch()
            self.mode_toggle_btn.clicked.connect(self.on_mode_toggle)
            top_layout.addWidget(self.mode_toggle_btn)
            self.connect_btn = None  # Initialize as None when connected
        
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(10)
        
        # Header
        header = QLabel("🔐 Identity Manager")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        header.setFont(header_font)
        header.setStyleSheet("color: #000000; background: transparent;")
        main_layout.addWidget(header)
        
        # User info (store as instance variable so it can be updated)
        self.user_info_label = QLabel()
        self.user_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_font = QFont("Segoe UI", 12, QFont.Weight.DemiBold)
        self.user_info_label.setFont(user_font)
        self.user_info_label.setStyleSheet("color: #2c3e50; background: transparent;")
        self.update_user_info_display()
        main_layout.addWidget(self.user_info_label)
        
        main_layout.addSpacing(15)
        
        # Setup auto-refresh timer (every 1 second)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_stats)
        self.refresh_timer.start(1000)  # 1000 milliseconds = 1 second
        
        # Stats section with padding
        stats_container = QHBoxLayout()
        stats_container.addSpacing(200)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        
        # Always start with 0 - refresh_stats will populate real data once connected
        self.stat1 = StatCard("👥 Total Users", 0)
        stats_layout.addWidget(self.stat1)
        
        self.stat2 = StatCard("✨ Added Today", 0)
        stats_layout.addWidget(self.stat2)
        
        stats_container.addLayout(stats_layout)
        stats_container.addSpacing(200)
        
        main_layout.addLayout(stats_container)
        
        main_layout.addSpacing(35)
        
        # Navigation label (store as instance variable for show/hide)
        self.nav_label = QLabel("📋 Navigation")
        nav_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        self.nav_label.setFont(nav_font)
        self.nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.nav_label.setStyleSheet("color: #000000; background: transparent;")
        main_layout.addWidget(self.nav_label)
        
        main_layout.addSpacing(8)
        
        # Navigation buttons vertical layout with horizontal padding
        self.nav_container_layout = QHBoxLayout()
        self.nav_container_layout.addSpacing(250)
        
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(18)
        
        self.add_btn = NavButton("➕ Add Users", "Create new user accounts")
        self.add_btn.setMaximumWidth(300)
        self.add_btn.clicked.connect(self.open_add_users)
        nav_layout.addWidget(self.add_btn)
        
        self.show_btn = NavButton("👥 Show Users", "View all user accounts")
        self.show_btn.setMaximumWidth(300)
        self.show_btn.clicked.connect(self.open_show_users)
        nav_layout.addWidget(self.show_btn)
        
        self.change_btn = NavButton("🔑 Change Password", "Update user passwords")
        self.change_btn.setMaximumWidth(300)
        self.change_btn.clicked.connect(self.open_change_password)
        nav_layout.addWidget(self.change_btn)
        
        self.remove_btn = NavButton("🗑️ Remove User", "Delete user accounts")
        self.remove_btn.setMaximumWidth(300)
        self.remove_btn.clicked.connect(self.open_remove_user)
        nav_layout.addWidget(self.remove_btn)
        
        self.nav_container_layout.addLayout(nav_layout)
        self.nav_container_layout.addSpacing(250)
        
        main_layout.addLayout(self.nav_container_layout)
        
        main_layout.addStretch(2)  # Increased stretch to push logout button down
        
        # Hide navigation buttons if not connected
        if not self.is_connected:
            self.nav_label.hide()
            self.add_btn.hide()
            self.show_btn.hide()
            self.change_btn.hide()
            self.remove_btn.hide()
        # Exit button with padding
        logout_container = QHBoxLayout()
        logout_container.addSpacing(250)
        
        logout_btn = QPushButton("🚪 EXIT APPLICATION")
        logout_btn.setMaximumWidth(200)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setMinimumHeight(60)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                padding: 16px;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff6b5a;
            }
            QPushButton:pressed {
                background-color: #c0392b;
            }
        """)
        logout_container.addWidget(logout_btn)
        logout_container.addSpacing(250)
        
        main_layout.addLayout(logout_container)
        
        # Security label
        security = QLabel("🔒 Secured with enterprise-grade encryption")
        security.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_font = QFont("Segoe UI", 9)
        security.setFont(security_font)
        security.setStyleSheet("color: #7f8c8d; background: transparent;")
        main_layout.addWidget(security)
        
        # Add stretch at bottom to center content vertically when maximized
        main_layout.addStretch(1)
    
    def open_add_users(self):
        from add_user_ui import AddUserScreen
        self.add_window = AddUserScreen()
        self.add_window.show()
    
    def update_user_info_display(self):
        """Update user info label to show current mode or connection status."""
        if not self.is_connected:
            user_text = "⚠️ Not Connected - Click CONNECT button to establish connection"
        else:
            current_mode = get_current_mode()
            mode_emoji = "🧪" if current_mode == "test" else "🏭"
            mode_text = current_mode.upper()
            user_text = f"👤 {self.user_data['name']} | {mode_emoji} {mode_text} Mode"
        
        self.user_info_label.setText(user_text)
    
    def show_initial_connection_dialog(self):
        """Show dialog to establish initial database connection."""
        dialog = InitialConnectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Connection successful, refresh the dashboard
            self.is_connected = True
            self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Rebuild the entire dashboard after connection is established."""
        # Stop the old refresh timer if running
        if hasattr(self, 'refresh_timer') and self.refresh_timer:
            self.refresh_timer.stop()

        # Delete the old layout by re-parenting all children then deleting the layout
        old_layout = self.layout()
        if old_layout:
            # Recursively delete all items in the layout
            def clear_layout(layout):
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                    elif item.layout():
                        clear_layout(item.layout())
            clear_layout(old_layout)
            # Remove the layout from the widget
            try:
                from PyQt6 import sip
                sip.delete(old_layout)
            except Exception:
                pass

        # Build a brand-new layout
        new_layout = QVBoxLayout(self)
        new_layout.setSpacing(12)
        new_layout.setContentsMargins(30, 25, 30, 25)
        self.setup_dashboard_screen(new_layout)

        # Navigation buttons are already visible because is_connected=True
        self.update()
        self.refresh_stats()
    
    def show_navigation_buttons(self):
        """Show navigation buttons after connection is established."""
        if self.nav_label:
            self.nav_label.show()
        if self.add_btn:
            self.add_btn.show()
        if self.show_btn:
            self.show_btn.show()
        if self.change_btn:
            self.change_btn.show()
        if self.remove_btn:
            self.remove_btn.show()
    
    def open_show_users(self):
        from show_users_ui import ShowUsersScreen
        self.show_window = ShowUsersScreen()
        self.show_window.show()
    
    def open_change_password(self):
        from change_password_ui import ChangePasswordScreen
        self.change_window = ChangePasswordScreen()
        self.change_window.show()
    
    def open_remove_user(self):
        from remove_user_ui import RemoveUserScreen
        self.remove_window = RemoveUserScreen()
        self.remove_window.show()
    
    def refresh_stats(self):
        """Refresh the statistics cards with fresh data."""
        # Guard: only update if stat cards exist and are connected
        if not hasattr(self, 'stat1') or not self.stat1 or not self.is_connected:
            return

        try:
            total_users = get_user_count()
        except Exception:
            total_users = "N/A"
        
        try:
            today_users = get_today_users_count()
        except Exception:
            today_users = "N/A"
        
        # Update stat cards with new values
        try:
            self.stat1.value_label.setText(str(total_users))
            self.stat2.value_label.setText(str(today_users))
        except RuntimeError:
            # Widget was deleted during rebuild, skip this cycle
            pass
    
    def logout(self):
        """Exit the application instead of returning to login."""
        import sys
        self.close()
        sys.exit(0)
    
    def on_mode_toggle(self):
        """Handle mode toggle button click."""
        current_mode = get_current_mode()
        new_mode = "production" if current_mode == "test" else "test"
        
        # Show the database reconfiguration dialog
        dialog = DatabaseReconfigDialog(self, new_mode)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the new configuration
            config = dialog.get_configuration()
            
            # Test the connection
            if self.test_database_connection(config):
                # Save the new configuration
                self.save_mode_config(new_mode, config)
                
                # Reload the session configuration with the new mode
                reload_session_config(new_mode)
                
                # Update the toggle switch with new mode
                self.mode_toggle_btn.current_mode = new_mode
                self.mode_toggle_btn.update()
                self.mode_toggle_btn.repaint()
                
                # Refresh stats with new database
                self.refresh_stats()
                
                # Update the user info display to show new mode
                self.update_user_info_display()
                
                QMessageBox.information(self, "✅ Success", 
                    f"Successfully switched to {new_mode.upper()} mode!")
            else:
                DatabaseReconfigDialog.show_error_msg(self, "❌ Connection Failed",
                    f"Could not connect to the {new_mode} database.\n\nPlease check your credentials and try again.")
    
    def test_database_connection(self, config):
        """Test database connection with the provided credentials."""
        try:
            import mysql.connector
            
            # Create connection config
            test_config = config.copy()
            test_config.pop('mode', None)
            test_config['use_pure'] = True
            test_config['autocommit'] = True
            test_config['connection_timeout'] = 10
            
            # Try to connect
            conn = mysql.connector.connect(**test_config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def save_mode_config(self, mode, config):
        """Save the mode configuration to a session file."""
        try:
            config_filename = f"session_db_config_{mode}.json"
            with open(config_filename, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            pass


class InitialConnectionDialog(QDialog):
    """Dialog for establishing initial database connection to TEST mode."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "test"  # Always start with TEST mode
        self.setWindowTitle("🔗 Connect to Database")
        self.setModal(True)
        self.setMinimumSize(500, 350)
        self.init_ui()
    
    @staticmethod
    def show_warn_msg(parent, title, text):
        """Show a warning message box with black text."""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #000000;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #f39c12;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 20px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #d68910;
            }
        """)
        msg.exec()

    @staticmethod
    def show_error_msg(parent, title, text):
        """Show an error message box with black text."""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
            }
            QMessageBox QLabel {
                color: #000000;
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background-color: #e74c3c;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 20px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        msg.exec()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("🔗 Connect to Test Database")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Enter your test database credentials:")
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #666666;")
        layout.addWidget(desc)
        
        layout.addSpacing(10)
        
        # Host/Port
        conn_label = QLabel("🖥️ Host & Port:")
        conn_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        conn_label.setStyleSheet("color: #000000;")
        layout.addWidget(conn_label)
        
        self.connection_input = QLineEdit()
        self.connection_input.setPlaceholderText("e.g., localhost:3306")
        self.connection_input.setText("localhost:3306")
        self.connection_input.setMinimumHeight(40)
        self.connection_input.setFont(QFont("Segoe UI", 10))
        self.connection_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #27ae60;
            }
        """)
        layout.addWidget(self.connection_input)
        
        # Database name
        db_label = QLabel("📊 Database Name:")
        db_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        db_label.setStyleSheet("color: #000000;")
        layout.addWidget(db_label)
        
        self.database_input = QLineEdit()
        self.database_input.setPlaceholderText("e.g., user_management_test")
        self.database_input.setText("user_management_test")
        self.database_input.setMinimumHeight(40)
        self.database_input.setFont(QFont("Segoe UI", 10))
        self.database_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #27ae60;
            }
        """)
        layout.addWidget(self.database_input)
        
        # Username
        user_label = QLabel("👤 Username:")
        user_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        user_label.setStyleSheet("color: #000000;")
        layout.addWidget(user_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Database username")
        self.username_input.setText("root")
        self.username_input.setMinimumHeight(40)
        self.username_input.setFont(QFont("Segoe UI", 10))
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #27ae60;
            }
        """)
        layout.addWidget(self.username_input)
        
        # Password
        pass_label = QLabel("🔐 Password:")
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
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #27ae60;
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
        self.show_password_btn.setToolTip("Show password")
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
        """)
        password_container.addWidget(self.show_password_btn)
        
        layout.addLayout(password_container)
        
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
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        connect_btn = QPushButton("✅ Connect")
        connect_btn.setMinimumHeight(40)
        connect_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        connect_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(connect_btn)
        
        layout.addLayout(button_layout)
    
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
    
    def validate_and_accept(self):
        """Validate input and accept dialog."""
        connection_string = self.connection_input.text().strip()
        database = self.database_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not connection_string:
            self.show_warn_msg(self, "Validation Error", "Please enter a host and port")
            return
        
        if not database:
            self.show_warn_msg(self, "Validation Error", "Please enter a database name")
            return
        
        if not username:
            self.show_warn_msg(self, "Validation Error", "Please enter a username")
            return
        
        # Try to connect
        if not self.test_connection(connection_string, database, username, password):
            self.show_error_msg(self, "❌ Connection Failed",
                "Could not connect to the database.\n\n"
                "Please verify:\n"
                "• Host and port are correct\n"
                "• Username and password are correct\n"
                "• MySQL server is running\n"
                "• Database exists")
            return
        
        # Save configuration
        self.save_config(connection_string, database, username, password)
        self.accept()
    
    def test_connection(self, host_port, database, username, password):
        """Test database connection."""
        try:
            import mysql.connector
            
            # Parse host and port
            if ':' in host_port:
                host, port = host_port.split(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 3306
            
            config = {
                'host': host,
                'port': port,
                'user': username,
                'password': password,
                'database': database,
                'use_pure': True,
                'autocommit': True,
                'connection_timeout': 10
            }
            
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            
            return True
        except Exception as e:
            return False
    
    def save_config(self, host_port, database, username, password):
        """Save configuration to test mode config file."""
        try:
            # Parse host and port
            if ':' in host_port:
                host, port = host_port.split(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 3306
            
            config = {
                'host': host,
                'port': port,
                'user': username,
                'password': password,
                'database': database,
                'mode': 'test',
                'use_pure': True
            }
            
            # Save configuration
            config_filename = "session_db_config_test.json"
            with open(config_filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Reload session config
            reload_session_config('test')
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")


class DatabaseReconfigDialog(QDialog):
    """Dialog for reconfiguring database when switching modes."""
    
    def __init__(self, parent=None, mode="test"):
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle(f"� Connect to {mode.title()} Database")
        self.setModal(True)
        self.setMinimumSize(500, 420)
        self.init_ui()
    
    @staticmethod
    def show_warn_msg(parent, title, text):
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; }
            QMessageBox QLabel { color: #000000; font-size: 12px; }
            QMessageBox QPushButton {
                background-color: #f39c12; color: #ffffff;
                border: none; border-radius: 6px; padding: 6px 20px; font-weight: bold;
            }
            QMessageBox QPushButton:hover { background-color: #d68910; }
        """)
        msg.exec()

    @staticmethod
    def show_error_msg(parent, title, text):
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox { background-color: #ffffff; }
            QMessageBox QLabel { color: #000000; font-size: 12px; }
            QMessageBox QPushButton {
                background-color: #e74c3c; color: #ffffff;
                border: none; border-radius: 6px; padding: 6px 20px; font-weight: bold;
            }
            QMessageBox QPushButton:hover { background-color: #c0392b; }
        """)
        msg.exec()

    def _make_input(self, placeholder, focus_color="#0066cc"):
        """Helper to create a styled QLineEdit."""
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(40)
        field.setFont(QFont("Segoe UI", 10))
        field.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #ffffff;
                color: #000000;
            }}
            QLineEdit:focus {{
                border: 2px solid {focus_color};
            }}
        """)
        return field

    def init_ui(self):
        """Initialize the dialog UI."""
        mode_color = "#27ae60" if self.mode == "test" else "#e67e22"
        self.setStyleSheet("QDialog { background-color: #ffffff; }")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        icon = "🔗"
        title = QLabel(f"{icon} Connect to {self.mode.title()} Database")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        layout.addWidget(title)
        
        subtitle = QLabel(f"Enter your {self.mode} database credentials:")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet(f"color: {mode_color};")
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        # Host & Port
        host_label = QLabel("🖥️ Host & Port:")
        host_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        host_label.setStyleSheet("color: #000000;")
        layout.addWidget(host_label)
        self.host_input = self._make_input("e.g., localhost:3306", mode_color)
        self.host_input.setText("localhost:3306")
        layout.addWidget(self.host_input)

        # Database Name
        db_label = QLabel("🗄️ Database Name:")
        db_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        db_label.setStyleSheet("color: #000000;")
        layout.addWidget(db_label)
        self.database_input = self._make_input(f"e.g., user_management_{self.mode}", mode_color)
        self.database_input.setText(f"user_management_{self.mode}")
        layout.addWidget(self.database_input)

        # Username
        user_label = QLabel("👤 Username:")
        user_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        user_label.setStyleSheet("color: #000000;")
        layout.addWidget(user_label)
        self.username_input = self._make_input("Database username", mode_color)
        self.username_input.setText("root")
        layout.addWidget(self.username_input)

        # Password
        pass_label = QLabel("🔐 Password:")
        pass_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        pass_label.setStyleSheet("color: #000000;")
        layout.addWidget(pass_label)
        
        password_container = QHBoxLayout()
        password_container.setSpacing(0)
        password_container.setContentsMargins(0, 0, 0, 0)
        
        self.password_input = self._make_input("Database password", mode_color)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_container.addWidget(self.password_input, 1)
        
        self.show_password_btn = QPushButton("👁️")
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.setMaximumWidth(40)
        self.show_password_btn.setMinimumHeight(40)
        self.show_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        self.show_password_btn.setStyleSheet("""
            QPushButton { background-color: transparent; color: #000000; border: none; padding: 8px; font-size: 16px; }
            QPushButton:hover { background-color: #f0f0f0; border-radius: 4px; }
        """)
        password_container.addWidget(self.show_password_btn)
        layout.addLayout(password_container)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cancel_btn.setStyleSheet("""
            QPushButton { background-color: #cccccc; color: #000000; border: none; border-radius: 8px; padding: 8px 20px; }
            QPushButton:hover { background-color: #b3b3b3; }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        switch_btn = QPushButton(f"✅ Connect to {self.mode.title()}")
        switch_btn.setMinimumHeight(40)
        switch_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        switch_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {mode_color}; color: #ffffff; border: none; border-radius: 8px; padding: 8px 20px; }}
            QPushButton:hover {{ opacity: 0.8; }}
        """)
        switch_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(switch_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_password_visibility(self):
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🚫")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁️")
    
    def validate_and_accept(self):
        """Validate input and accept dialog."""
        if not self.host_input.text().strip():
            self.show_warn_msg(self, "Validation Error", "Please enter a host and port")
            return
        if not self.database_input.text().strip():
            self.show_warn_msg(self, "Validation Error", "Please enter a database name")
            return
        if not self.username_input.text().strip():
            self.show_warn_msg(self, "Validation Error", "Please enter a username")
            return
        self.accept()
    
    def get_configuration(self):
        """Get the configuration data as a dict for connection testing."""
        host_port = self.host_input.text().strip()
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host = host_port
            port = 3306
        
        return {
            'host': host,
            'port': port,
            'user': self.username_input.text().strip(),
            'password': self.password_input.text().strip(),
            'database': self.database_input.text().strip(),
            'mode': self.mode,
            'use_pure': True
        }


