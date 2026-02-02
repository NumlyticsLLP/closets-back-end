# 🔐 User Management System - Project Structure

A modular, professional user management system with password generation and bcrypt encryption.

## 📁 Project Structure

```
PASSWORD GENERATOR/
│
├── app.py                          # Main application entry point
├── config.py                       # Database configuration and constants
├── database.py                     # Database connection and operations
├── utils.py                        # Utility functions (password generation)
├── style.css                       # External CSS styling
│
├── pages/                          # Page modules
│   ├── __init__.py                # Pages package initializer
│   ├── dashboard.py               # Dashboard page with metrics
│   ├── add_users.py               # Add single/multiple users
│   ├── show_users.py              # Display all users with search
│   ├── change_password.py         # Change user passwords
│   └── remove_user.py             # Delete users
│
├── setup_database.py              # Database initialization script
├── setup_database.sql             # SQL schema file
└── test_all_scenarios.py          # Comprehensive test suite

```

## 🎯 File Descriptions

### Core Files

- **app.py**: Main Streamlit application entry point with navigation and page routing
- **config.py**: Centralized configuration for database credentials and constants
- **database.py**: All database-related operations (connections, queries, user management)
- **utils.py**: Helper functions including password generation algorithm
- **style.css**: External CSS for professional UI styling

### Pages Directory

Each page is a self-contained module with its own logic:

- **dashboard.py**: System overview with user statistics and recent users table
- **add_users.py**: Interface for adding single or bulk users with auto-generated passwords
- **show_users.py**: User listing with search and filter functionality
- **change_password.py**: Password update interface with random/custom options
- **remove_user.py**: User deletion with confirmation safeguards

## 🚀 Running the Application

```powershell
cd "c:\Users\Vraj S\Downloads\PASSWORD GENERATOR"
streamlit run app.py
```

## 🔧 Configuration

Edit `config.py` to change:
- Database credentials
- Special characters for password generation
- Other system constants

## 📊 Database

- **Host**: localhost:3306
- **Database**: user_management
- **Security**: Bcrypt password hashing

## ✨ Features

- ✅ Modular architecture for easy maintenance
- ✅ Separation of concerns (UI, logic, data)
- ✅ External CSS for clean code
- ✅ Reusable functions across modules
- ✅ Professional UI with gold (#fcb900) color scheme
- ✅ Bcrypt encryption for passwords
- ✅ Excel export for credentials
- ✅ Bulk user operations

## 📝 Notes

- All page modules can be modified independently
- Database functions are centralized in `database.py`
- UI styling is managed through `style.css`
- Configuration changes only require editing `config.py`
