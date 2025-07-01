# Database Migration Guide: SQLite to MySQL

This guide provides step-by-step instructions for migrating your Django test case management application from SQLite to MySQL database.

## Overview

This migration guide covers:
- Data backup from existing SQLite database
- MySQL setup and configuration
- Django settings migration
- Data export/import using Django fixtures
- Rollback procedures
- Common troubleshooting issues

## Prerequisites

Before starting the migration, ensure you have:
- Python 3.8 or higher
- MySQL 8.0 or higher installed
- Current SQLite database with existing data
- Backup of your current project
- Required Python packages installed (`mysqlclient`, `python-dotenv`)

## Step 1: Backup Existing SQLite Data

### 1.1 Create Project Backup

```bash
# Create a complete backup of your project
cp -r /path/to/testcase_management /path/to/testcase_management_backup

# Or create a tar archive
tar -czf testcase_management_backup_$(date +%Y%m%d_%H%M%S).tar.gz testcase_management/
```

### 1.2 Export Data Using Django Fixtures

Create fixtures from your existing SQLite database:

```bash
# Export all data
python manage.py dumpdata > full_backup.json

# Export specific apps (recommended)
python manage.py dumpdata auth > auth_data.json
python manage.py dumpdata test_cases > test_cases_data.json

# Export with natural foreign keys (better for cross-database compatibility)
python manage.py dumpdata --natural-foreign --natural-primary > natural_backup.json

# Export excluding contenttypes and sessions (recommended)
python manage.py dumpdata --exclude auth.permission --exclude contenttypes --exclude sessions > clean_backup.json
```

### 1.3 Verify Backup Integrity

```bash
# Check JSON validity
python -m json.tool full_backup.json > /dev/null && echo "JSON is valid" || echo "JSON is invalid"

# Check fixture content
python manage.py shell -c "
import json
with open('full_backup.json', 'r') as f:
    data = json.load(f)
    print(f'Total records: {len(data)}')
    models = {}
    for item in data:
        model = item['model']
        models[model] = models.get(model, 0) + 1
    for model, count in models.items():
        print(f'{model}: {count} records')
"
```

## Step 2: MySQL Database Setup

### 2.1 Install MySQL Server

Follow the installation instructions in `docs/mysql-setup.md` for your operating system.

### 2.2 Create Database and User

```bash
# Connect to MySQL as root
mysql -u root -p

# Execute SQL commands
```

```sql
-- Create database
CREATE DATABASE testcase_management 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'testcase_user'@'localhost' IDENTIFIED BY 'your_secure_password';
CREATE USER 'testcase_user'@'%' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
    ON testcase_management.* 
    TO 'testcase_user'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
    ON testcase_management.* 
    TO 'testcase_user'@'%';

-- Additional Django privileges
GRANT REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES 
    ON testcase_management.* 
    TO 'testcase_user'@'localhost';

GRANT REFERENCES, CREATE TEMPORARY TABLES, LOCK TABLES 
    ON testcase_management.* 
    TO 'testcase_user'@'%';

FLUSH PRIVILEGES;
EXIT;
```

### 2.3 Test MySQL Connection

```bash
# Test connection
mysql -h 127.0.0.1 -P 3306 -u testcase_user -p testcase_management

# If successful, you should see MySQL prompt
# Type EXIT to leave
```

## Step 3: Update Django Settings

### 3.1 Install Required Dependencies

```bash
# Install MySQL client library
pip install mysqlclient python-dotenv

# Or install all requirements
pip install -r requirements.txt
```

### 3.2 Create Environment Configuration

Create or update `.env` file in project root:

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

### 3.3 Update Django Settings

Your `testcase_management/settings.py` should already be configured for MySQL. Verify the database configuration:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "testcase_management"),
        "USER": os.environ.get("DB_USER", "root"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": os.environ.get("DB_CHARSET", "utf8mb4"),
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", 600)),
    }
}
```

## Step 4: Database Migration

### 4.1 Test Database Connection

```bash
# Test Django database connection
python manage.py dbshell

