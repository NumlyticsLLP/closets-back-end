import pandas as pd
import bcrypt
import random
import string
import mysql.connector
from datetime import datetime

# --- Database Configuration ---
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "0000",
    "database": "user_management"
}

special_chars = r"!@#$%&*-_?/\|+=-.,><()"

# --- Helper Functions ---

def get_db_connection():
    """Establish database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def gen_password(name):
    """Generate a random password based on user's name."""
    parts = name.strip().split()
    
    # Choose 3 letters from either first or last name
    if len(parts) >= 2:
        base_source = random.choice([parts[0], parts[1]])
    else:
        base_source = parts[0] if parts else "usr"
    
    name_part = base_source[:3].capitalize()

    # Remaining 3 characters
    digit = random.choice(string.digits)
    special = random.choice(special_chars)
    rand_char = random.choice(string.ascii_lowercase + string.digits)
    
    # Randomly position the name chunk
    others = [digit, special, rand_char]
    insert_position = random.randint(0, 3)
    parts_combined = others[:insert_position] + [name_part] + others[insert_position:]
    
    return ''.join(parts_combined)

# --- Main Functions ---

def add_users():
    """Add new users to the system."""
    print("\n" + "="*50)
    print("ADD NEW USERS")
    print("="*50)
    
    users = []
    while True:
        email = input("Enter email (or 'done' to finish): ").strip()
        if email.lower() == 'done':
            break
        name = input("Enter full name: ").strip()
        if email and name:
            users.append((email, name))
        else:
            print("❌ Email and name cannot be empty!")
    
    if not users:
        print("⚠️ No users to add.")
        return
    
    # Remove duplicates
    users = list(dict.fromkeys(users))
    
    # Build DataFrame
    df = pd.DataFrame(users, columns=["email", "name"])
    df["password"] = df["name"].apply(gen_password)
    df["bcrypt_password"] = df["password"].apply(lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode())
    
    # Save to Excel
    output_file = f"user_credentials-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(output_file, index=False)
    print(f"✅ Excel file saved as '{output_file}'")
    
    # Insert into MySQL
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        success_count = 0
        
        for _, row in df.iterrows():
            try:
                cursor.callproc("sp_insert_user", (
                    row["email"],
                    row["name"],
                    row["bcrypt_password"],
                    "user"
                ))
                success_count += 1
            except Exception as e:
                print(f"❌ Error adding {row['email']}: {e}")
        
        conn.commit()
        print(f"✅ {success_count}/{len(df)} users added to database successfully!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        cursor.close()
        conn.close()

def remove_user():
    """Remove a user from the system."""
    print("\n" + "="*50)
    print("REMOVE USER")
    print("="*50)
    
    email = input("Enter email of user to remove: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        return
    
    confirm = input(f"Are you sure you want to remove '{email}'? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("⚠️ Operation cancelled.")
        return
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ User '{email}' removed successfully!")
        else:
            print(f"⚠️ User '{email}' not found in database.")
        
    except Exception as e:
        print(f"❌ Error removing user: {e}")
    finally:
        cursor.close()
        conn.close()

def show_passwords():
    """Display all users and their passwords."""
    print("\n" + "="*50)
    print("USER PASSWORDS")
    print("="*50)
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT email, name FROM users ORDER BY name")
        users = cursor.fetchall()
        
        if not users:
            print("⚠️ No users found in database.")
            return
        
        print(f"\nFound {len(users)} users:\n")
        for i, (email, name) in enumerate(users, 1):
            print(f"{i}. {name} ({email})")
            print("   Note: Passwords are hashed - use 'Change Password' to set a new password")
            print()
        
    except Exception as e:
        print(f"❌ Error retrieving users: {e}")
    finally:
        cursor.close()
        conn.close()

def change_password():
    """Change a user's password."""
    print("\n" + "="*50)
    print("CHANGE PASSWORD")
    print("="*50)
    
    email = input("Enter email of user: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        return
    
    print("\nPassword options:")
    print("1. Generate random password")
    print("2. Enter custom password")
    choice = input("Choose option (1/2): ").strip()
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Get user's name for password generation
        cursor.execute("SELECT name FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if not result:
            print(f"⚠️ User '{email}' not found in database.")
            return
        
        name = result[0]
        
        if choice == '1':
            new_password = gen_password(name)
            print(f"Generated password: {new_password}")
        elif choice == '2':
            new_password = input("Enter new password: ").strip()
            if not new_password:
                print("❌ Password cannot be empty!")
                return
        else:
            print("❌ Invalid choice!")
            return
        
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        
        # Update in database
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        
        # Save to Excel for record
        output_file = f"password_change-{email.split('@')[0]}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df = pd.DataFrame([[email, name, new_password, hashed_password]], 
                         columns=["email", "name", "password", "bcrypt_password"])
        df.to_excel(output_file, index=False)
        
        print(f"✅ Password changed successfully for '{email}'!")
        print(f"✅ Credentials saved to '{output_file}'")
        
    except Exception as e:
        print(f"❌ Error changing password: {e}")
    finally:
        cursor.close()
        conn.close()

def main_menu():
    """Display and handle main menu."""
    while True:
        print("\n" + "="*50)
        print("USER MANAGEMENT SYSTEM")
        print("="*50)
        print("1. Add Users")
        print("2. Remove User")
        print("3. Show Users/Passwords")
        print("4. Change Password")
        print("5. Exit")
        print("="*50)
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == '1':
            add_users()
        elif choice == '2':
            remove_user()
        elif choice == '3':
            show_passwords()
        elif choice == '4':
            change_password()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please select 1-5.")

# --- Run Application ---
if __name__ == "__main__":
    main_menu()
