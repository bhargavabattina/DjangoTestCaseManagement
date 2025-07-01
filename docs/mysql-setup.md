# MySQL Setup Guide for Test Case Management Application

This guide provides comprehensive instructions for setting up MySQL database for the Django-based test case management application.

## Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher (recommended)
- Docker and Docker Compose (for containerized deployment)
- Git (for version control)

## MySQL Installation

### Ubuntu/Debian

```bash
# Update package index
sudo apt update

# Install MySQL server
sudo apt install mysql-server

# Secure MySQL installation
sudo mysql_secure_installation

# Start and enable MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql
```

### CentOS/RHEL/Rocky Linux

```bash
# Install MySQL repository
sudo dnf install mysql-server

# Start and enable MySQL service
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Get temporary root password
sudo grep 'temporary password' /var/log/mysqld.log

# Secure MySQL installation
sudo mysql_secure_installation
```

### macOS

```bash
# Using Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Secure installation
mysql_secure_installation
```

### Windows

1. Download MySQL installer from [MySQL official website](https://dev.mysql.com/downloads/installer/)
2. Run the installer and follow the setup wizard
3. Choose "Server only" or "Full" installation
4. Configure MySQL server with root password
5. Start MySQL service from Windows Services

## Database Setup

### 1. Create Database and User

Connect to MySQL as root user:

```bash
mysql -u root -p
```

Execute the following SQL commands:

```sql
-- Create database
CREATE DATABASE testcase_management 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create application user
CREATE USER 'testcase_user'@'localhost' IDENTIFIED BY 'your_secure_password';
CREATE USER 'testcase_user'@'%' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
    ON testcase_management.* 
    TO 'testcase_user'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
    ON testcase_management.* 
    TO 'testcase_user'@'%';

-- Additional privileges for Django
GRANT REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES 
    ON testcase_management.* 
    TO 'testcase_user'@'localhost';

GRANT REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES 
    ON testcase_management.* 
    TO 'testcase_user'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

### 2. Using Initialization Script

Alternatively, you can use the provided initialization script:

```bash
# Run the initialization script
mysql -u root -p < scripts/init_mysql.sql
```

## Django Configuration

### 1. Environment Variables Setup

Create or update your `.env` file in the project root:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# MySQL Database Configuration
DB_NAME=testcase_management
DB_USER=testcase_user
DB_PASSWORD=your_secure_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Database Connection Settings
DB_CONN_MAX_AGE=600
DB_CHARSET=utf8mb4
DB_COLLATION=utf8mb4_unicode_ci
DB_TIMEOUT=20
```

### 2. Install Python Dependencies

```bash
# Install MySQL client library
pip install mysqlclient

# Or install all requirements
pip install -r requirements.txt
```

### 3. Database Migrations

Run Django migrations to create database tables:

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

## Docker Deployment

### 1. Using Docker Compose

The project includes a complete Docker setup. To deploy using Docker:

```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
docker-compose logs -f mysql

# Stop services
docker-compose down
```

### 2. Docker Environment Variables

The `docker-compose.yml` file includes pre-configured environment variables. You can override them by creating a `.env` file or modifying the compose file.

### 3. Database Initialization in Docker

The MySQL container will automatically run initialization scripts from the `scripts/` directory on first startup.

## Production Considerations

### 1. Security Settings

```env
# Production environment variables
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. MySQL Configuration for Production

Update MySQL configuration (`/etc/mysql/mysql.conf.d/mysqld.cnf`):

```ini
[mysqld]
# Performance settings
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
max_connections = 200

# Security settings
bind-address = 127.0.0.1
skip-networking = false

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

### 3. Database Backup

```bash
# Create backup
mysqldump -u root -p testcase_management > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
mysql -u root -p testcase_management < backup_file.sql
```

### 4. Performance Optimization

- Enable MySQL query cache
- Configure appropriate buffer sizes
- Set up database indexing
- Monitor slow queries
- Use connection pooling

## Troubleshooting

### Common Issues

#### 1. Connection Refused Error

**Problem**: `Can't connect to MySQL server on 'localhost'`

**Solutions**:
- Check if MySQL service is running: `sudo systemctl status mysql`
- Start MySQL service: `sudo systemctl start mysql`
- Verify MySQL is listening on correct port: `netstat -tlnp | grep 3306`
- Check firewall settings

#### 2. Authentication Plugin Error

**Problem**: `Authentication plugin 'caching_sha2_password' cannot be loaded`

**Solution**:
```sql
ALTER USER 'testcase_user'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';
FLUSH PRIVILEGES;
```

#### 3. Permission Denied

**Problem**: `Access denied for user 'testcase_user'@'localhost'`

**Solutions**:
- Verify user exists: `SELECT User, Host FROM mysql.user;`
- Check user privileges: `SHOW GRANTS FOR 'testcase_user'@'localhost';`
- Recreate user with proper privileges

#### 4. Character Set Issues

**Problem**: Unicode characters not displaying correctly

**Solutions**:
- Ensure database uses utf8mb4 charset
- Update Django settings to use utf8mb4
- Check MySQL configuration for character set settings

#### 5. Migration Errors

**Problem**: Django migrations failing

**Solutions**:
```bash
# Reset migrations (development only)
python manage.py migrate test_cases zero
python manage.py makemigrations test_cases
python manage.py migrate

# Or delete migration files and recreate
rm test_cases/migrations/0*.py
python manage.py makemigrations test_cases
python manage.py migrate
```

### Log Files

- MySQL error log: `/var/log/mysql/error.log`
- MySQL slow query log: `/var/log/mysql/slow.log`
- Django logs: Check Django settings for logging configuration

### Performance Monitoring

```sql
-- Check MySQL status
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Questions';
SHOW STATUS LIKE 'Uptime';

-- Check slow queries
SHOW STATUS LIKE 'Slow_queries';

-- Show process list
SHOW PROCESSLIST;
```

## Testing Database Connection

### 1. Test MySQL Connection

```bash
# Test connection with mysql client
mysql -h 127.0.0.1 -P 3306 -u testcase_user -p testcase_management

# Test connection with Django
python manage.py dbshell
```

### 2. Django Database Test

```python
# Test in Django shell
python manage.py shell

# In Django shell
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT VERSION()")
print(cursor.fetchone())
```

## Monitoring and Maintenance

### 1. Regular Maintenance Tasks

```bash
# Optimize tables
mysqlcheck -u root -p --optimize testcase_management

# Check table integrity
mysqlcheck -u root -p --check testcase_management

# Analyze tables
mysqlcheck -u root -p --analyze testcase_management
```

### 2. Monitoring Queries

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- Show database size
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'testcase_management'
GROUP BY table_schema;
```

This documentation should help you successfully set up and maintain the MySQL database for your test case management application. For additional support, refer to the official MySQL and Django documentation.