# You should see MySQL prompt
# Type EXIT to leave
```

### 4.2 Run Initial Migrations

```bash
# Create migration files (if not already present)
python manage.py makemigrations

# Apply migrations to create tables
python manage.py migrate

# Verify tables were created
python manage.py dbshell -c "SHOW TABLES;"
```

### 4.3 Create Superuser

```bash
# Create a new superuser for MySQL database
python manage.py createsuperuser
```

## Step 5: Data Import

### 5.1 Import Data Using Fixtures

```bash
# Method 1: Import all data at once
python manage.py loaddata full_backup.json

# Method 2: Import specific fixtures in order
python manage.py loaddata auth_data.json
python manage.py loaddata test_cases_data.json

# Method 3: Import with natural keys (recommended)
python manage.py loaddata natural_backup.json

# Method 4: Import clean backup (recommended)
python manage.py loaddata clean_backup.json
```

### 5.2 Handle Import Errors

If you encounter errors during import:

```bash
# Import with verbosity for detailed error messages
python manage.py loaddata --verbosity=2 full_backup.json

# Skip problematic records (use with caution)
python manage.py loaddata --ignore full_backup.json

# Import specific models only
python manage.py loaddata --app test_cases test_cases_data.json
```

### 5.3 Verify Data Import

```bash
# Check data in Django shell
python manage.py shell

# In Django shell:
from test_cases.models import Project, Epic, UserStory, TestCase
from django.contrib.auth.models import User

print(f"Users: {User.objects.count()}")
print(f"Projects: {Project.objects.count()}")
print(f"Epics: {Epic.objects.count()}")
print(f"User Stories: {UserStory.objects.count()}")
print(f"Test Cases: {TestCase.objects.count()}")

# Check specific data
for project in Project.objects.all():
    print(f"Project: {project.name} - Epics: {project.epic_set.count()}")
```

## Step 6: Post-Migration Verification

### 6.1 Test Application Functionality

```bash
# Start development server
python manage.py runserver

# Test the following:
# - Login functionality
# - Dashboard access
# - CRUD operations for all entities
# - Excel import functionality
# - Data relationships and constraints
```

### 6.2 Performance Testing

```bash
# Check database performance
python manage.py shell -c "
from django.db import connection
from django.test.utils import override_settings
import time

start_time = time.time()
from test_cases.models import TestCase
test_cases = list(TestCase.objects.select_related('user_story__epic__project').all())
end_time = time.time()

