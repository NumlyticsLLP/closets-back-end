"""
Database Configuration
"""
import os
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

# Default database connection settings (fallback)
DEFAULT_DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "0000",
    "database": "user_management",
    "use_pure": True  # Use pure Python implementation to avoid PyQt6 conflicts
}

# Global variable to store current DB config
DB_CONFIG = DEFAULT_DB_CONFIG.copy()

def load_db_credentials_from_file(filepath):
    """
    Load database credentials from a text file.
    Supports both JSON format and key-value format.
    
    JSON Format:
    {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "your_password",
        "database": "user_management"
    }
    
    Key-Value Format:
    host=localhost
    port=3306
    user=root
    password=your_password
    database=user_management
    """
    global DB_CONFIG
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            
        # Try to parse as JSON first
        try:
            config_data = json.loads(content)
            if isinstance(config_data, dict):
                # Update DB_CONFIG with loaded values
                for key in ['host', 'port', 'user', 'password', 'database']:
                    if key in config_data:
                        DB_CONFIG[key] = config_data[key]
                
                # Ensure port is integer
                if 'port' in config_data:
                    DB_CONFIG['port'] = int(config_data['port'])
                
                return True, "Database credentials loaded successfully from JSON format"
                
        except json.JSONDecodeError:
            # Try to parse as key-value format
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key in ['host', 'user', 'password', 'database']:
                        DB_CONFIG[key] = value
                    elif key == 'port':
                        DB_CONFIG[key] = int(value)
            
            return True, "Database credentials loaded successfully from key-value format"
            
    except FileNotFoundError:
        return False, f"Credentials file not found: {filepath}"
    except ValueError as e:
        return False, f"Invalid port number in credentials file: {e}"
    except Exception as e:
        return False, f"Error reading credentials file: {e}"

def prompt_for_credentials_file():
    """
    Prompt user to select database credentials file.
    Returns tuple (success, filepath, message)
    """
    try:
        # Create a temporary widget for file dialog
        widget = QWidget()
        
        # Open file dialog
        filepath, _ = QFileDialog.getOpenFileName(
            widget,
            "🗁️ Select Database Credentials File",
            os.path.expanduser("~"),
            "Text Files (*.txt);;JSON Files (*.json);;All Files (*.*)"
        )
        
        if filepath:
            success, message = load_db_credentials_from_file(filepath)
            return success, filepath, message
        else:
            # User cancelled - use default config
            return True, None, "Using default database configuration"
            
    except Exception as e:
        return False, None, f"Error selecting credentials file: {e}"

def show_credentials_dialog():
    """
    Show dialog asking user to select credentials file.
    Returns True if successful, False otherwise.
    """
    try:
        widget = QWidget()
        
        # Ask user if they want to load credentials from file
        reply = QMessageBox.question(
            widget,
            "🔑 Database Configuration",
            "📄 Would you like to load database credentials from a file?\n\n"
            "✅ Yes - Select credentials file\n"
            "❌ No - Use default configuration\n\n"
            "Expected file formats:\n"
            "• JSON: {\"host\": \"localhost\", \"user\": \"root\", ...}\n"
            "• Key-Value: host=localhost\nuser=root\n...",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, filepath, message = prompt_for_credentials_file()
            
            if success:
                if filepath:
                    QMessageBox.information(
                        widget,
                        "Success",
                        f"✅ {message}\n\n"
                        f"📂 File: {filepath}\n\n"
                        f"Database: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
                    )
                else:
                    QMessageBox.information(
                        widget,
                        "Default Configuration",
                        f"🛠️ Using default database configuration\n\n"
                        f"Database: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
                    )
                return True
            else:
                QMessageBox.warning(
                    widget,
                    "Error",
                    f"❌ Failed to load credentials:\n\n{message}\n\n"
                    f"🛠️ Using default configuration instead."
                )
                return True  # Continue with default config
        else:
            # User chose to use default configuration
            QMessageBox.information(
                widget,
                "Default Configuration",
                f"🛠️ Using default database configuration\n\n"
                f"Database: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            )
            return True
            
    except Exception as e:
        try:
            QMessageBox.critical(
                QWidget(),
                "Configuration Error",
                f"❌ Error during database configuration:\n\n{e}\n\n"
                f"🛠️ Using default configuration."
            )
        except:
            print(f"Error during database configuration: {e}")
        return True  # Continue with default config

def create_sample_credentials_file():
    """
    Create a sample credentials file for user reference.
    Only creates files if they don't already exist to preserve user settings.
    """
    sample_json = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "0000",
        "database": "user_management"
    }
    
    sample_keyvalue = """# Database Credentials File
# Key-Value Format
# Note: All these values can be customized for your setup
host=localhost
port=3306
user=root
password=0000
database=user_management"""
    
    try:
        created_files = []
        
        # Create JSON sample only if it doesn't exist
        if not os.path.exists('sample_credentials.json'):
            with open('sample_credentials.json', 'w', encoding='utf-8') as f:
                json.dump(sample_json, f, indent=4)
            created_files.append('sample_credentials.json')
            
        # Create key-value sample only if it doesn't exist
        if not os.path.exists('sample_credentials.txt'):
            with open('sample_credentials.txt', 'w', encoding='utf-8') as f:
                f.write(sample_keyvalue)
            created_files.append('sample_credentials.txt')
        
        if created_files:
            return True, f"Sample credential files created: {', '.join(created_files)}"
        else:
            return True, "Sample credential files already exist - preserved existing settings"
            
    except Exception as e:
        return False, f"Error creating sample files: {e}"

# Special characters for password generation
SPECIAL_CHARS = r"!@#$%&*-_?/\|+=-.,><()"
