"""
Password Generator Application - Main Entry Point with Mode Selection
"""

import sys
import os
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen, QLabel, QDialog
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Import application components
from mode_selection_dialog import ModeSelectionDialog
from config import load_db_credentials_from_file, show_credentials_dialog, create_sample_credentials_file

class PasswordGeneratorApp:
    """Main application class with mode selection."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Password Generator")
        self.app.setApplicationDisplayName("Password Generator")
        self.app.setApplicationVersion("1.0")
        
        # Set application icon globally
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "Logo without text.png")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.app.setWindowIcon(app_icon)
        
        # Set taskbar properties
        self.setup_taskbar_visibility()
        
        self.current_mode = None
        self.db_config = {}
    
    def setup_taskbar_visibility(self):
        """Ensure the application shows properly in taskbar."""
        try:
            # Set application properties for proper taskbar display
            self.app.setQuitOnLastWindowClosed(True)
            
            # Windows-specific taskbar setup
            if sys.platform == "win32":
                try:
                    import ctypes
                    # Set the app user model ID for proper taskbar grouping
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PasswordGenerator.1.0")
                except Exception as e:
                    logging.warning(f"Could not set Windows taskbar ID: {e}")
        except Exception as e:
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
        """Show database credentials to the user for confirmation."""
        mode_icon = "🧪" if self.current_mode == "test" else "🏭"
        
        credentials_info = f"""
{mode_icon} Running in {self.current_mode.upper()} Mode

📊 Database Configuration:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 Connection: {self.db_config['connection_string']}
👤 Username: {self.db_config['username']}
🔐 Password: {self.db_config['password']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Application will now connect to the {self.current_mode} database.

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
            
            logging.info(f"📋 Parsed DB Config: {host}:{port}/{database} (mode: {self.current_mode})")
            return db_config
            
        except Exception as e:
            logging.error(f"❌ Error parsing connection string: {e}")
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
                logging.error("❌ Failed to parse connection string")
                return
            
            # Set up database configuration for the application
            self.setup_database_config(parsed_config)
            
            # Create generic user data for dashboard since no admin login needed
            user_data = {
                'name': f'{self.current_mode.title()} Mode User',
                'role': f'{self.current_mode.title()} Administrator',
                'email': f'{self.current_mode}@system.local'
            }
            
            # Test database connection before creating dashboard
            try:
                from dashboard_ui import Dashboard
                from database_desktop import get_db_connection, initialize_database
                
                conn = get_db_connection()
                if conn:
                    conn.close()
                else:
                    # Show warning but continue
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        None,
                        "Database Connection Warning",
                        "⚠️ Could not connect to MySQL database.\n\n"
                        "Possible causes:\n"
                        "• MySQL server is not running\n"
                        "• Invalid credentials\n"
                        "• Database doesn't exist\n\n"
                        "The application will continue with limited functionality.\n"
                        "User statistics will show 'N/A'."
                    )
                    
            except Exception as db_test_err:
                logging.error(f"❌ Database test failed: {db_test_err}")
                logging.warning("⚠️ Dashboard will continue with limited functionality")
                
                # Show error dialog but continue
                from PyQt6.QtWidgets import QMessageBox
                error_msg = str(db_test_err)
                if "2003" in error_msg or "Can't connect" in error_msg:
                    user_msg = ("❌ MySQL Server Not Running\n\n"
                               "Please start your MySQL server and restart the application.\n\n"
                               "The app will continue with limited functionality.")
                elif "1045" in error_msg or "Access denied" in error_msg:
                    user_msg = ("❌ Database Access Denied\n\n"
                               "Please check your username and password.\n\n"
                               "The app will continue with limited functionality.")
                else:
                    user_msg = (f"❌ Database Connection Error\n\n{error_msg}\n\n"
                               "The app will continue with limited functionality.")
                
                QMessageBox.warning(None, "Database Error", user_msg)
            
            self.dashboard = Dashboard(user_data)
            
            # Set taskbar icon for dashboard
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "Logo without text.png")
            if os.path.exists(icon_path):
                self.dashboard.setWindowIcon(QIcon(icon_path))
            
            self.dashboard.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
            
            self.dashboard.show()
            
        except Exception as e:
            logging.error(f"❌ Error starting main application: {e}")
            import traceback
            logging.error(f"📋 Full traceback: {traceback.format_exc()}")
            
            # Show error dialog to user
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "Application Error",
                f"Failed to start the application:\n\n{str(e)}\n\nCheck the logs for more details."
            )
            QMessageBox.critical(
                None,
                "Startup Error",
                f"Failed to start the application.\n\nError: {e}"
            )
    
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
    
    def run(self):
        """Run the application."""
        try:
            # Show mode selection first
            if not self.show_mode_selection():
                return 0
            
            # Run the Qt application loop
            return self.app.exec()
            
        except Exception as e:
            logging.error(f"❌ Application error: {e}")
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
        logging.info("Application interrupted by user")
        return 0
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


def main():
    """Initialize and run the desktop application."""
    logger.info("="*60)
    logger.info("Starting User Management System")
    logger.info(f"Launch time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    app = QApplication(sys.argv)
    app.setApplicationName("User Management System")
    app.setOrganizationName("Password Manager")
    
    logger.info("Initializing database configuration...")
    
    # Prompt for database credentials file
    try:
        if not show_credentials_dialog():
            logger.error("Failed to configure database credentials")
            return 1
    except Exception as e:
        logger.error(f"Error during credentials configuration: {e}")
        try:
            QMessageBox.critical(
                QWidget(),
                "Startup Error",
                f"❌ Failed to configure database credentials:\n\n{e}\n\n"
                f"🛠️ Please check your credentials file and try again."
            )
        except:
            print(f"Startup error: {e}")
        return 1
    
    logger.info("Database configuration completed successfully")
    
    # Initialize and show login screen
    try:
        logger.info("Initializing login screen...")
        login_window = LoginScreen()
        login_window.show()
        logger.info("Application initialized successfully")
        
        # Start the application event loop
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        logger.info("User Management System shutdown completed")
        return exit_code
        
    except Exception as e:
        logger.error(f"Error initializing application: {e}")
        try:
            QMessageBox.critical(
                QWidget(),
                "Application Error",
                f"❌ Failed to start application:\n\n{e}\n\n"
                f"🔧 Please check your installation and try again."
            )
        except:
            print(f"Application error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