print(f'Query time: {end_time - start_time:.3f} seconds')
print(f'Test cases loaded: {len(test_cases)}')
print(f'Database queries: {len(connection.queries)}')
"
```

## Step 7: Rollback Procedures

### 7.1 Emergency Rollback to SQLite

If migration fails and you need to rollback quickly:

```bash
# 1. Stop the application
# 2. Restore from backup
cp -r /path/to/testcase_management_backup/* .

# 3. Or extract from tar archive
tar -xzf testcase_management_backup_*.tar.gz

# 4. Update settings.py to use SQLite temporarily
# Comment out MySQL configuration and add:
```

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

```bash
# 5. Start application
python manage.py runserver
```

### 7.2 Partial Rollback (Keep MySQL, Restore Data)

If only data import failed:

```bash
# 1. Clear all data from MySQL
python manage.py flush --noinput

# 2. Re-run migrations
python manage.py migrate

# 3. Import from backup again
python manage.py loaddata clean_backup.json

# 4. Create superuser
python manage.py createsuperuser
```

## Step 8: Troubleshooting Common Issues

### 8.1 Connection Errors

**Error**: `Can't connect to MySQL server`

**Solutions**:
```bash
# Check MySQL service status
sudo systemctl status mysql

# Start MySQL if not running
sudo systemctl start mysql

# Check port availability
netstat -tlnp | grep 3306

# Test connection manually
mysql -h 127.0.0.1 -P 3306 -u testcase_user -p
```

### 8.2 Authentication Errors

**Error**: `Access denied for user 'testcase_user'@'localhost'`

**Solutions**:
```sql
-- Check user exists
SELECT User, Host FROM mysql.user WHERE User = 'testcase_user';

-- Check privileges
SHOW GRANTS FOR 'testcase_user'@'localhost';

-- Reset password
ALTER USER 'testcase_user'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

### 8.3 Migration Errors

**Error**: `django.db.utils.OperationalError: (1071, 'Specified key was too long')`

**Solutions**:
```python
# In settings.py, ensure proper charset:
'OPTIONS': {
    'charset': 'utf8mb4',
    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
},
```

**Error**: `django.db.utils.IntegrityError: FOREIGN KEY constraint failed`

**Solutions**:
```bash
# Import in correct order
python manage.py loaddata auth_data.json
python manage.py loaddata test_cases_data.json

# Or use natural keys
python manage.py loaddata natural_backup.json
```

### 8.4 Character Encoding Issues

**Error**: Unicode characters not displaying correctly

**Solutions**:
```sql
-- Check database charset
SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME 
FROM information_schema.SCHEMATA 
WHERE SCHEMA_NAME = 'testcase_management';

-- Fix charset if needed
ALTER DATABASE testcase_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### 8.5 Performance Issues

**Problem**: Slow query performance after migration

**Solutions**:
```sql
-- Check table statistics
ANALYZE TABLE test_cases_project;
ANALYZE TABLE test_cases_epic;
ANALYZE TABLE test_cases_userstory;
ANALYZE TABLE test_cases_testcase;

-- Check indexes
SHOW INDEX FROM test_cases_testcase;

-- Optimize tables
OPTIMIZE TABLE test_cases_project;
OPTIMIZE TABLE test_cases_epic;
OPTIMIZE TABLE test_cases_userstory;
OPTIMIZE TABLE test_cases_testcase;
```

### 8.6 Data Import Issues

**Error**: `DeserializationError: Invalid model identifier`

**Solutions**:
```bash
# Clean the fixture file
python manage.py shell -c "
import json
with open('full_backup.json', 'r') as f:
    data = json.load(f)

# Remove problematic entries
clean_data = [item for item in data if 'contenttypes' not in item['model']]

with open('clean_backup.json', 'w') as f:
    json.dump(clean_data, f, indent=2)
"

# Import cleaned data
python manage.py loaddata clean_backup.json
```

## Step 9: Final Validation Checklist

After completing the migration, verify:

- [ ] Database connection is working
- [ ] All tables are created with correct schema
- [ ] Data has been imported successfully
- [ ] Foreign key relationships are intact
- [ ] User authentication works
- [ ] All CRUD operations function correctly
- [ ] Excel import functionality works
- [ ] Application performance is acceptable
- [ ] Backup procedures are in place

## Step 10: Cleanup and Optimization

### 10.1 Remove SQLite Database

```bash
# After confirming migration success, remove SQLite files
rm db.sqlite3
rm db.sqlite3-*  # SQLite journal files if present
```

### 10.2 Update Documentation

- Update deployment documentation
- Update environment setup instructions
- Document new backup procedures
- Update development setup guide

### 10.3 Database Optimization

```sql
-- Update table statistics
ANALYZE TABLE test_cases_project, test_cases_epic, test_cases_userstory, test_cases_testcase;

-- Check for unused indexes
SELECT DISTINCT
    t.table_schema,
    t.table_name,
    t.index_name
FROM information_schema.statistics t
LEFT JOIN information_schema.key_column_usage k 
    ON t.table_schema = k.table_schema
    AND t.table_name = k.table_name
    AND t.index_name = k.constraint_name
WHERE t.table_schema = 'testcase_management'
    AND k.constraint_name IS NULL
    AND t.index_name != 'PRIMARY';
```

## Conclusion

This migration guide provides a comprehensive approach to migrating from SQLite to MySQL. Always test the migration process in a development environment before applying to production. Keep backups of your data throughout the process and be prepared to rollback if issues arise.

For additional support, refer to:
- `docs/mysql-setup.md` for detailed MySQL configuration
- Django documentation for database migrations
- MySQL documentation for performance optimization

Remember to update your deployment scripts and documentation to reflect the new database configuration.
