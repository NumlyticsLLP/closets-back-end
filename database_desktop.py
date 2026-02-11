"""
Database Module for Desktop Application with Mode Support
Handles all database operations with Test/Production mode support
"""
import mysql.connector
import bcrypt
import pandas as pd
import logging
import json
import os
from config import DB_CONFIG

logger = logging.getLogger(__name__)

# Global variables for current session
current_db_config = None
current_mode = None

def load_session_config():
    """Load session configuration based on available session files."""
    global current_db_config, current_mode
    
    # Check for session config files (Test/Production modes)
    for mode in ['test', 'production']:
        config_file = f"session_db_config_{mode}.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                current_db_config = config
                current_mode = mode
                return config
            except Exception as e:
                logger.warning(f"⚠️ Could not load {config_file}: {e}")
    
    # Fallback to legacy DB_CONFIG 
    if DB_CONFIG:
        current_db_config = DB_CONFIG
        current_mode = "legacy"
        return DB_CONFIG
    
    logger.error("❌ No valid database configuration found")
    return None

def get_current_mode():
    """Get the current application mode."""
    global current_mode
    if not current_mode:
        load_session_config()
    return current_mode or "unknown"

def get_mode_info():
    """Get detailed information about current mode."""
    global current_db_config, current_mode
    
    if not current_db_config:
        load_session_config()
    
    if current_db_config and current_mode:
        return {
            'mode': current_mode,
            'host': current_db_config.get('host', 'unknown'),
            'database': current_db_config.get('database', 'unknown'),
            'user': current_db_config.get('user', 'unknown')
        }
    
    return {
        'mode': 'unknown',
        'host': 'unknown', 
        'database': 'unknown',
        'user': 'unknown'
    }


def initialize_database():
    """Initialize database and create tables if they don't exist."""
    try:
        # First, try to connect without specifying a database
        temp_config = current_db_config.copy() if current_db_config else {}
        database_name = temp_config.pop('database', 'user_management')
        temp_config.pop('mode', None)
        
        # CRITICAL: Always use pure Python MySQL connector to avoid PyQt6 C extension conflicts
        temp_config['use_pure'] = True
        
        # Connect to MySQL server (without specific database)
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}`")
        cursor.execute(f"USE `{database_name}`")
        
        # Create users table if it doesn't exist
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_role (role),
            INDEX idx_created_at (created_at)
        )
        """
        cursor.execute(create_table_sql)
        
        # Check if we need to create a default admin
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # Create default admin
            password = "admin123"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute(
                "INSERT INTO users (email, name, password, role) VALUES (%s, %s, %s, %s)",
                ('admin@example.com', 'System Administrator', hashed, 'admin')
            )
            conn.commit()
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as db_err:
        logger.error(f"❌ Database initialization error: {db_err}")
        return False
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def get_db_connection():
    """Establish database connection using current mode configuration."""
    global current_db_config, current_mode
    
    # Load config if not already loaded
    if not current_db_config:
        load_session_config()
    
    # Use mode-based config if available, otherwise fallback to DB_CONFIG
    config_to_use = current_db_config if current_db_config else DB_CONFIG
    
    if not config_to_use:
        logger.error("❌ No database configuration available")
        return None
    
    try:
        # Prepare config for connection (remove mode key if present)
        config = config_to_use.copy()
        config.pop('mode', None)
        
        # CRITICAL: Always use pure Python MySQL connector to avoid PyQt6 C extension conflicts
        config['use_pure'] = True
        
        # Try to connect to the database
        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            return conn
            
    except mysql.connector.Error as db_err:
        logger.error(f"❌ MySQL connection error ({current_mode or 'legacy'} mode): {db_err}")
        
        # Handle specific MySQL error codes
        if db_err.errno == 1049:  # Unknown database error
            if initialize_database():
                # Try connecting again after initialization
                try:
                    conn = mysql.connector.connect(**config)
                    if conn.is_connected():
                        return conn
                except Exception as retry_err:
                    logger.error(f"❌ Failed to connect after initialization: {retry_err}")
        elif db_err.errno == 2003:  # Can't connect to MySQL server
            logger.error("❌ MySQL server is not running or not accessible")
            logger.error("💡 Please start your MySQL server and try again")
        elif db_err.errno == 1045:  # Access denied
            logger.error("❌ Access denied - check your username and password")
        else:
            logger.error(f"Error code: {db_err.errno}")
            logger.error(f"SQL State: {db_err.sqlstate}")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        import traceback
        logger.error(f"📋 Connection traceback: {traceback.format_exc()}")
        
        # Don't let any database errors crash the app
        try:
            error_str = str(e).lower()
            if "mysql" in error_str and "not" in error_str and "running" in error_str:
                logger.error("💡 MySQL server appears to be offline")
            elif "access denied" in error_str:
                logger.error("💡 MySQL access denied - check credentials")
            elif "unknown database" in error_str:
                logger.error("💡 Database doesn't exist - will be created automatically")
        except:
            pass  # Don't let error parsing itself cause issues
            
        return None


def verify_admin_credentials(email, password):
    """
    Verify admin login credentials with flexible admin detection.
    Simply searches existing database for admin users - no setup required.
    """
    logger.info(f"Login attempt for email: {email}")
    conn = get_db_connection()
    if not conn:
        logger.error("Login failed: Database connection unavailable")
        return False, {"error": "Database connection unavailable"}
    
    try:
        cursor = conn.cursor()
        
        # Direct search for user in existing database
        cursor.execute("SELECT id, email, name, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            user_id, user_email, user_name, hashed_password, role = user
            logger.info(f"User found: {user_name} (Role: {role})")
            
            # Verify password against existing hash
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                logger.info("Password verification: SUCCESS")
                
                # Auto-detect admin privileges from existing data
                is_admin = False
                
                # Method 1: Check role column for 'admin'
                if role and role.lower() in ['admin', 'administrator', 'superuser', 'root']:
                    is_admin = True
                    logger.info(f"Admin detected via role: {role}")
                
                # Method 2: Check if user ID = 1 (often the first/primary admin)
                elif user_id == 1:
                    is_admin = True
                    logger.info("Admin detected via user ID = 1 (primary admin)")
                
                # Method 3: Check for admin-like email patterns
                elif any(admin_pattern in user_email.lower() for admin_pattern in ['admin', 'administrator', 'root', 'superuser']):
                    is_admin = True
                    logger.info(f"Admin detected via email pattern: {user_email}")
                
                if is_admin:
                    logger.info(f"Admin login successful: {user_name}")
                    return True, {"id": user_id, "email": user_email, "name": user_name, "role": role}
                else:
                    logger.warning(f"Access denied: User '{user_name}' does not have admin privileges")
                    return False, {"error": "Access denied. Administrator privileges required."}
            else:
                logger.warning("Password verification: FAILED")
                return False, {"error": "Invalid password"}
        else:
            logger.warning(f"User not found: {email}")
            return False, {"error": "User not found"}
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        print(f"Login error: {e}")
        return False, {"error": f"Authentication error: {str(e)}"}
    finally:
        cursor.close()
        conn.close()


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
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("⚠️ No database connection for user count")
            return 0
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        logger.error(f"❌ Error getting user count: {e}")
        return 0


def get_today_users_count():
    """Get count of users added today."""
    try:
        conn = get_db_connection()
        if not conn:
            logger.warning("⚠️ No database connection for today users count")
            return 0
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        logger.error(f"❌ Error getting today users count: {e}")
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
