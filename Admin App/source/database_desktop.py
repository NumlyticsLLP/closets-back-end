"""
Database Module for Desktop Application with Mode Support
Handles all database operations with Test/Production mode support
"""
import mysql.connector
import bcrypt
import pandas as pd
import json
import os
from config import DB_CONFIG

# Global variables for current session
current_db_config = None
current_mode = None
error_logged = {}  # Track which errors have been logged to avoid duplicates

def parse_connection_string(connection_string):
    """
    Parse connection string to extract host, port, and database.
    
    Format: hostname:port/database_name or hostname/database_name
    Examples:
    - localhost:3306/mydb
    - 192.168.1.1:3306/database
    - localhost/mydb (uses default port 3306)
    """
    try:
        # Split by / to separate host:port from database
        if '/' not in connection_string:
            raise ValueError("Connection string must include database: hostname:port/database")
        
        host_port_part, database = connection_string.rsplit('/', 1)
        
        # Split host and port
        if ':' in host_port_part:
            host, port = host_port_part.rsplit(':', 1)
            port = int(port)
        else:
            host = host_port_part
            port = 3306  # Default MySQL port
        
        return {
            'host': host.strip(),
            'port': port,
            'database': database.strip()
        }
    except Exception as e:
        raise ValueError(f"Invalid connection string format: {str(e)}")

def fetch_database_tables(connection_string, username, password):
    """
    Fetch list of tables from the specified database using connection details.
    
    Args:
        connection_string: Format 'host:port/database' or 'host/database'
        username: Database username
        password: Database password
    
    Returns:
        List of table names, or empty list if connection fails
    """
    try:
        # Parse the connection string
        conn_params = parse_connection_string(connection_string)
        
        # Create connection config
        config = {
            'host': conn_params['host'],
            'port': conn_params['port'],
            'user': username,
            'password': password,
            'database': conn_params['database'],
            'use_pure': True  # Use pure Python connector
        }
        
        # Establish connection
        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Get all tables in the database
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Extract table names from tuples
            table_list = [table[0] for table in tables]
            return table_list
        
        return []
        
    except mysql.connector.Error as db_err:
        return []
    except ValueError as ve:
        return []
    except Exception as e:
        return []

def fetch_table_columns(connection_string, username, password, table_name):
    """
    Fetch column names and types from a specific table.
    
    Args:
        connection_string: Format 'host:port/database' or 'host/database'
        username: Database username
        password: Database password
        table_name: Name of the table to get columns from
    
    Returns:
        List of dictionaries with column info: [{'name': 'col_name', 'type': 'VARCHAR'}, ...]
        or empty list if connection fails
    """
    try:
        # Parse the connection string
        conn_params = parse_connection_string(connection_string)
        
        # Create connection config
        config = {
            'host': conn_params['host'],
            'port': conn_params['port'],
            'user': username,
            'password': password,
            'database': conn_params['database'],
            'use_pure': True  # Use pure Python connector
        }
        
        # Establish connection
        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Get column information from the table
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns_info = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Parse column information
            columns = []
            for col_info in columns_info:
                columns.append({
                    'name': col_info[0],
                    'type': col_info[1],
                    'null': col_info[2],
                    'key': col_info[3],
                    'default': col_info[4],
                    'extra': col_info[5]
                })
            
            return columns
        
        return []
        
    except mysql.connector.Error as db_err:
        return []
    except Exception as e:
        return []

def load_session_config(mode=None):
    """Load session configuration based on available session files.
    
    Args:
        mode: If specified, loads only that mode. Otherwise auto-detects.
    """
    global current_db_config, current_mode
    
    # If mode is specified, load only that mode
    if mode:
        config_file = f"session_db_config_{mode}.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                current_db_config = config
                current_mode = mode
                return config
            except Exception as e:
                pass
        return None
    
    # Auto-detect: Check for session config files (Test/Production modes)
    for mode in ['test', 'production']:
        config_file = f"session_db_config_{mode}.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                current_db_config = config
                current_mode = mode
                return config
            except:
                pass
    
    # Fallback to legacy DB_CONFIG 
    if DB_CONFIG:
        current_db_config = DB_CONFIG
        current_mode = "legacy"
        return DB_CONFIG
    
    return None

