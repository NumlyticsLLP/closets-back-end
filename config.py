"""
Database Configuration
"""

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "0000",
    "database": "user_management",
    "use_pure": True  # Use pure Python implementation to avoid PyQt6 conflicts
}

# Special characters for password generation
SPECIAL_CHARS = r"!@#$%&*-_?/\|+=-.,><()"
