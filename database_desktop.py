"""
Database Module for Desktop Application
Handles all database operations without Streamlit dependencies
"""
import mysql.connector
import bcrypt
import pandas as pd
import logging
from config import DB_CONFIG

logger = logging.getLogger(__name__)


def get_db_connection():
    """Establish database connection."""
    try:
        logger.info(f"Connecting to database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
        conn = mysql.connector.connect(**DB_CONFIG)
        logger.info("Database connection established successfully")
        return conn
    except mysql.connector.Error as db_err:
        logger.error(f"MySQL connection error: {db_err}")
        logger.error(f"Error code: {db_err.errno}")
        logger.error(f"SQL State: {db_err.sqlstate}")
        print(f"MySQL connection error: {db_err}")
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        print(f"Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return None


def verify_admin_credentials(email, password):
    """Verify admin login credentials."""
    logger.info(f"Login attempt for email: {email}")
    conn = get_db_connection()
    if not conn:
        logger.error("Login failed: Database connection unavailable")
        return False, None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            user_id, user_email, user_name, hashed_password, role = user
            logger.info(f"User found: {user_name} (Role: {role})")
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                logger.info("Password verification: SUCCESS")
                # Check if user is admin
                if role and role.lower() == 'admin':
                    logger.info(f"Admin login successful: {user_name}")
                    return True, {"id": user_id, "email": user_email, "name": user_name, "role": role}
                else:
                    logger.warning(f"Access denied: User '{user_name}' is not an admin")
                    return False, {"error": "Access denied. Admin privileges required."}
            else:
                logger.warning("Password verification: FAILED")
        else:
            logger.warning(f"User not found: {email}")
        
        return False, None
    except Exception as e:
        logger.error(f"Login error: {e}")
        print(f"Login error: {e}")
        return False, None


def get_all_users():
    """Retrieve all users from database."""
    logger.info("Fetching all users from database")
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to retrieve users: No database connection")
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, role, created_at, updated_at FROM users ORDER BY name")
        users = cursor.fetchall()
        df = pd.DataFrame(users, columns=["ID", "Email", "Name", "Role", "Created", "Updated"])
        cursor.close()
        conn.close()
        logger.info(f"Retrieved {len(df)} users successfully")
        return df
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        print(f"Error retrieving users: {e}")
        return pd.DataFrame()


def get_user_count():
    """Get total count of users."""
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except:
        return 0


def get_today_users_count():
    """Get count of users added today."""
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except:
        return 0


def get_updated_today_count():
    """Get count of users updated today."""
    conn = get_db_connection()
    if not conn:
        return 0
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(updated_at) = CURDATE()")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except:
        return 0


def add_user(email, name, password, role='user'):
    """Add a new user to the database."""
    logger.info(f"Adding new user: {name} ({email}) with role: {role}")
    conn = get_db_connection()
    if not conn:
        logger.error("Add user failed: Database connection failed")
        return False, "Database connection failed"
    
    try:
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (email, name, role, password, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (email, name, role, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"User added successfully: {name} ({email})")
        return True, "User added successfully"
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False, str(e)


def remove_user(email):
    """Remove a user from the database."""
    logger.info(f"Attempting to remove user: {email}")
    conn = get_db_connection()
    if not conn:
        logger.error("Remove user failed: Database connection failed")
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()
        
        if rows_affected > 0:
            logger.info(f"User removed successfully: {email}")
            return True, "User removed successfully"
        else:
            logger.warning(f"User not found: {email}")
            return False, "User not found"
    except Exception as e:
        logger.error(f"Error removing user: {e}")
        return False, str(e)


def change_password(email, new_password):
    """Change user password."""
    logger.info(f"Changing password for user: {email}")
    conn = get_db_connection()
    if not conn:
        logger.error("Change password failed: Database connection failed")
        return False, "Database connection failed"
    
    try:
        # Hash password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET password = %s, updated_at = NOW() WHERE email = %s
        """, (hashed_password, email))
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()
        
        if rows_affected > 0:
            logger.info(f"Password changed successfully for: {email}")
            return True, "Password changed successfully"
        else:
            logger.warning(f"User not found for password change: {email}")
            return False, "User not found"
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return False, str(e)
