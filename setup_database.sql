-- Create database
CREATE DATABASE IF NOT EXISTS user_management;

USE user_management;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create stored procedure for inserting/updating users
DELIMITER $$

DROP PROCEDURE IF EXISTS sp_insert_user$$

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
END$$

DELIMITER ;

-- Display success message
SELECT 'Database and tables created successfully!' AS Status;