def get_current_mode():
    """Get the current application mode."""
    global current_mode
    if not current_mode:
        load_session_config()
    return current_mode or "unknown"

def reload_session_config(mode=None):
    """Reload session configuration from files (used after mode switch).
    
    Args:
        mode: If specified, loads that specific mode. Otherwise auto-detects.
    """
    global current_db_config, current_mode
    current_db_config = None
    current_mode = None
    return load_session_config(mode)

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

def load_table_session_config():
    """Load table session configuration based on available session files."""
    # Check for session table config files (Test/Production modes)
    for mode in ['test', 'production']:
        config_file = f"session_table_config_{mode}.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return config
            except:
                pass
    
    return None

def get_current_table_info():
    """Get current table information from session config."""
    table_config = load_table_session_config()
    return table_config if table_config else {}


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
        
        # Create users_audit table for logging user activities
        audit_table_sql = """
        CREATE TABLE IF NOT EXISTS users_audit (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            action VARCHAR(50) NOT NULL,
            action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_action_at (action_at),
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(audit_table_sql)
        
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
        return False
    except Exception as e:
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
        return None
    
    try:
        # Prepare config for connection (remove mode key if present)
        config = config_to_use.copy()
        config.pop('mode', None)
        
        # CRITICAL: Always use pure Python MySQL connector to avoid PyQt6 C extension conflicts
        config['use_pure'] = True
        # Disable SSL for local connections to avoid SSL handshake hangs
        config.setdefault('ssl_disabled', True)
        
        # Try to connect to the database
        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            return conn
            
    except mysql.connector.Error as db_err:
        # Handle specific MySQL error codes
        if db_err.errno == 1049:  # Unknown database error
            if initialize_database():
                # Try connecting again after initialization
                try:
                    conn = mysql.connector.connect(**config)
                    if conn.is_connected():
                        return conn
                except Exception as retry_err:
                    pass
        
        return None
        
    except Exception as e:
        pass


def verify_admin_credentials(email, password):
    """
    Verify admin login credentials with flexible admin detection.
    Simply searches existing database for admin users - no setup required.
    """
    conn = get_db_connection()
    if not conn:
        return False, {"error": "Database connection unavailable"}
    
    try:
        cursor = conn.cursor()
        
        # Direct search for user in existing database
        cursor.execute("SELECT id, email, name, password, role FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            user_id, user_email, user_name, hashed_password, role = user
            
            # Verify password against existing hash
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                
                # Auto-detect admin privileges from existing data
                is_admin = False
                
                # Method 1: Check role column for 'admin'
                if role and role.lower() in ['admin', 'administrator', 'superuser', 'root']:
                    is_admin = True
                
                # Method 2: Check if user ID = 1 (often the first/primary admin)
                elif user_id == 1:
                    is_admin = True
                
                # Method 3: Check for admin-like email patterns
                elif any(admin_pattern in user_email.lower() for admin_pattern in ['admin', 'administrator', 'root', 'superuser']):
                    is_admin = True
                
                if is_admin:
                    return True, {"id": user_id, "email": user_email, "name": user_name, "role": role}
                else:
                    return False, {"error": "Access denied. Administrator privileges required."}
            else:
                return False, {"error": "Invalid password"}
        else:
            return False, {"error": "User not found"}
        
    except Exception as e:
        return False, {"error": f"Authentication error: {str(e)}"}
    finally:
        cursor.close()
        conn.close()


def get_all_users():
    """Retrieve all users from database."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        # First check if the users table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            # Users table doesn't exist, return empty DataFrame
            # This allows fallback to custom table
            cursor.close()
            conn.close()
            return pd.DataFrame()
        
        cursor.execute("SELECT id, email, name, role, created_at, updated_at FROM users ORDER BY name")
        users = cursor.fetchall()
        df = pd.DataFrame(users, columns=["ID", "Email", "Name", "Role", "Created", "Updated"])
        cursor.close()
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()


