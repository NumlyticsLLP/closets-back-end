import mysql.connector

# Database configuration
config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "0000"
}

print("Creating database and tables...")

try:
    # Connect to MySQL server
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS user_management")
    print("✅ Database 'user_management' created/verified")
    
    # Use the database
    cursor.execute("USE user_management")
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            password TEXT NOT NULL,
            role VARCHAR(50) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    print("✅ Table 'users' created/verified")
    
    # Drop procedure if exists
    cursor.execute("DROP PROCEDURE IF EXISTS sp_insert_user")
    
    # Create stored procedure
    cursor.execute("""
        CREATE PROCEDURE sp_insert_user(
            IN p_email VARCHAR(255),
            IN p_name VARCHAR(255),
            IN p_password TEXT,
            IN p_role VARCHAR(50)
        )
        BEGIN
            INSERT INTO users (email, name, password, role)
            VALUES (p_email, p_name, p_password, p_role)
            ON DUPLICATE KEY UPDATE
                name = p_name,
                password = p_password,
                role = p_role,
                updated_at = CURRENT_TIMESTAMP;
        END
    """)
    print("✅ Stored procedure 'sp_insert_user' created")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ Database setup completed successfully!")
    print("="*50)
    print("Database: user_management")
    print("Table: users")
    print("Stored Procedure: sp_insert_user")
    
except Exception as e:
    print(f"❌ Error setting up database: {e}")
