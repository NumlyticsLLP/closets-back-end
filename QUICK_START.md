# 🔐 Quick Start Guide - Admin Login

## ✅ Setup Complete!

The database has been configured with admin authentication.

## 🔑 Admin Credentials

**Email:** `admin@example.com`  
**Password:** `Admin@123`

⚠️ **Change this password after your first login!**

## 🚀 Launch Application

```bash
.venv\Scripts\python.exe -m streamlit run app.py
```

## 📋 How It Works

1. **Login Screen**
   - Open the app - you'll see the login page
   - Enter admin email and password
   - Click "🚀 LOGIN"

2. **Admin Dashboard**
   - After successful login, you'll see:
     - Your name and role in the header
     - Full navigation sidebar with all features
     - Logout button at the bottom of sidebar

3. **Available Features for Admin**
   - 🏠 Dashboard - System overview
   - ➕ Add Users - Add single/bulk users
   - 👥 Show Users - View all users
   - 🔑 Change Password - Update passwords
   - 🗑️ Remove User - Delete users

4. **Logout**
   - Click the "🚪 LOGOUT" button in the sidebar
   - You'll be redirected to the login page

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ Session-based authentication
- ✅ Role-based access control
- ✅ Admin-only access to management system

## 👥 Current Users in Database

| ID | Email | Role |
|----|-------|------|
| 1 | john.doe@cbdbarrie.com | user |
| 2 | jane.smith@cbdbarrie.com | user |
| 5 | alice.test@test.com | user |
| 6 | bob.test@test.com | user |
| 8 | vraj.sondagar@numlytics.com | user |
| 9 | admin@example.com | **admin** |

## 🛠️ Making More Admins

To make existing users admins, run this SQL:

```sql
UPDATE users SET role = 'admin' WHERE email = 'user@example.com';
```

Or you can add a new admin through the Add Users page after logging in as admin.

## ❓ Troubleshooting

**Can't login?**
- Verify email: `admin@example.com`
- Verify password: `Admin@123`
- Check database connection in config.py

**"Access denied" message?**
- The user doesn't have admin role
- Update user role to 'admin' in database

**Application won't start?**
- Make sure you're in the correct directory
- Check that virtual environment is activated
- Verify all dependencies are installed

## 📞 Need Help?

Check the [ADMIN_SETUP.md](ADMIN_SETUP.md) file for detailed documentation.