def get_all_records_from_table(connection_string, username, password, database_name, table_name):
    """
    Retrieve all records from a specified table with dynamic columns.
    
    Args:
        connection_string: Format 'host:port/database' or 'host/database'
        username: Database username
        password: Database password
        database_name: Database name
        table_name: Table name to retrieve from
    
    Returns:
        DataFrame with table data or empty DataFrame if fails
    """
    try:
        # Parse the connection string
        conn_params = parse_connection_string(connection_string)
        
        # Create connection config
        config = {
            'host': conn_params['host'],
            'port': conn_params['port'],
            'user': username,
            'password': password,
            'database': database_name,
            'use_pure': True  # Use pure Python connector
        }
        
        # Establish connection
        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Get all data from the table
            cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY 1 LIMIT 1000")
            records = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns_info = cursor.fetchall()
            column_names = [col[0] for col in columns_info]
            
            cursor.close()
            conn.close()
            
            if records:
                df = pd.DataFrame(records, columns=column_names)
                return df
            else:
                return pd.DataFrame(columns=column_names)
        
        return pd.DataFrame()
        
    except mysql.connector.Error as db_err:
        pass
        return pd.DataFrame()
    except Exception as e:
        pass
        return pd.DataFrame()


def get_user_by_id(user_id):
    """Retrieve a specific user by ID."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, role, created_at, updated_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'role': user[3],
                'created_at': user[4],
                'updated_at': user[5]
            }
        else:
            return None
    except Exception as e:
        pass
        return None


def update_user_info(user_id, name, email, role):
    """Update user information (name, email, role) and log to users_audit (SCD Type 2)."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Check if email already exists for another user
        cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            conn.close()
            return False, "Email already exists for another user"
        
        # Get current user details
        cursor.execute("SELECT email, password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return False, "User not found"
        
        current_email, current_password = user
        
        # Close out current version in audit table (SCD Type 2)
        cursor.execute("""
            UPDATE users_audit 
            SET effective_end_date = NOW(), is_current = 0
            WHERE userid = %s AND is_current = 1
        """, (user_id,))
        
        # Update user info in users table
        cursor.execute("""
            UPDATE users SET name = %s, email = %s, role = %s, updated_at = NOW() WHERE id = %s
        """, (name, email, role, user_id))
        
        # Log update to audit table as new current version
        cursor.execute("""
            INSERT INTO users_audit 
            (userid, email, designername, password, role, audit_action, effective_start_date, is_current)
            VALUES (%s, %s, %s, %s, %s, 'UPDATE', NOW(), 1)
        """, (user_id, email, name, current_password, role))
        
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()
        
        if rows_affected > 0:
            return True, "User information updated successfully"
        else:
            return False, "Failed to update user"
    except Exception as e:
        pass
        return False, str(e)


def get_user_count():
    """Get total count of users from the configured table."""
    global error_logged
    try:
        # Check if a custom table is configured
        table_info = get_current_table_info()
        
        if table_info and table_info.get('table'):
            # Use custom table
            custom_table = table_info.get('table')
            database = table_info.get('database', '')
            connection_string = table_info.get('connection_string', '')
            username = table_info.get('username', '')
            password = table_info.get('password', '')
            
            if connection_string and username and password:
                try:
                    # Parse connection string
                    parts = connection_string.split('/')
                    host_port = parts[0]
                    
                    host_parts = host_port.split(':')
                    host = host_parts[0]
                    port = int(host_parts[1]) if len(host_parts) > 1 else 3306
                    
                    # Connect to custom table database
                    conn = mysql.connector.connect(
                        host=host,
                        port=port,
                        user=username,
                        password=password,
                        database=database,
                        use_pure=True
                    )
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM `{custom_table}`")
                    count = cursor.fetchone()[0]
                    cursor.close()
                    conn.close()
                    return count
                except Exception as e:
                    error_key = "get_user_count_custom"
                    if error_key not in error_logged:
                        pass
                        error_logged[error_key] = True
                    return 0
        
        # Fall back to default users table
        conn = get_db_connection()
        if not conn:
            return 0
        
        cursor = conn.cursor()
        # Count all users directly from the users table
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        error_key = "get_user_count"
        if error_key not in error_logged:
            pass
            error_logged[error_key] = True
        return 0


def get_today_users_count():
    """Get count of users added today from the configured table."""
    global error_logged
    try:
        # Check if a custom table is configured
        table_info = get_current_table_info()
        
        if table_info and table_info.get('table'):
            # For custom tables, we don't know the date column schema
            # So return 0 to avoid incorrect counts
            return 0
        
        # Fall back to default users table using created_at
        conn = get_db_connection()
        if not conn:
            return 0
        
        cursor = conn.cursor()
        # Count users created today using the users table directly
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURDATE()")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count
    except Exception as e:
        error_key = "get_today_users_count"
        if error_key not in error_logged:
            pass
            error_logged[error_key] = True
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
    """Add a new user to the database and log to users_audit."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (email, name, role, password, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (email, name, role, hashed_password))
        
        # Get the inserted user's ID
        user_id = cursor.lastrowid
        
        # Log to audit table
        cursor.execute("""
            INSERT INTO users_audit 
            (userid, email, designername, password, role, audit_action, is_current)
            VALUES (%s, %s, %s, %s, %s, 'INSERT', 1)
        """, (user_id, email, name, hashed_password, role))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, "User added successfully"
    except Exception as e:
        pass
        return False, str(e)


def remove_user(email_or_id, table_config=None):
    """Remove a user from the database and log to users_audit (SCD Type 2)."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Get user details before deleting
        cursor.execute("SELECT id, email, name, password, role FROM users WHERE email = %s", (email_or_id,))
        user = cursor.fetchone()
        
        if user:
            user_id, email, name, password, role = user
            
            # Close out current version in audit table (SCD Type 2)
            cursor.execute("""
                UPDATE users_audit 
                SET effective_end_date = NOW(), is_current = 0
                WHERE userid = %s AND is_current = 1
            """, (user_id,))
            
            # Delete from users table
            cursor.execute("DELETE FROM users WHERE email = %s", (email_or_id,))
            
            # Log deletion to audit table with end date
            cursor.execute("""
                INSERT INTO users_audit 
                (userid, email, designername, password, role, audit_action, effective_start_date, effective_end_date, is_current)
                VALUES (%s, %s, %s, %s, %s, 'DELETE', NOW(), NOW(), 0)
            """, (user_id, email, name, password, role))
            
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()
            
            if rows_affected > 0:
                return True, "User removed successfully"
            else:
                return False, "User not found"
        else:
            cursor.close()
            conn.close()
            return False, "User not found"
    except Exception as e:
        pass
        return False, str(e)


def change_password(email, new_password):
    """Change user password and log to users_audit (SCD Type 2)."""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        # Hash password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor = conn.cursor()
        
        # Get user details before updating
        cursor.execute("""
            SELECT id, email, name, role FROM users WHERE email = %s
        """, (email,))

        user = cursor.fetchone()
        
        if user:
            user_id, user_email, name, role = user
            
            # Close out current version in audit table (SCD Type 2)
            # Mark old version as historical with end date
            cursor.execute("""
                UPDATE users_audit 
                SET effective_end_date = NOW(), is_current = 0
                WHERE userid = %s AND is_current = 1
            """, (user_id,))
            
            # Update password in users table
            cursor.execute("""
                UPDATE users SET password = %s, updated_at = NOW() WHERE email = %s
            """, (hashed_password, email))
            
            # Log update to audit table as new current version
            cursor.execute("""
                INSERT INTO users_audit 
                (userid, email, designername, password, role, audit_action, effective_start_date, is_current)
                VALUES (%s, %s, %s, %s, %s, 'UPDATE', NOW(), 1)
            """, (user_id, user_email, name, hashed_password, role))
            
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            conn.close()
            
            if rows_affected > 0:
                return True, "Password changed successfully"
            else:
                return False, "User not found"
        else:
            cursor.close()
            conn.close()
            return False, "User not found"
    except Exception as e:
        pass
        return False, str(e)


# ============================================================================
# AUDIT LOGGING FUNCTIONS FOR USERS TABLE
# ============================================================================

def log_audit(user_id, email, name, password, role, action):
    """
    Log user action to users_audit table.
    
    Args:
        user_id: User ID
        email: User email
        name: User name (designername)
        password: User password (can be hashed or placeholder)
        role: User role
        action: Action type (INSERT, UPDATE, DELETE)
    
    Returns:
        Tuple (success: bool, message: str)
    """
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users_audit 
            (userid, email, designername, password, role, audit_action, is_current)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, (user_id, email, name, password, role, action))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Audit logged successfully"
    except Exception as e:
        pass
        return False, str(e)


