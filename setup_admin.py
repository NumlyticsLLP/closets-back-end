"""
Database Setup Script
Run this script to add the role column to the users table and create an admin user
"""
import mysql.connector
import bcrypt
from config import DB_CONFIG


def setup_database():
    """Add role column and create admin user."""
    
    try:
        # Connect to database
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected to database successfully!")
        
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
            # Add role column
            print("\nAdding 'role' column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(20) DEFAULT 'user' AFTER name
            """)
            print("✅ 'role' column added successfully!")
        else:
            print("\n'role' column already exists.")
        
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_exists = cursor.fetchone()[0] > 0
        
        if not admin_exists:
            print("\n📝 Creating admin user...")
            
            # Admin credentials
            admin_email = "admin@example.com"
            admin_name = "Administrator"
            admin_password = "Admin@123"  # Change this password!
            admin_role = "admin"
            
            # Hash password
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert admin user
            cursor.execute("""
                INSERT INTO users (email, name, role, password, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, (admin_email, admin_name, admin_role, hashed_password))
            
            print(f"✅ Admin user created successfully!")
            print(f"\n{'='*50}")
            print(f"📧 Email: {admin_email}")
            print(f"🔒 Password: {admin_password}")
            print(f"{'='*50}")
            print("\n⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("\nAdmin user already exists.")
        
        # Commit changes
        conn.commit()
        
        # Show all users with roles
        print("\n" + "="*50)
        print("Current Users:")
        print("="*50)
        cursor.execute("SELECT id, email, name, role FROM users ORDER BY id")
        users = cursor.fetchall()
        
        for user in users:
            print(f"ID: {user[0]} | Email: {user[1]} | Name: {user[2]} | Role: {user[3] or 'user'}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database setup completed successfully!")
        
    except mysql.connector.Error as e:
        print(f"\n❌ Database error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("="*50)
    print("Database Setup - User Management System")
    print("="*50)
    
    response = input("\nThis script will:\n1. Add 'role' column to users table\n2. Create an admin user if not exists\n\nProceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        setup_database()
    else:
        print("\nSetup cancelled.")
