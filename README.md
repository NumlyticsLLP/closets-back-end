# Identity Manager

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-Latest-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

**A desktop application for secure user account management — built with PyQt6 and MySQL.**

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Connecting to a Database](#connecting-to-a-database)
- [Database Schema](#database-schema)
- [File Structure](#file-structure)
- [Building the Executable](#building-the-executable)
- [Troubleshooting](#troubleshooting)

---

## Overview

Identity Manager is a PyQt6 desktop application that gives administrators a clean interface for managing user accounts stored in a MySQL database. It supports two independent environments — **Test** and **Production** — switchable at runtime via a toggle on the dashboard.

The app launches immediately to the dashboard. A **Connect** button is shown until a database connection is established. Once connected, navigation and live statistics become available.

---

## Features

- **Dual environment support** — separate Test and Production MySQL databases, switchable via an iOS-style toggle
- **Dashboard** — shows total users and users added today; stats load only after a live DB connection
- **Add Users** — creates an account and generates a secure bcrypt-hashed password; credentials exported to CSV/Excel
- **Show Users** — searchable, sortable table of all users with CSV export
- **Change Password** — regenerates a secure password for any user
- **Remove User** — safe deletion with confirmation dialog
- **File Storage** — configurable download paths for exported credential files
- **Windows taskbar icon** — set via direct WinAPI (`WM_SETICON`) for reliable display

---

## Installation

### Prerequisites
- Python 3.10+
- MySQL Server 8.0+
- Windows 10/11

### 1. Clone the repository
```bash
git clone https://github.com/NumlyticsLLP/closets-back-end.git
cd "PASSWORD GENERATOR"
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Running the App

```bash
python main.py
```

The dashboard opens immediately. Click **Connect** to enter your MySQL credentials and establish a connection.

---

## Connecting to a Database

Click the **Connect** button on the dashboard and enter:

| Field | Example |
|---|---|
| Host | `localhost` |
| Port | `3306` |
| Database Name | `user_management_test` |
| Username | `root` |
| Password | `your_password` |

The app validates the connection before proceeding. On success, the toggle switch and navigation become active.

To switch between Test and Production environments, use the **TEST / PROD** toggle. A reconnection dialog will appear.

---

## Database Schema

```sql
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    password    VARCHAR(255) NOT NULL,
    role        ENUM('user', 'admin') DEFAULT 'user',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

The dashboard statistics query the `users` table:
- **Total Users** — `SELECT COUNT(*) FROM users`
- **Added Today** — `SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()`

---

## File Structure

```
PASSWORD GENERATOR/
├── main.py                     # Entry point; AppUserModelID, WM_SETICON, app bootstrap
├── dashboard_ui.py             # Dashboard, connection dialog, mode toggle, stats cards
├── database_desktop.py         # All MySQL operations (connect, CRUD, stats)
├── add_user_ui.py              # Add user screen
├── show_users_ui.py            # User table with search and CSV export
├── change_password_ui.py       # Password reset screen
├── remove_user_ui.py           # User deletion screen
├── login_ui.py                 # Admin login screen
├── file_storage_dialog.py      # Download path selector dialog
├── file_storage_utils.py       # Export helpers (CSV, Excel)
├── mode_selection_dialog.py    # Mode selection dialog (legacy)
├── config.py                   # Credential file loader helpers
├── utils.py                    # Password generation utilities
├── mode_configurations.json    # Mode display configuration
├── app_icon.ico                # Application icon (multi-size ICO)
├── assets/
│   ├── Logo 1.png
│   └── Logo without text.png
├── fixed.spec                  # PyInstaller spec (onedir build)
├── requirements.txt
└── .gitignore
```

---

## Building the Executable

The project uses a **onedir** PyInstaller build, which avoids the slow temp-extraction startup of onefile builds.

```bash
pyinstaller --clean fixed.spec
```

Output: `dist\IdentityManager\IdentityManager.exe`

To distribute, share the entire `dist\IdentityManager\` folder. The EXE requires the files alongside it.

> The icon is embedded in the EXE via `--icon=app_icon.ico` in the spec and also applied at runtime via `WM_SETICON` for reliable Windows taskbar display.

---

## Troubleshooting

### App opens but shows no stats
The dashboard intentionally shows `0` until a database connection is made. Click **Connect** and enter valid MySQL credentials.

### Database connection fails
- Confirm MySQL is running: `Get-Service -Name "*mysql*"`
- Check host, port, username, and password
- Ensure the database exists and the user has access

### EXE is slow to start
Make sure you are using the **onedir** build (`dist\IdentityManager\`), not a onefile build. The onedir build starts in 1–3 seconds; onefile extracts files to a temp folder on every launch.

### Taskbar icon not showing
The icon is set via `WM_SETICON` after the window is shown. If it still does not appear, try right-clicking the taskbar button → **Pin to taskbar**.

---

*Last updated: February 18, 2026*
