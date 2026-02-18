"""
Password Generator Application - Main Entry Point with Mode Selection
"""

import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen, QLabel, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

# Windows: set AppUserModelID BEFORE QApplication is created so taskbar shows the icon
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ClosetsByDesign.IdentityManager.1.0")
    except Exception:
        pass

def _set_taskbar_icon_win32(widget, ico_path: str):
    """Directly send WM_SETICON to the native HWND — the only reliable method on Windows."""
    if sys.platform != "win32" or not os.path.exists(ico_path):
        return
    try:
        import ctypes
        WM_SETICON      = 0x0080
        ICON_SMALL      = 0
        ICON_BIG        = 1
        LR_LOADFROMFILE = 0x0010
        IMAGE_ICON      = 1
        hwnd = int(widget.winId())

        # Load each size explicitly so Windows never upscales/blurs
        sm = ctypes.windll.user32.GetSystemMetrics(49)  # SM_CXSMICON
        bg = ctypes.windll.user32.GetSystemMetrics(11)  # SM_CXICON
        if sm == 0: sm = 16
        if bg == 0: bg = 32

        hicon_small = ctypes.windll.user32.LoadImageW(
            None, ico_path, IMAGE_ICON, sm, sm, LR_LOADFROMFILE
        )
        hicon_big = ctypes.windll.user32.LoadImageW(
            None, ico_path, IMAGE_ICON, bg, bg, LR_LOADFROMFILE
        )
        if hicon_small:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        if hicon_big:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
    except Exception:
        pass

# Import application components
from mode_selection_dialog import ModeSelectionDialog
from dashboard_ui import Dashboard
from config import load_db_credentials_from_file, show_credentials_dialog, create_sample_credentials_file

class PasswordGeneratorApp:
    """Main application class with mode selection."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Identity Manager")
        self.app.setApplicationDisplayName("Identity Manager")
        self.app.setApplicationVersion("1.0")
        
        # Load icon once and reuse everywhere
        self._app_icon = self._load_icon()
        if self._app_icon:
            self.app.setWindowIcon(self._app_icon)
        
        self.current_mode = None
        self.db_config = {}

    def _load_icon(self):
        """Load the best available icon for the application."""
        base = os.path.dirname(__file__)
        candidates = [
            os.path.join(base, "app_icon.ico"),
            os.path.join(base, "assets", "Logo without text.png"),
            os.path.join(base, "assets", "Logo 1.png"),
        ]
        for path in candidates:
            if os.path.exists(path):
                icon = QIcon(path)
                if not icon.isNull():
                    return icon
        return None
    
    def setup_taskbar_visibility(self):
        """Ensure the application shows properly in taskbar."""
        try:
            self.app.setQuitOnLastWindowClosed(True)
        except Exception:
            pass
    
    def show_mode_selection(self):
        """Show mode selection dialog and handle the result."""
        mode_dialog = ModeSelectionDialog()
        mode_dialog.mode_selected.connect(self.handle_mode_selection)
        
        # Center the dialog on screen
        mode_dialog.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowTitleHint
        )
        
        result = mode_dialog.exec()
        
        if result != QDialog.DialogCode.Accepted:
            return False
        
        return True
    
    def handle_mode_selection(self, mode, connection_string, username, password):
        """Handle the selected mode and database configuration."""
        self.current_mode = mode
        self.db_config = {
            'connection_string': connection_string,
            'username': username,
            'password': password,
            'mode': mode
        }
        
        # Show credentials confirmation to user
        self.show_credentials_confirmation()
        
        # Start the main application
        self.start_main_application()
    
    def show_credentials_confirmation(self):
        """Show database connection status to the user (without exposing credentials)."""
        mode_icon = "🧪" if self.current_mode == "test" else "🏭"
        
        credentials_info = f"""
{mode_icon} Running in {self.current_mode.upper()} Mode

✅ Application will now connect to the configured {self.current_mode} database.

