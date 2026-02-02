import pandas as pd
import bcrypt
import mysql.connector
from datetime import datetime
import os
import glob

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "0000",
    "database": "user_management"
}

def get_db_connection():
    """Establish database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def clean_previous_tests():
    """Clean up test data from previous runs."""
    print("\n" + "="*70)
    print("CLEANUP: Removing test users and Excel files")
    print("="*70)
    
    # Remove test Excel files
    for pattern in ["user_credentials-*.xlsx", "password_change-*.xlsx"]:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
                print(f"🗑️ Deleted: {file}")
            except Exception as e:
                print(f"⚠️ Could not delete {file}: {e}")
    
    # Remove test users from database
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email LIKE '%test.com'")
            deleted = cursor.rowcount
            conn.commit()
            print(f"🗑️ Deleted {deleted} test users from database")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"⚠️ Could not clean database: {e}")
    
    print("✅ Cleanup completed\n")

def verify_excel_file(filename, expected_emails):
    """Verify Excel file contains plain text passwords."""
    try:
        if not os.path.exists(filename):
            print(f"❌ Excel file not found: {filename}")
            return False
        
        df = pd.read_excel(filename)
        print(f"\n📄 Excel file: {filename}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Rows: {len(df)}")
        
        # Check for password column (plain text)
        if 'password' in df.columns:
            print(f"   ✅ Plain text passwords found:")
            for _, row in df.iterrows():
                email = row['email']
                password = row['password']
                print(f"      • {email}: {password}")
            return True
        else:
            print(f"   ❌ No plain text password column found")
            return False
            
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")
        return False

def verify_database_entry(email):
    """Verify database contains bcrypt hashed password."""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, password, created_at, updated_at FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if result:
            name, hashed_pwd, created, updated = result
            print(f"\n💾 Database entry for {email}:")
            print(f"   Name: {name}")
            print(f"   Password (bcrypt hash): {hashed_pwd[:50]}...")
            print(f"   Created: {created}")
            print(f"   Updated: {updated}")
            
            # Verify it's a bcrypt hash
            if hashed_pwd.startswith('$2b$'):
                print(f"   ✅ Valid bcrypt hash format")
                return True
            else:
                print(f"   ❌ Invalid hash format")
                return False
        else:
            print(f"❌ User {email} not found in database")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST SCENARIO 1: ADD USERS
# ============================================================================
def test_scenario_1_add_users():
    """Test adding users with plain passwords in Excel and bcrypt in DB."""
    print("\n" + "🔥"*35)
    print("SCENARIO 1: ADD USERS")
    print("🔥"*35)
    
    test_users = [
        ("alice.test@test.com", "Alice Wonder"),
        ("bob.test@test.com", "Bob Builder"),
        ("charlie.test@test.com", "Charlie Brown")
    ]
    
    # Generate passwords
    import random, string
    special_chars = r"!@#$%&*-_?/\|+=-.,><()"
    
    def gen_test_password(name):
        parts = name.strip().split()
        base = parts[0] if parts else "usr"
        name_part = base[:3].capitalize()
        digit = random.choice(string.digits)
        special = random.choice(special_chars)
        rand_char = random.choice(string.ascii_lowercase)
        others = [digit, special, rand_char]
        insert_pos = random.randint(0, 3)
        combined = others[:insert_pos] + [name_part] + others[insert_pos:]
        return ''.join(combined)
    
    # Build DataFrame
    df = pd.DataFrame(test_users, columns=["email", "name"])
    df["password"] = df["name"].apply(gen_test_password)
    df["bcrypt_password"] = df["password"].apply(lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode())
    
    # Save to Excel
    excel_file = f"user_credentials-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"✅ Excel file created: {excel_file}")
    
    # Insert into MySQL
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        success = 0
        for _, row in df.iterrows():
            cursor.callproc("sp_insert_user", (row["email"], row["name"], row["bcrypt_password"], "user"))
            success += 1
        conn.commit()
        print(f"✅ {success} users added to database")
        cursor.close()
        conn.close()
        
        # VERIFICATION
        print("\n" + "─"*70)
        print("VERIFICATION: Checking Excel has plain passwords, DB has bcrypt")
        print("─"*70)
        
        excel_ok = verify_excel_file(excel_file, [u[0] for u in test_users])
        
        db_ok = True
        for email, name in test_users:
            if not verify_database_entry(email):
                db_ok = False
        
        result = excel_ok and db_ok
        print("\n" + "─"*70)
        print(f"SCENARIO 1 RESULT: {'✅ PASSED' if result else '❌ FAILED'}")
        print("─"*70)
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================================================
# TEST SCENARIO 2: SHOW USERS
# ============================================================================
def test_scenario_2_show_users():
    """Test showing users from database."""
    print("\n" + "🔥"*35)
    print("SCENARIO 2: SHOW USERS")
    print("🔥"*35)
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, role, created_at FROM users WHERE email LIKE '%test.com' ORDER BY name")
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found")
            return False
        
        print(f"\n📋 Found {len(users)} users in database:\n")
        for user_id, email, name, role, created in users:
            print(f"  ID: {user_id} | Name: {name}")
            print(f"  Email: {email} | Role: {role}")
            print(f"  Created: {created}")
            print(f"  Note: Password is bcrypt hashed (not visible)")
            print("  " + "-"*60)
        
        cursor.close()
        conn.close()
        
        result = len(users) >= 3
        print(f"\nSCENARIO 2 RESULT: {'✅ PASSED' if result else '❌ FAILED'}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================================================
# TEST SCENARIO 3: CHANGE PASSWORD
# ============================================================================
def test_scenario_3_change_password():
    """Test changing password with new Excel file and DB update."""
    print("\n" + "🔥"*35)
    print("SCENARIO 3: CHANGE PASSWORD")
    print("🔥"*35)
    
    test_email = "alice.test@test.com"
    new_password = "NewSecure2026!"
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, password FROM users WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ User not found")
            return False
        
        name, old_hash = result
        print(f"👤 User: {name} ({test_email})")
        print(f"🔒 Old password hash: {old_hash[:50]}...")
        
        # Generate new hash
        new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        
        # Update database
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_hash, test_email))
        conn.commit()
        print(f"✅ Database updated with new password hash")
        
        # Save to Excel
        excel_file = f"password_change-{test_email.split('@')[0]}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df = pd.DataFrame([[test_email, name, new_password, new_hash]], 
                         columns=["email", "name", "password", "bcrypt_password"])
        df.to_excel(excel_file, index=False)
        print(f"✅ Excel file created: {excel_file}")
        
        cursor.close()
        conn.close()
        
        # VERIFICATION
        print("\n" + "─"*70)
        print("VERIFICATION: New password in Excel, new hash in DB")
        print("─"*70)
        
        excel_ok = verify_excel_file(excel_file, [test_email])
        db_ok = verify_database_entry(test_email)
        
        result = excel_ok and db_ok
        print("\n" + "─"*70)
        print(f"SCENARIO 3 RESULT: {'✅ PASSED' if result else '❌ FAILED'}")
        print("─"*70)
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================================================
# TEST SCENARIO 4: VERIFY PASSWORD
# ============================================================================
def test_scenario_4_verify_password():
    """Test password verification using bcrypt."""
    print("\n" + "🔥"*35)
    print("SCENARIO 4: VERIFY PASSWORD")
    print("🔥"*35)
    
    test_email = "alice.test@test.com"
    test_password = "NewSecure2026!"  # From previous scenario
    wrong_password = "WrongPassword123"
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name, password FROM users WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ User not found")
            return False
        
        name, stored_hash = result
        print(f"👤 Testing password for: {name} ({test_email})")
        
        # Test correct password
        print(f"\n🔑 Testing correct password: '{test_password}'")
        if bcrypt.checkpw(test_password.encode(), stored_hash.encode()):
            print(f"   ✅ Correct password verified!")
            correct_ok = True
        else:
            print(f"   ❌ Verification failed!")
            correct_ok = False
        
        # Test wrong password
        print(f"\n🔑 Testing wrong password: '{wrong_password}'")
        if not bcrypt.checkpw(wrong_password.encode(), stored_hash.encode()):
            print(f"   ✅ Wrong password correctly rejected!")
            wrong_ok = True
        else:
            print(f"   ❌ Wrong password was accepted (should not happen)!")
            wrong_ok = False
        
        cursor.close()
        conn.close()
        
        result = correct_ok and wrong_ok
        print(f"\nSCENARIO 4 RESULT: {'✅ PASSED' if result else '❌ FAILED'}")
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================================================
# TEST SCENARIO 5: REMOVE USER
# ============================================================================
def test_scenario_5_remove_user():
    """Test removing a user from database."""
    print("\n" + "🔥"*35)
    print("SCENARIO 5: REMOVE USER")
    print("🔥"*35)
    
    test_email = "charlie.test@test.com"
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute("SELECT name FROM users WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ User not found before deletion")
            return False
        
        name = result[0]
        print(f"👤 Found user: {name} ({test_email})")
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
        conn.commit()
        deleted_count = cursor.rowcount
        
        if deleted_count > 0:
            print(f"✅ User deleted from database")
        else:
            print(f"❌ No user was deleted")
            return False
        
        # Verify deletion
        cursor.execute("SELECT * FROM users WHERE email = %s", (test_email,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result is None:
            print(f"✅ Verified: User no longer exists in database")
            print(f"\nSCENARIO 5 RESULT: ✅ PASSED")
            return True
        else:
            print(f"❌ User still exists in database")
            print(f"\nSCENARIO 5 RESULT: ❌ FAILED")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ============================================================================
# FINAL SUMMARY
# ============================================================================
def run_complete_test():
    """Run all 5 scenarios and provide summary."""
    print("\n" + "🚀 "*35)
    print("COMPREHENSIVE TEST: ALL 5 SCENARIOS")
    print("Testing Excel (plain passwords) + Database (bcrypt hashes)")
    print("🚀 "*35)
    
    # Clean previous test data
    clean_previous_tests()
    
    # Run all scenarios
    results = {
        "1. Add Users (Excel + DB)": test_scenario_1_add_users(),
        "2. Show Users": test_scenario_2_show_users(),
        "3. Change Password (Excel + DB)": test_scenario_3_change_password(),
        "4. Verify Password (Bcrypt)": test_scenario_4_verify_password(),
        "5. Remove User": test_scenario_5_remove_user()
    }
    
    # Final summary
    print("\n\n" + "="*70)
    print("🏆 FINAL TEST SUMMARY")
    print("="*70)
    
    for scenario, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{scenario}: {status}")
    
    print("="*70)
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\nResults: {passed_count}/{total_count} scenarios passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL SCENARIOS PASSED!")
        print("\n✅ Plain text passwords → Stored in Excel files")
        print("✅ Bcrypt hashed passwords → Stored in Database")
        print("✅ Full application functionality verified!")
    else:
        print(f"\n⚠️ {total_count - passed_count} scenario(s) failed")
    
    print("="*70)
    
    # List Excel files created
    print("\n📄 Excel files created during test:")
    excel_files = glob.glob("user_credentials-*.xlsx") + glob.glob("password_change-*.xlsx")
    for f in excel_files:
        print(f"   • {f}")

if __name__ == "__main__":
    run_complete_test()
