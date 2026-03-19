# Identity Manager

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-Latest-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Version](https://img.shields.io/badge/Version-2.0-gold.svg)
![License](https://img.shields.io/badge/License-Private-red.svg)

**A Windows desktop application for secure user account management — built with PyQt6 and MySQL.**

Developed for **Closets By Design** to manage user identities across isolated Test and Production MySQL environments from a single clean interface.

---

## What's New in Version 2.0

### Login Screen — Rebuilt
- **Credentials file path is saved** automatically on first Browse. On next launch the app auto-loads it silently — no popup, no re-browsing required
- **Database information cards** — Host:Port, Database Name, and Username display in separate read-only boxes once a file is loaded
- **Credentials File card** moved below the Database Information section for a cleaner top-to-bottom flow
- Removed the UPLOAD/UPLOADED status label — the info boxes replace it
- Added gold divider line between the password input and the DB information section
- Improved internal card spacing throughout

### Dashboard & Navigation
- **Navigation buttons** redesigned — warm gold gradient (`#F8F4EE → #EDE8E0`), 2px darker border, 3D pressed effect
- **Exit button** styled to match Remove User (red: `#FDECEA` / `#922B21`) for clear visual distinction
- All debug `print()` log statements removed from every module

### User Management Screens
- **CLOSE button removed** from Add User, Change Password, and Remove User screens
- **Show All Users** — CLOSE button removed; sort arrows fixed (toggle bug where the arrow text broke subsequent sort cycles)
- **Audit Trail** — CLOSE replaced with a **BACK** button; row height increased to 60 px to match the Show Users table; numeric columns (`audit_id`, `userid`) right-aligned and display correctly using `pd.notna()` checks

### EXE Build — Performance & Icon
- All asset paths now use `resource_path()` (resolves `sys._MEIPASS` when frozen, `__file__` in dev) — logo and icon load correctly in the EXE
- `_set_taskbar_icon_win32()` is now **called** after `show()` via `LoadImageW` + `SendMessageW(WM_SETICON)` — taskbar icon displays reliably
- Build switched to **`--onedir`** — EXE starts in 1–3 seconds instead of 10–20 seconds

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [System Flow](#system-flow)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Connecting to a Database](#connecting-to-a-database)
- [User Operations](#user-operations)
- [Database Schema](#database-schema)
- [File Structure](#file-structure)
- [Building the Executable](#building-the-executable)
- [Troubleshooting](#troubleshooting)

---

## Overview

Identity Manager is a PyQt6 desktop application that gives administrators a clean, professional interface for managing user accounts stored in a MySQL database. It supports two completely independent database environments — **Test** and **Production** — switchable at runtime without restarting.

The app is designed around a simple principle: **no connection = no data**. The login screen auto-loads your saved credentials file and just requires a password entry. The dashboard launches and shows zero stats until a database connection is established.

---

## How It Works

### Startup

When launched, the app goes directly to the login screen. If a credentials file was previously browsed and saved, it is **auto-loaded silently** — the Host:Port, Database Name, and Username fields are pre-filled. No popup. The administrator simply enters the database password and clicks **Connect**.

If no saved path exists, the Credentials File card shows Browse and Change Path buttons.

### Connection

The app tests the connection before accepting it. On success:

- The login screen closes
- The **Dashboard** opens with navigation buttons visible
- Stats cards populate with live data
- A 1-second auto-refresh timer starts

### Environment Switching (TEST ↔ PROD)

The iOS-style toggle in the top-right corner shows the current active environment. Clicking it opens a reconnection dialog. On success the app hot-swaps the database connection — no restart needed.

### User Operations

| Button | Action |
|---|---|
| ➕ Add Users | Create a new user account; system generates a bcrypt-hashed password and exports credentials to CSV/Excel |
| 👥 Show Users | Browse, search, sort, and export the full user list with Audit Trail access |
| 🔑 Change Password | Regenerate the password for any selected user |
| 🗑️ Remove User | Delete a user account with confirmation |

---

## System Flow

```mermaid
flowchart TD
    A([Launch app]) --> B[Login screen opens]
    B --> C{Saved credentials\npath exists?}
    C -->|Yes| D[Auto-load silently\nFill Host · DB · Username boxes]
    C -->|No| E[Show Browse button]
    D --> F[Admin enters password\nclicks Connect]
    E --> G[Admin browses JSON file\nPath saved for next launch]
    G --> F
    F --> H[Test MySQL connection]
    H -->|Fail| I[Error dialog · Retry]
    H -->|Success| J[Dashboard opens\nNav visible · Stats load]

    J --> K{Admin selects action}
    K -->|Add Users| L[AddUserScreen\nbcrypt hash · INSERT · Export XLSX+CSV]
    K -->|Show Users| M[ShowUsersScreen\nSearch · Sort · CSV export · Audit Trail]
    K -->|Change Password| N[ChangePasswordScreen\nNew password · UPDATE · Export]
    K -->|Remove User| O[RemoveUserScreen\nConfirm · DELETE]
    K -->|Toggle TEST↔PROD| P[Enter new DB credentials\nHot-swap connection]

    J --> Q[Auto-refresh every 1s\nCOUNT users · COUNT today]
```

---

## Features

- **Saved credentials path** — Browse once; path persisted to `saved_credentials_path.json` and auto-loaded silently on next launch
- **Database info display** — Host:Port, Database Name, Username shown in read-only fields after loading a credentials file
- **Dual environment support** — Test and Production MySQL, switchable via iOS-style toggle with no restart
- **Connection-gated UI** — nav buttons and stats hidden until a verified DB connection exists
- **Live stats** — Total Users and Added Today auto-refresh every second
- **Add Users** — bcrypt-hashed password generation, credentials exported to CSV and Excel
- **Show Users** — searchable, sortable table with sort arrows (correctly toggles asc/desc), CSV export, and Audit Trail
- **Audit Trail** — full SCD Type 2 history with colour-coded CURRENT / HISTORICAL rows, 60 px row height, sortable columns, BACK button
- **Change Password** — regenerates and exports a new password for any user
- **Remove User** — safe deletion with confirmation dialog
- **Windows taskbar icon** — set via `LoadImageW` + `SendMessageW(WM_SETICON)` for reliable display across all Windows versions
- **Frozen-EXE asset resolution** — all assets found via `resource_path()` whether running from source or EXE
- **Fast startup** — `--onedir` build; 1–3 second launch instead of 10–20 seconds

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | PyQt6 |
| Language | Python 3.10+ |
| Database | MySQL 8.0+ via `mysql-connector-python` |
| Password Hashing | `bcrypt` |
| Data Export | `pandas`, `openpyxl` |
| Build | PyInstaller (onedir) |
| Platform | Windows 10/11 |

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

The login screen opens. If a credentials file was previously saved it auto-loads. Enter the database password and click **Connect**.

---

## Connecting to a Database

### First-time setup
1. Click **Browse** in the Credentials File card
2. Select your JSON credentials file — the path is saved automatically
3. The Host:Port, Database Name, and Username fields will populate
4. Enter the database password and click **Connect**

### Subsequent launches
The credentials file is auto-loaded. Just enter the password and connect.

### Credentials JSON format
```json
{
  "host": "localhost",
  "port": 3306,
  "database": "user_management",
  "user": "root"
}
```

### Changing the credentials file
Click **CHANGE PATH** (visible after a file is loaded) to browse a new file.

### Switching environments at runtime
Click the **TEST / PROD** toggle on the dashboard and enter credentials for the target database.

---

## User Operations

### Add a User
1. Click **➕ Add Users**
2. Enter full name, email address, and role (`user` or `admin`)
3. Click **Add User** — a secure password is generated, hashed, stored, and exported

### Show Users
1. Click **👥 Show Users**
2. The full `users` table loads in a searchable, sortable grid
3. Click any column header to sort (▲ / ▼ arrow shown)
4. Click **Download CSV** to export; click **View Audit Trail** for full history

### Audit Trail
- Shows all SCD Type 2 historical records with CURRENT (green) / HISTORICAL (amber) colour coding
- Click column headers to sort; numeric columns right-aligned
- Click **BACK** to return to the user list

### Change a Password
1. Click **🔑 Change Password**
2. Select the user from the dropdown
3. Click **Change Password** — a new password is generated, hashed, saved, and exported

### Remove a User
1. Click **🗑️ Remove User**
2. Select the user from the dropdown
3. Confirm in the popup — the record is permanently deleted

---

## Database Schema

```sql
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    password    VARCHAR(255) NOT NULL,        -- bcrypt hash
    role        ENUM('user', 'admin') DEFAULT 'user',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);
```

---

## File Structure

```
PASSWORD GENERATOR/
├── main.py                          # Entry point — QApp bootstrap, resource_path, WM_SETICON
├── dashboard_ui.py                  # Dashboard, stats cards, iOS toggle, connection dialogs
├── database_desktop.py              # All MySQL operations — connect, CRUD, stats, session config
├── login_ui.py                      # Login screen — credentials file, DB info boxes, auto-save path
├── add_user_ui.py                   # Add user screen
├── show_users_ui.py                 # User table — search, sort, CSV export, audit trail
├── change_password_ui.py            # Password reset screen
├── remove_user_ui.py                # User deletion screen with confirmation
├── file_storage_dialog.py           # Download folder selector dialog
├── file_storage_utils.py            # CSV and Excel export helpers
├── mode_selection_dialog.py         # Mode selection dialog
├── config.py                        # DB config loader helpers
├── utils.py                         # Password generation + resource_path() helper
├── mode_configurations.json         # Mode display labels and colors
├── saved_credentials_path.json      # Auto-created — stores last used credentials file path
├── assets/
│   ├── app_icon.ico                 # Multi-size application icon (16–256 px)
│   ├── Logo 1.png                   # Full logo with text
│   └── Logo without text.png        # Icon-only logo
├── requirements.txt
└── fixed.spec                       # PyInstaller onedir build spec
```

---

## Building the Executable

The project uses a **onedir** PyInstaller build. The EXE finds assets in the same folder at runtime — 1–3 second startup.

### Quick build
```powershell
cd "C:\Users\Vraj S\Documents\GitHub\closets-back-end\PASSWORD GENERATOR"
# Kill any running instance first
Stop-Process -Name "IdentityManager" -Force -ErrorAction SilentlyContinue
# Clean previous build
Remove-Item -Recurse -Force build, dist, IdentityManager.spec -ErrorAction SilentlyContinue
# Build
.\.venv\Scripts\python.exe -m PyInstaller --onedir --windowed --icon="assets\app_icon.ico" --add-data "assets;assets" --name="IdentityManager" main.py
```

**Output:** `dist\IdentityManager\IdentityManager.exe`

To distribute, zip and share the entire `dist\IdentityManager\` folder.

> **Icon note:** The icon is embedded in the EXE via `--icon` **and** applied at runtime via `LoadImageW` + `SendMessageW(WM_SETICON)`. Both steps are required — PyQt's `setWindowIcon` alone does not reliably update the Windows shell taskbar.

---

## Troubleshooting

### Credentials boxes are empty on launch
The credentials file path has not been saved yet. Click **Browse**, select your JSON file — it will be saved automatically for all future launches.

### App opens but stats show 0 and nav is hidden
Expected — the dashboard starts disconnected. Enter your password on the login screen and click **Connect**.

### Connection fails
- Verify MySQL is running: `Get-Service -Name "*mysql*"`
- Check host, port, database name, user, and password in your JSON credentials file
- Ensure the user has `SELECT`, `INSERT`, `UPDATE`, `DELETE` privileges on the target database

### EXE opens slowly (10–20 seconds)
You are using a `--onefile` build. Use the `--onedir` output at `dist\IdentityManager\IdentityManager.exe` — it starts in 1–3 seconds.

### Logo / icon not showing in the EXE
- Rebuild with `--add-data "assets;assets"` to bundle the assets folder into the EXE
- Ensure `app_icon.ico` is present in the `assets\` folder before building
- If the taskbar icon is still missing after launch, right-click → **Pin to taskbar** and relaunch

### Taskbar icon blurry
Run `python make_icon.py` (requires Pillow) to regenerate `assets\app_icon.ico` as a sharp multi-size ICO from `assets\Logo without text.png`.

### Wrong database environment active
Check the toggle in the top-right corner. **Green = TEST**, **Orange = PRODUCTION**. Click the toggle to switch.

---

*Version 2.0 — Last updated: February 20, 2026*


**A Windows desktop application for secure user account management — built with PyQt6 and MySQL.**

Developed for **Closets By Design** to manage user identities across isolated Test and Production MySQL environments from a single clean interface.

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [System Flow](#system-flow)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Connecting to a Database](#connecting-to-a-database)
- [User Operations](#user-operations)
- [Database Schema](#database-schema)
- [File Structure](#file-structure)
- [Building the Executable](#building-the-executable)
- [Troubleshooting](#troubleshooting)

---

## Overview

Identity Manager is a PyQt6 desktop application that gives administrators a clean, professional interface for managing user accounts stored in a MySQL database. It supports two completely independent database environments — **Test** and **Production** — switchable at runtime without restarting.

The app is designed around a simple principle: **no connection = no data**. The dashboard launches immediately but shows zero stats and hides all navigation until a database connection is established. This prevents accidental operations on the wrong environment and makes the current state obvious at a glance.

---

## How It Works

### Startup

When launched, the app skips any splash screen and goes directly to the dashboard. In the top-right corner a green **Connect** button is shown. All navigation buttons (Add Users, Show Users, etc.) are hidden. Stats cards display `0`.

### Connection

Clicking **Connect** opens a dialog where the administrator enters MySQL credentials (host, port, database name, username, password). The app tests the connection before accepting it. On success:

- The **Connect** button is replaced by the **TEST / PROD toggle switch**
- Navigation buttons become visible
- Stats cards are populated with live data from the database
- A 1-second auto-refresh timer starts updating stats

### Environment Switching (TEST ↔ PROD)

The iOS-style toggle in the top-right corner shows the current active environment. Clicking it opens a reconnection dialog where the administrator enters credentials for the other environment. On success the app hot-swaps the database connection — no restart needed. The toggle animates to reflect the new state.

### User Operations

From the dashboard, the administrator can:

| Button | Action |
|---|---|
| ➕ Add Users | Create a new user account; system generates a bcrypt-hashed password and exports credentials to CSV/Excel |
| 👥 Show Users | Browse, search, and export the full user list |
| 🔑 Change Password | Regenerate the password for any selected user |
| 🗑️ Remove User | Delete a user account with confirmation |

Each operation opens in its own window and reads/writes directly to the active MySQL database.

### Password Generation

Passwords are generated programmatically using Python's `secrets` module (via `utils.py`). They are immediately hashed with `bcrypt` before being written to the database. The plaintext password is shown once and saved to the credential export files.

### Export

When a user is added or a password changed, the app prompts for a download folder and writes:
- A per-user `.xlsx` file with username, email, role, and generated password
- An append-only `all_users_data.csv` consolidated log

---

## System Flow

```mermaid
flowchart TD
    A([Launch app]) --> B[Dashboard opens\nConnect button shown\nNav hidden · Stats = 0]
    B --> C{Admin clicks\nConnect}
    C -->|Enters credentials| D[Test MySQL connection]
    D -->|Fail| E[Error dialog\nStay on Connect screen]
    D -->|Success| F[Save session_db_config_test.json\nStart 1s refresh timer]
    F --> G[Dashboard rebuilds\nToggle shown · Nav visible\nStats load from DB]

    G --> H{Admin selects action}

    H -->|Toggle TEST↔PROD| I[DatabaseReconfigDialog\nEnter new DB credentials]
    I -->|Fail| J[Error · Stay on current mode]
    I -->|Success| K[Save session_db_config_production.json\nHot-swap connection\nRefresh stats]

    H -->|Add Users| L[AddUserScreen\nEnter name · email · role]
    L --> M[Generate password\nbcrypt hash · INSERT into users]
    M --> N[Export CSV + XLSX\nto chosen folder]

    H -->|Show Users| O[ShowUsersScreen\nSELECT * FROM users\nSearch · Sort · CSV export]

    H -->|Change Password| P[ChangePasswordScreen\nSelect user · Generate new password\nbcrypt hash · UPDATE users]
    P --> Q[Export new credentials]

    H -->|Remove User| R[RemoveUserScreen\nSelect user · Confirm dialog\nDELETE FROM users]

    G --> S[Auto-refresh every 1s\nSELECT COUNT - users\nSELECT COUNT - today]
```

### Module Interaction

```mermaid
graph LR
    main["main.py\n(bootstrap)"] --> dashboard["dashboard_ui.py\n(Dashboard)"]
    dashboard --> db["database_desktop.py\n(DB layer)"]
    dashboard --> add["add_user_ui.py"]
    dashboard --> show["show_users_ui.py"]
    dashboard --> change["change_password_ui.py"]
    dashboard --> remove["remove_user_ui.py"]
    add --> db
    show --> db
    change --> db
    remove --> db
    add --> fs["file_storage_utils.py\n(CSV/Excel export)"]
    change --> fs
    show --> fs
    db --> mysql[(MySQL\nTest / Production)]
```

---

## Features

- **Dual environment support** — Test and Production MySQL databases, switchable via an iOS-style toggle with no restart
- **Connection-gated UI** — nav buttons and stats are hidden until a verified DB connection exists
- **Live stats** — Total Users and Added Today auto-refresh every second from the `users` table
- **Add Users** — bcrypt-hashed password generation, credentials exported to CSV and Excel
- **Show Users** — searchable, sortable full user table with CSV export
- **Change Password** — regenerates and exports a new password for any user
- **Remove User** — safe deletion with a confirmation dialog
- **Configurable export paths** — download folder preference saved per session
- **Windows taskbar icon** — set via direct `WM_SETICON` WinAPI call for reliable display across all Windows versions

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | PyQt6 |
| Language | Python 3.10+ |
| Database | MySQL 8.0+ via `mysql-connector-python` |
| Password Hashing | `bcrypt` |
| Data Export | `pandas`, `openpyxl` |
| Build | PyInstaller (onedir) |
| Platform | Windows 10/11 |

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

The dashboard opens immediately. Click **Connect** to enter your MySQL credentials.

---

## Connecting to a Database

Click the **Connect** button and fill in:

| Field | Example |
|---|---|
| Host | `localhost` |
| Port | `3306` |
| Database Name | `user_management_test` |
| Username | `root` |
| Password | `your_password` |

The connection is tested before the dashboard unlocks. A failed attempt shows an error and lets you retry.

To switch environments at runtime, click the **TEST / PROD** toggle and enter credentials for the target database.

---

## User Operations

### Add a User
1. Click **➕ Add Users**
2. Enter full name, email address, and role (`user` or `admin`)
3. Click **Add User** — the app generates a secure password, stores it hashed in the DB, and prompts for an export folder
4. Credentials are saved to `user_<name>_<timestamp>.xlsx` and appended to `all_users_data.csv`

### Show Users
1. Click **👥 Show Users**
2. The full `users` table loads in a searchable, sortable grid
3. Click **Download CSV** to export the current view

### Change a Password
1. Click **🔑 Change Password**
2. Select the user from the dropdown
3. Click **Change Password** — a new secure password is generated, hashed, and saved
4. New credentials are exported to file

### Remove a User
1. Click **🗑️ Remove User**
2. Select the user from the dropdown
3. Read the warning and click **Remove User**
4. Confirm in the popup — the record is permanently deleted

---

## Database Schema

```sql
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    password    VARCHAR(255) NOT NULL,        -- bcrypt hash
    role        ENUM('user', 'admin') DEFAULT 'user',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);
```

**Dashboard statistics queries:**
```sql
-- Total Users card
SELECT COUNT(*) FROM users;

-- Added Today card
SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE();
```

---

## File Structure

```
PASSWORD GENERATOR/
├── main.py                      # Entry point — QApp bootstrap, WinAPI icon, WM_SETICON
├── dashboard_ui.py              # Dashboard, stats cards, iOS toggle, connection dialogs
├── database_desktop.py          # All MySQL operations — connect, CRUD, stats, session config
├── add_user_ui.py               # Add user screen
├── show_users_ui.py             # User table — search, sort, CSV export
├── change_password_ui.py        # Password reset screen
├── remove_user_ui.py            # User deletion screen with confirmation
├── login_ui.py                  # Admin login screen (mode-aware)
├── file_storage_dialog.py       # Download folder selector dialog
├── file_storage_utils.py        # CSV and Excel export helpers
├── mode_selection_dialog.py     # Legacy mode selection dialog
├── config.py                    # DB config loader helpers
├── utils.py                     # Secure password generation (secrets module)
├── mode_configurations.json     # Mode display labels and colors
├── app_icon.ico                 # Multi-size application icon (16–256px)
├── fixed.spec                   # PyInstaller onedir build spec
├── requirements.txt
├── .gitignore
└── assets/
    ├── Logo 1.png               # Full logo with text
    └── Logo without text.png    # Icon-only logo (source for app_icon.ico)
```

---

## Building the Executable

The project uses a **onedir** PyInstaller build. Unlike onefile, this layout extracts files once at build time — the EXE finds them in the same folder at runtime, giving a 1–3 second startup instead of 10–20 seconds.

```bash
pyinstaller --clean fixed.spec
```

**Output:** `dist\IdentityManager\IdentityManager.exe`

To distribute, zip and share the entire `dist\IdentityManager\` folder. The EXE cannot run without the accompanying files.

> **Icon note:** The icon is embedded via `--icon=app_icon.ico` in the spec file **and** applied at runtime by calling `LoadImageW` + `SendMessageW(WM_SETICON)` directly on the native HWND after `show()`. This two-step approach is required because PyQt's `setWindowIcon` alone does not reliably update the Windows shell taskbar.

---

## Troubleshooting

### App opens but stats show 0 and nav is hidden
Expected — the dashboard starts disconnected. Click **Connect** and enter valid MySQL credentials to unlock the UI.

### Connection dialog fails
- Verify MySQL is running: `Get-Service -Name "*mysql*"`
- Double-check host, port, database name, username, and password
- Ensure the specified database exists and the user has `SELECT`, `INSERT`, `UPDATE`, `DELETE` privileges

### EXE opens slowly
You are likely using a onefile build. Use the **onedir** output at `dist\IdentityManager\IdentityManager.exe` — it starts in 1–3 seconds because no extraction step happens at runtime.

### Taskbar icon is missing or blurry
- Missing: The icon is applied via `WM_SETICON` after `show()`. If it doesn't appear, restart the app or right-click the taskbar button → **Pin to taskbar**
- Blurry: Regenerate `app_icon.ico` by running `python make_icon.py` (requires Pillow). The script builds a sharpened multi-size ICO from `assets/Logo without text.png`

### Wrong database environment active
Check the toggle in the top-right corner of the dashboard. **Green = TEST**, **Orange = PRODUCTION**. Click the toggle to switch and enter credentials for the target database.

---

*Last updated: February 18, 2026*
