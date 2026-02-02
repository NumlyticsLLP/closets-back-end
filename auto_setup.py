"""
Automatic Database Setup Script
Runs without user input
"""
import mysql.connector
import bcrypt
from config import DB_CONFIG


def auto_setup():
    """Automatically add role column and create admin user."""
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully!")
        
        # Check if role column exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'role'
        """, (DB_CONFIG['database'],))
        
        role_exists = cursor.fetchone()[0] > 0
        
        if not role_exists:
            print("\n📝 Adding 'role' column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(20) DEFAULT 'user' AFTER name
            """)
            print("✅ 'role' column added successfully!")
        else:
            print("\n✓ 'role' column already exists.")
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_exists = cursor.fetchone()[0] > 0
        
        if not admin_exists:
            print("\n📝 Creating admin user...")
            
            # Admin credentials
            admin_email = "admin@example.com"
            admin_name = "Administrator"
            admin_password = "Admin@123"
            admin_role = "admin"
            
            # Hash password
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert admin user
            cursor.execute("""
                INSERT INTO users (email, name, role, password, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (admin_email, admin_name, admin_role, hashed_password))
            
            print(f"✅ Admin user created successfully!")
            print(f"\n{'='*60}")
            print(f"  📧 Admin Email: {admin_email}")
            print(f"  🔒 Admin Password: {admin_password}")
            print(f"{'='*60}")
            print("\n  ⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("\n✓ Admin user already exists.")
        
        # Commit changes
        conn.commit()
        
        # Show all users with roles
        print("\n" + "="*60)
        print("  Current Users in Database:")
        print("="*60)
        cursor.execute("SELECT id, email, name, role FROM users ORDER BY id")
        users = cursor.fetchall()
        
        for user in users:
            role_display = user[3] if user[3] else 'user'
            print(f"  ID: {user[0]:<3} | {user[1]:<30} | {user[2]:<20} | {role_display}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("  ✅ Database setup completed successfully!")
        print("="*60)
        print("\n  🚀 You can now run the application with:")
        print('     .venv\\Scripts\\python.exe -m streamlit run app.py')
        print("\n")
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  User Management System - Database Setup")
    print("="*60)
    print("\n  This script will:")
    print("  1. Add 'role' column to users table (if not exists)")
    print("  2. Create an admin user (if not exists)\n")
    
    auto_setup()
