-- MySQL database initialization script for test case management application
-- This script creates the database, user, and sets up proper permissions

-- Create database with UTF8MB4 charset and unicode collation
CREATE DATABASE IF NOT EXISTS testcase_management 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create application user for database operations
CREATE USER IF NOT EXISTS 'testcase_user'@'%' IDENTIFIED BY 'hXLujfuQ';
CREATE USER IF NOT EXISTS 'testcase_user'@'localhost' IDENTIFIED BY 'hXLujfuQ';

-- Grant necessary privileges for application operations
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
    ON testcase_management.* 
    TO 'testcase_user'@'%';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
    ON testcase_management.* 
    TO 'testcase_user'@'localhost';

-- Additional privileges for Django migrations and admin operations
GRANT REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES 
    ON testcase_management.* 
    TO 'testcase_user'@'%';

GRANT REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES 
    ON testcase_management.* 
    TO 'testcase_user'@'localhost';

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;

-- Use the created database
USE testcase_management;

-- Set session variables for proper charset handling
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection = utf8mb4;