💡 You can change the mode by restarting the application.
        """
        
        QMessageBox.information(
            None,
            f"Password Generator - {self.current_mode.title()} Mode",
            credentials_info
        )
    
    def parse_connection_string(self):
        """Parse connection string and create database configuration."""
        connection_string = self.db_config['connection_string']
        username = self.db_config['username']
        password = self.db_config['password']
        
        try:
            # Parse connection string (host:port/database)
            if '/' in connection_string:
                host_port, database = connection_string.split('/', 1)
            else:
                host_port = connection_string
                database = f"user_management_{self.current_mode}"
            
            if ':' in host_port:
                host, port = host_port.split(':', 1)
                port = int(port)
            else:
                host = host_port
                port = 3306
            
            # Create database configuration
            db_config = {
                'host': host,
                'port': port,
                'user': username,
                'password': password,
                'database': database,
                'mode': self.current_mode
            }
            
            return db_config
            
        except Exception as e:
            QMessageBox.critical(
                None, 
                "Configuration Error",
                f"Invalid connection string format.\n\nExpected: host:port/database\nError: {e}"
            )
            return None
    
    def start_main_application(self):
        """Start the main application with the configured database."""
        try:
            # Parse the connection string
            parsed_config = self.parse_connection_string()
            if not parsed_config:
                self.show_credentials_error("Invalid Configuration", "Please enter a valid connection string in the format: host:port/database")
                self.restart_mode_selection()
                return
            
            # Set up database configuration for the application
            self.setup_database_config(parsed_config)
            
            # Test database connection BEFORE proceeding
            if not self.test_database_connection(parsed_config):
                self.show_credentials_error(
                    "Database Connection Failed",
                    "❌ Could not connect to the database with provided credentials.\n\n"
                    "Please verify:\n"
                    "• Database host and port are correct\n"
                    "• Username and password are correct\n"
                    "• MySQL server is running\n"
                    "• Database exists\n\n"
                    "Click OK to re-enter credentials."
                )
                self.restart_mode_selection()
                return
            
            # Create generic user data for dashboard since no admin login needed
            user_data = {
                'name': f'{self.current_mode.title()} Mode User',
                'role': f'{self.current_mode.title()} Administrator',
                'email': f'{self.current_mode}@system.local'
            }
            
            self.dashboard = Dashboard(user_data)
            
            # Set window flags FIRST (before icon, before show)
            self.dashboard.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )

            if self._app_icon:
                self.dashboard.setWindowIcon(self._app_icon)
            
            self.dashboard.show()

            # After show() the native HWND exists — use WinAPI directly for reliable taskbar icon
            _ico = os.path.join(os.path.dirname(__file__), "app_icon.ico")
            _set_taskbar_icon_win32(self.dashboard, _ico)
            
        except Exception as e:
            self.show_credentials_error("Application Error", f"Failed to start the application:\n\n{str(e)}")
            self.restart_mode_selection()
    
    def setup_database_config(self, config):
        """Set up database configuration for the application."""
        # Create a temporary config file for this session
        import json
        config_filename = f"session_db_config_{self.current_mode}.json"
        
        try:
            with open(config_filename, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            pass
    
    def test_database_connection(self, config):
        """Test database connection with the provided credentials."""
        try:
            import mysql.connector
            
            # Create connection config without the mode field
            test_config = config.copy()
            test_config.pop('mode', None)
            test_config['use_pure'] = True
            test_config['autocommit'] = True
            test_config['connection_timeout'] = 10
            
            # Try to connect
            conn = mysql.connector.connect(**test_config)
            cursor = conn.cursor()
            
            # Test the connection with a simple query
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return True
            
        except mysql.connector.errors.ProgrammingError as e:
            return False
        except mysql.connector.errors.DatabaseError as e:
            return False
        except mysql.connector.errors.InterfaceError as e:
            return False
        except Exception as e:
            return False
    
    def show_credentials_error(self, title, message):
        """Show error message for credentials issue."""
        QMessageBox.critical(None, f"❌ {title}", message)
    
    def restart_mode_selection(self):
        """Close current setup and restart mode selection."""
        if hasattr(self, 'dashboard') and self.dashboard is not None:
            self.dashboard.close()
        
        # Reset configuration
        self.current_mode = None
        self.db_config = {}
        
        # Show mode selection dialog again
        QTimer.singleShot(500, self.show_mode_selection)
    
    def run(self):
        """Run the application."""
        try:
            # Create generic user data for dashboard with no initial connection
            user_data = {
                'name': 'Administrator',
                'role': 'Admin',
                'email': 'admin@system.local',
                'connected': False  # Start with no connection
            }
            
            # Go directly to dashboard without mode selection
            self.dashboard = Dashboard(user_data)
            
            # Set window flags FIRST (before icon, before show)
            self.dashboard.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )

            if self._app_icon:
                self.dashboard.setWindowIcon(self._app_icon)

            self.dashboard.show()

            # After show() the native HWND exists — use WinAPI directly for reliable taskbar icon
            _ico = os.path.join(os.path.dirname(__file__), "app_icon.ico")
            _set_taskbar_icon_win32(self.dashboard, _ico)
            
            # Run the Qt application loop
            return self.app.exec()
            
        except Exception as e:
            QMessageBox.critical(None, "Application Error", f"Failed to start the application:\n\n{str(e)}")
            return 1
        finally:
            self.cleanup_session_files()
    
    def cleanup_session_files(self):
        """Clean up temporary session files."""
        session_files = [
            f"session_db_config_{self.current_mode}.json" if self.current_mode else "",
        ]
        
        for file in session_files:
            if not file:
                continue
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                pass


def main():
    """Main entry point."""
    try:
        # Create and run the application
        app = PasswordGeneratorApp()
        return app.run()
        
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        return 1


if __name__ == "__main__":
    sys.exit(main())