def get_audit_history(user_id):
    """Retrieve audit history for a specific user."""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT audit_id, audit_action, audit_user, userid, email, designername, 
                   effective_start_date, effective_end_date, is_current
            FROM users_audit
            WHERE userid = %s
            ORDER BY effective_start_date DESC
            LIMIT 100
        """, (user_id,))
        
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if records:
            return records
        return None
    except Exception as e:
        pass
        return None


def get_all_audit_records(limit=1000):
    """
    Retrieve all audit records from users_audit table.
    
    Returns:
        DataFrame with audit records or empty DataFrame if fails
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                audit_id, 
                userid, 
                email, 
                designername, 
                role, 
                audit_action, 
                audit_user,
                effective_start_date,
                effective_end_date,
                is_current
            FROM users_audit
            ORDER BY effective_start_date DESC, audit_id DESC
            LIMIT %s
        """, (limit,))
        
        records = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        if records:
            df = pd.DataFrame(records, columns=columns)
            return df
        else:
            return pd.DataFrame(columns=columns)
    except Exception as e:
        pass
        return pd.DataFrame()


def get_user_audit_trail(user_id):
    """
    Get complete audit trail for a specific user (all versions).
    
    Returns:
        DataFrame with user's audit history
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                audit_id, 
                userid, 
                email, 
                designername, 
                role, 
                audit_action, 
                audit_user,
                effective_start_date,
                effective_end_date,
                is_current
            FROM users_audit
            WHERE userid = %s
            ORDER BY effective_start_date DESC
        """, (user_id,))
        
        records = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        if records:
            df = pd.DataFrame(records, columns=columns)
            return df
        else:
            return pd.DataFrame(columns=columns)
    except Exception as e:
        pass
        return pd.DataFrame()


def get_users_with_audit_dates(limit=1000):
    """
    Get current users with created and updated dates from audit table.
    Created date = first (MIN) effective_start_date for each user
    Updated date = last (MAX) effective_start_date for each user
    
    Returns:
        DataFrame with user data including aggregated dates
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                ua.userid,
                ua.email,
                ua.designername,
                ua.role,
                ua.audit_action,
                ua.audit_user,
                ua.effective_start_date,
                ua.effective_end_date,
                ua.is_current,
                MIN(ua2.effective_start_date) as created_date,
                MAX(ua2.effective_start_date) as updated_date
            FROM users_audit ua
            INNER JOIN users_audit ua2 ON ua.userid = ua2.userid
            WHERE ua.is_current = 1
            GROUP BY ua.userid, ua.email, ua.designername, ua.role, 
                     ua.audit_action, ua.audit_user, ua.effective_start_date,
                     ua.effective_end_date, ua.is_current
            ORDER BY ua.userid DESC
            LIMIT %s
        """, (limit,))
        
        records = cursor.fetchall()
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        if records:
            df = pd.DataFrame(records, columns=columns)
            return df
        else:
            return pd.DataFrame(columns=columns)
    except Exception as e:
        pass
        return pd.DataFrame()
