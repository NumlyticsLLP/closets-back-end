# PASSWORD_PROTECTOR_2.0

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-Latest-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-Educational-red.svg)

🔐 **A comprehensive, enterprise-grade desktop application for secure user account management with advanced password generation, database integration, and beautiful modern UI design.**

## 📋 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation Guide](#installation-guide)
- [Configuration](#configuration)
- [Usage Instructions](#usage-instructions)
- [Database Schema](#database-schema)
- [File Structure](#file-structure)
- [Security Features](#security-features)
- [Export & Import](#export--import)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

**PASSWORD_PROTECTOR_2.0** is a sophisticated desktop application built with PyQt6 that provides secure user account management capabilities for organizations and administrators. The application features a modern, intuitive interface with comprehensive functionality for managing user databases, generating secure passwords, and maintaining audit trails.

### 🎯 Primary Objectives
- **Secure Authentication**: Multi-layered admin authentication system
- **User Lifecycle Management**: Complete CRUD operations for user accounts
- **Password Security**: Automated generation of cryptographically secure passwords
- **Data Persistence**: Robust MySQL database integration with transaction safety
- **Export Capabilities**: Flexible data export in multiple formats (CSV, Excel)
- **User Experience**: Modern, responsive UI with consistent design patterns
- **Enterprise Ready**: Scalable architecture suitable for organizational deployment

## ✨ Key Features

### 🔐 Security & Authentication
- **Admin Portal**: Secure admin-only access with bcrypt password hashing
- **Session Management**: Persistent login sessions with automatic logout
- **Password Generation**: Cryptographically secure password creation algorithm
- **Database Encryption**: Encrypted password storage using industry-standard bcrypt
- **Input Validation**: Comprehensive input sanitization and validation

### 👥 User Management
- **Create Users**: Add new user accounts with role-based permissions
- **View Users**: Comprehensive table view with real-time search and filtering
- **Update Passwords**: Secure password reset functionality with audit trails
- **Remove Users**: Safe user deletion with confirmation dialogs
- **User Statistics**: Real-time dashboard with user metrics and analytics

### 📊 Data Management
- **MySQL Integration**: Robust database connectivity with connection pooling
- **Transaction Safety**: ACID-compliant database operations
- **Backup & Export**: Automated data export to CSV and Excel formats
- **Path Preferences**: Customizable download locations with persistent settings
- **Audit Logging**: Comprehensive logging of all system operations

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with golden accent theme
- **Responsive Layout**: Adaptive UI components that scale across different screen sizes
- **Intuitive Navigation**: Logical workflow with clear visual indicators
- **Error Handling**: User-friendly error messages and validation feedback
- **Accessibility**: Keyboard navigation and screen reader compatibility

## 🏗️ System Architecture

### Technology Stack
- **Frontend**: PyQt6 (Cross-platform GUI framework)
- **Backend**: Python 3.8+ with object-oriented design patterns
- **Database**: MySQL 8.0+ with mysql-connector-python driver
- **Security**: bcrypt for password hashing, input sanitization
- **Data Processing**: pandas for data manipulation and export
- **Build System**: PyInstaller for standalone executable creation

### Design Patterns
- **MVC Architecture**: Clear separation of concerns between UI, logic, and data
- **Singleton Pattern**: Database connection management
- **Factory Pattern**: UI component creation and styling
- **Observer Pattern**: Real-time UI updates and data synchronization

## 🚀 Installation Guide

### Prerequisites
Before installation, ensure your system meets these requirements:

#### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 500MB free disk space
- **Network**: Internet connection for dependency installation

#### Database Requirements
- **MySQL Server**: Version 8.0 or higher
- **Database Access**: Administrative privileges for database creation
- **Network Access**: Local or remote MySQL server accessibility

### Option 1: Use Pre-built Executable (Recommended)

For end users who want to run the application without setting up a development environment:

1. **Download the Executable**
   ```bash
   # Navigate to the dist folder in the project
   cd dist/
   ```

2. **Run the Application**
   - Double-click `UserManagementSystem.exe` (Windows)
   - The application will launch with the login screen

### Option 2: Developer Installation

For developers who want to modify or contribute to the project:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/vraj-sondagar-numlytics/PASSWORD_PROTECTOR_2.0.git
   cd PASSWORD_PROTECTOR_2.0
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install PyQt6==6.6.0
   pip install mysql-connector-python==8.2.0
   pip install pandas==2.1.4
   pip install bcrypt==4.1.2
   pip install openpyxl==3.1.2
   pip install pyinstaller==6.3.0
   ```

4. **Database Setup**
   ```bash
   # Connect to MySQL as administrator
   mysql -u root -p

   # Execute the database setup script
   mysql -u root -p < setup_database.sql
   ```

5. **Configure Database Connection**
   ```python
   # Edit config.py with your database credentials
   DB_CONFIG = {
       "host": "localhost",
       "port": 3306,
       "database": "user_management",
       "user": "your_username",
       "password": "your_password",
       "use_pure": True
   }
   ```

6. **Launch Application**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Database Configuration

The `config.py` file contains all database connection parameters:

```python
# Database Configuration
DB_CONFIG = {
    "host": "localhost",           # MySQL server hostname
    "port": 3306,                  # MySQL server port
    "database": "user_management", # Database name
    "user": "root",                # Database username
    "password": "your_password",   # Database password
    "use_pure": True,              # Use pure Python MySQL driver
    "autocommit": False,           # Manual transaction control
    "charset": "utf8mb4",          # Character set for Unicode support
    "collation": "utf8mb4_unicode_ci"
}

# Password Generation Configuration
SPECIAL_CHARS = "!@#$%^&*"        # Special characters for passwords
MIN_PASSWORD_LENGTH = 8           # Minimum password length
MAX_PASSWORD_LENGTH = 16          # Maximum password length
```

### Application Settings

```python
# UI Configuration
DEFAULT_THEME = "golden"           # Application color theme
WINDOW_MIN_WIDTH = 800            # Minimum window width
WINDOW_MIN_HEIGHT = 600           # Minimum window height
AUTO_SAVE_PREFERENCES = True      # Save user preferences automatically

# Security Settings
SESSION_TIMEOUT = 30              # Session timeout in minutes
MAX_LOGIN_ATTEMPTS = 3            # Maximum failed login attempts
ENCRYPTION_ROUNDS = 12            # bcrypt encryption rounds
```

## 📖 Usage Instructions

### Getting Started

1. **Launch the Application**
   - Run the executable or execute `python main.py`
   - The login screen will appear

2. **Administrative Login**
   - **Default Credentials**:
     - Email: `admin@example.com`
     - Password: `Adm4$b`
   - Click "LOGIN" to access the dashboard

### Dashboard Overview

The main dashboard provides:
- **User Statistics**: Real-time count of total users and users added today
- **Navigation Panel**: Access to all application features
- **Quick Actions**: Shortcuts to common tasks

### User Management Operations

#### Adding New Users

1. Click "➕ Add Users" from the dashboard
2. Fill in the required information:
   - **Full Name**: User's complete name
   - **Email Address**: Valid email for user identification
   - **Role**: Select 'user' or 'admin' permissions
3. Click "ADD USER"
4. Choose download location for credential files
5. System automatically generates a secure password
6. Credentials are saved to both CSV and Excel formats

#### Viewing All Users

1. Click "👥 Show Users" from the dashboard
2. Browse the complete user table with:
   - Real-time search functionality
   - Column sorting capabilities
   - User details display
3. Use "📥 DOWNLOAD CSV" to export current user list
4. Use "📂 CHANGE PATH" to modify default download location

#### Updating User Passwords

1. Click "🔑 Change Password" from the dashboard
2. Select user from dropdown menu
3. Click "CHANGE PASSWORD"
4. New password is automatically generated and displayed
5. Choose download location for credential backup
6. Updated credentials are saved to files

#### Removing Users

1. Click "🗑️ Remove User" from the dashboard
2. Select user from dropdown menu
3. Review the warning message carefully
4. Click "REMOVE USER"
5. Confirm deletion in the popup dialog
6. User is permanently removed from the database

### Data Export Features

#### CSV Export
- **All Users**: Export complete user database to timestamped CSV file
- **Individual Users**: Each new user generates individual credential file
- **Consolidated Log**: All users appended to single `all_users_data.csv` file

#### Excel Export
- **Formatted Reports**: Professional Excel files with proper formatting
- **Timestamped Files**: Each export includes creation timestamp
- **Multiple Sheets**: Support for multiple data sheets in single file

#### Path Management
- **Default Locations**: System remembers last used download folder
- **Custom Paths**: Admin can change default download location
- **Path Validation**: Ensures selected folders exist and are writable

## 🗄️ Database Schema

### Users Table Structure

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
);
```

### Default Admin Account
```sql
INSERT INTO users (email, name, password, role) VALUES
('admin@example.com', 'Administrator', '$2b$12$hashed_password', 'admin');
```

### Database Relationships
- **Primary Key**: Auto-incrementing user ID
- **Unique Constraints**: Email addresses must be unique
- **Indexes**: Optimized for email lookup and role-based queries
- **Timestamps**: Automatic creation and modification tracking

## 📁 File Structure

```
PASSWORD_PROTECTOR_2.0/
├── 📄 main.py                    # Application entry point and initialization
├── 🔐 login_ui.py               # Login screen with authentication logic
├── 📊 dashboard_ui.py           # Main dashboard with navigation and statistics
├── ➕ add_user_ui.py            # User creation interface with validation
├── 👀 show_users_ui.py          # User viewing and search interface
├── 🗑️ remove_user_ui.py         # User deletion interface with confirmations
├── 🔑 change_password_ui.py     # Password management interface
├── 🗄️ database_desktop.py       # Database operations and connection management
├── 🛠️ utils.py                  # Utility functions for password generation
├── ⚙️ config.py                 # Configuration settings and database parameters
├── 🗃️ setup_database.sql        # Database schema and initial data setup
├── 🚫 .gitignore                # Git ignore rules for clean repository
├── 📖 README.md                 # Comprehensive project documentation
└── 📦 dist/                     # Built executable files
    └── UserManagementSystem.exe # Standalone executable application
```

### Key Files Description

- **main.py**: Application bootstrap, logging configuration, and main window initialization
- **login_ui.py**: Secure authentication interface with input validation and error handling
- **dashboard_ui.py**: Central navigation hub with real-time statistics and custom UI components
- **database_desktop.py**: Database abstraction layer with connection pooling and error handling
- **utils.py**: Password generation algorithms and utility functions
- **config.py**: Centralized configuration management for database and application settings

## 🔒 Security Features

### Authentication & Authorization
- **Admin-Only Access**: Application restricted to administrative users only
- **Secure Password Storage**: All passwords encrypted using bcrypt with salt rounds
- **Session Management**: Secure login sessions with proper cleanup
- **Input Validation**: Comprehensive sanitization of all user inputs

### Password Security
- **Cryptographic Generation**: Passwords created using secure random algorithms
- **Complexity Requirements**: Enforced minimum complexity with mixed character types
- **Unique Generation**: Each password is unique and non-predictable
- **Secure Transmission**: Passwords handled securely throughout the application

### Database Security
- **Prepared Statements**: All database queries use parameterized statements
- **Transaction Integrity**: ACID-compliant database operations
- **Connection Security**: Encrypted database connections where supported
- **Error Handling**: Secure error messages that don't expose sensitive information

## 📤 Export & Import

### Supported Export Formats

#### CSV Export
- **File Format**: UTF-8 encoded CSV with proper headers
- **Timestamp Format**: YYYY-MM-DD HH:MM:SS for all date fields
- **Delimiter**: Comma-separated values with proper escaping
- **File Naming**: `all_users_YYYYMMDD_HHMMSS.csv` for timestamped exports

#### Excel Export
- **File Format**: Modern .xlsx format with cell formatting
- **Worksheet Structure**: Single sheet with formatted headers
- **Data Types**: Proper data type preservation for dates and numbers
- **File Naming**: `user_credentials_YYYYMMDD_HHMMSS.xlsx` for individual exports

### Data Fields Included
- **User ID**: Unique identifier for each user
- **Full Name**: Complete user name as entered
- **Email Address**: Primary user identification
- **Generated Password**: Secure password for user account
- **Role**: User permission level (user/admin)
- **Creation Date**: Timestamp of account creation
- **Last Modified**: Timestamp of last account modification

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Database Connection Problems
```
Issue: "Failed to connect to MySQL server"
Solutions:
1. Verify MySQL server is running
2. Check database credentials in config.py
3. Ensure MySQL port (3306) is not blocked by firewall
4. Verify database 'user_management' exists
5. Test connection with MySQL command line client
```

#### Login Issues
```
Issue: "Invalid email or password"
Solutions:
1. Verify admin credentials: admin@example.com / Adm4$b
2. Check database connection status
3. Ensure users table contains admin account
4. Verify password hashing is working correctly
5. Check application logs for detailed error messages
```

#### File Export Problems
```
Issue: "Failed to download CSV"
Solutions:
1. Ensure destination folder has write permissions
2. Check available disk space
3. Verify folder path is accessible
4. Close any open files with same name
5. Try different destination folder
```

#### UI Display Issues
```
Issue: "Window doesn't display properly"
Solutions:
1. Check screen resolution and DPI settings
2. Update graphics drivers
3. Try running with different Qt platform plugins
4. Verify PyQt6 installation is complete
5. Check for conflicting Qt installations
```

### Debug Mode

Enable debug mode by setting environment variable:
```bash
# Windows
set PYTHONPATH=%PYTHONPATH%;.
set DEBUG=1
python main.py

# macOS/Linux
export PYTHONPATH=$PYTHONPATH:.
export DEBUG=1
python main.py
```

### Log Files

Application logs are written to:
- **Windows**: `%APPDATA%/UserManagementSystem/logs/app.log`
- **macOS**: `~/Library/Logs/UserManagementSystem/app.log`
- **Linux**: `~/.local/share/UserManagementSystem/logs/app.log`

## 💻 Development

### Setting Up Development Environment

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/PASSWORD_PROTECTOR_2.0.git
   cd PASSWORD_PROTECTOR_2.0
   ```

2. **Install Development Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

### Code Style and Standards

- **PEP 8 Compliance**: Follow Python PEP 8 style guidelines
- **Type Hints**: Use type annotations for all function signatures
- **Docstrings**: Document all classes and methods with comprehensive docstrings
- **Error Handling**: Implement robust error handling with proper logging
- **Testing**: Write unit tests for all new functionality

### Building Executable

```bash
# Build standalone executable
pyinstaller --onefile --windowed --name="UserManagementSystem" main.py

# Build with custom icon (Windows)
pyinstaller --onefile --windowed --name="UserManagementSystem" --icon=icon.ico main.py

# The executable will be created in dist/ folder
```

### Testing

```bash
# Run unit tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run integration tests
python -m pytest tests/integration/
```

## 🤝 Contributing

We welcome contributions from the community! Please follow these guidelines:

### Contribution Process

1. **Fork the Repository**: Create a fork of the main repository
2. **Create Feature Branch**: Create a new branch for your feature or bug fix
3. **Make Changes**: Implement your changes with proper testing
4. **Submit Pull Request**: Create a pull request with detailed description
5. **Code Review**: Participate in the code review process
6. **Merge**: Once approved, changes will be merged to main branch

### Contribution Guidelines

- **Issue First**: For major changes, create an issue to discuss the proposed changes
- **Small Commits**: Make small, logical commits with clear commit messages
- **Test Coverage**: Ensure all new code has appropriate test coverage
- **Documentation**: Update documentation for any new features or changes
- **Backwards Compatibility**: Maintain backwards compatibility when possible

### Bug Reports

When reporting bugs, please include:
- **Environment Details**: OS, Python version, dependency versions
- **Reproduction Steps**: Clear steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Any error messages or stack traces
- **Screenshots**: If applicable, include screenshots

## 📜 License

This project is created for educational purposes. The software is provided "as is" without warranty of any kind, express or implied.

### Educational Use
- **Learning**: Perfect for students learning desktop application development
- **Teaching**: Suitable for educational institutions and coding bootcamps
- **Research**: Available for academic research and analysis
- **Portfolio**: Can be used in professional portfolios with proper attribution

### Disclaimer
- This software is intended for educational use only
- Users are responsible for ensuring compliance with applicable laws
- No warranty is provided for production use
- Authors are not liable for any damages or losses

---

## 📞 Support & Contact

For questions, suggestions, or support:

- **GitHub Issues**: [Create an issue](https://github.com/vraj-sondagar-numlytics/PASSWORD_PROTECTOR_2.0/issues)
- **Documentation**: Check this README for comprehensive information
- **Email**: Contact project maintainers through GitHub profiles

---

**Built with ❤️ using PyQt6 and Python**

*Last Updated: February 3, 2026*
