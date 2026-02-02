# Admin Authentication Setup Guide

## 🔐 Features Added

1. **Admin Login System** - Secure authentication with email and password
2. **Role-Based Access Control** - Only admin users can access the management system
3. **Session Management** - Secure session handling with logout functionality
4. **User Roles** - Admin vs Regular User distinction

## 📋 Setup Instructions

### Step 1: Run Database Setup Script

```bash
python setup_admin.py
```

This script will:
- Add a `role` column to the users table
- Create a default admin user with credentials:
  - **Email**: `admin@example.com`
  - **Password**: `Admin@123`

⚠️ **IMPORTANT**: Change the admin password after first login!

### Step 2: Launch the Application

```bash
.venv\Scripts\python.exe -m streamlit run app.py
```

### Step 3: Login

1. Open the application in your browser
2. Enter admin credentials
3. You'll be redirected to the dashboard

## 🔑 Admin Features

Once logged in as admin, you have access to:

- **🏠 Dashboard** - System overview and statistics
- **➕ Add Users** - Add single or bulk users
- **👥 Show Users** - View and search all users
- **🔑 Change Password** - Update user passwords
- **🗑️ Remove User** - Delete users from system

## 👥 User Roles

### Admin Role
- Full access to all management features
- Can add/edit/delete users
- Can view dashboard and statistics

### Regular User Role
- Cannot access the management system
- Only stored in database for password management

## 🔒 Security Features

1. **Bcrypt Password Hashing** - Industry-standard encryption
2. **Session-Based Authentication** - Secure session management
3. **Role Verification** - Access control on every page load
4. **Logout Functionality** - Secure session termination

## 📝 Database Schema Updates

The `users` table now includes:
- `role` VARCHAR(20) - User role (admin/user)

Example:
```sql
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' AFTER name;
```

## 🛠️ Manual Admin User Creation

If you need to create additional admin users manually:

```sql
INSERT INTO users (email, name, role, password, created_at, updated_at)
VALUES (
    'newemail@example.com',
    'New Admin Name',
    'admin',
    '$2b$12$hashed_password_here',  -- Use bcrypt to hash password
    NOW(),
    NOW()
);
```

## 🚀 Testing the System

1. **Test Admin Login**:
   - Email: `admin@example.com`
   - Password: `Admin@123`

2. **Test Logout**:
   - Click the "🚪 LOGOUT" button in the sidebar

3. **Test Access Control**:
   - Try logging in with a non-admin user (should be denied)

## 📞 Support

If you encounter any issues:
1. Check database connection in `config.py`
2. Ensure the `role` column exists in the users table
3. Verify bcrypt is installed: `pip install bcrypt`
4. Check that the admin user exists in the database

## 🔄 Upgrading from Previous Version

If you're upgrading from a version without authentication:
1. Run `setup_admin.py` to add the role column
2. All existing users will have 'user' role by default
3. Only the created admin user will have 'admin' role
4. To make existing users admins, update their role in database:
   ```sql
   UPDATE users SET role = 'admin' WHERE email = 'user@example.com';
   ```
