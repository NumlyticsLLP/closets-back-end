-- Create database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'user_management')
BEGIN
    CREATE DATABASE user_management;
END;

USE user_management;

-- Create users table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
BEGIN
    CREATE TABLE users (
        id INT PRIMARY KEY IDENTITY(1,1),
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        password TEXT NOT NULL,
        role VARCHAR(50) DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
END;

-- Create stored procedure for inserting/updating users
DROP PROCEDURE IF EXISTS sp_insert_user;
GO

CREATE PROCEDURE sp_insert_user
    @p_email VARCHAR(255),
    @p_name VARCHAR(255),
    @p_password TEXT,
    @p_role VARCHAR(50)
AS
BEGIN
    MERGE INTO users AS target
    USING (SELECT @p_email AS email) AS source
    ON target.email = source.email
    WHEN MATCHED THEN
        UPDATE SET name = @p_name, password = @p_password, role = @p_role, updated_at = CURRENT_TIMESTAMP
    WHEN NOT MATCHED THEN
        INSERT (email, name, password, role)
        VALUES (@p_email, @p_name, @p_password, @p_role);
END;

-- Display success message
SELECT 'Database and tables created successfully!' AS Status;
