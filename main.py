"""
Main Entry Point for Desktop Application
PyQt6-based User Management System
"""
import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from login_ui import LoginScreen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize and run the desktop application."""
    logger.info("="*60)
    logger.info("Starting User Management System")
    logger.info(f"Launch time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    app = QApplication(sys.argv)
    app.setApplicationName("User Management System")
    app.setOrganizationName("Password Manager")
    logger.info("Application initialized")
    
    # Create and show login screen
    logger.info("Loading login screen...")
    login = LoginScreen()
    login.show()
    logger.info("Login screen displayed")
    
    logger.info("Application running. Waiting for user input...")
    exit_code = app.exec()
    logger.info(f"Application closed with exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
