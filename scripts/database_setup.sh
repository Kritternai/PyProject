#!/bin/bash

# =============================================================================
# Smart Learning Hub - Database Setup Script
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=============================================================================${NC}"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# =============================================================================
# DATABASE SETUP
# =============================================================================
print_header "Smart Learning Hub - Database Setup"

# Check if we're in the right directory
if [ ! -f "init_database.py" ]; then
    print_error "init_database.py not found!"
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if database package exists
if [ ! -d "database" ]; then
    print_error "Database package not found!"
    print_error "Please ensure the database package is properly set up"
    exit 1
fi

# =============================================================================
# 1. CREATE NECESSARY DIRECTORIES
# =============================================================================
print_step "Creating necessary directories..."

# Create instance directory for database
mkdir -p instance
print_status "Instance directory created/verified"

# Create backup directory
mkdir -p database/backups
print_status "Backup directory created/verified"

# Create uploads directory
mkdir -p app/static/uploads
mkdir -p app/static/uploads/files
mkdir -p app/static/uploads/image
print_status "Upload directories created/verified"

# =============================================================================
# 2. DATABASE INITIALIZATION
# =============================================================================
print_step "Initializing database..."

if [ -f "instance/site.db" ]; then
    print_warning "Database file already exists"
    
    # Ask user if they want to backup and recreate
    read -p "Do you want to backup and recreate the database? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Create backup
        BACKUP_FILE="database/backups/manual_backup_$(date +%Y%m%d_%H%M%S).db"
        cp instance/site.db "$BACKUP_FILE"
        print_status "Database backed up to: $BACKUP_FILE"
        
        # Remove old database
        rm instance/site.db
        print_status "Old database removed"
        
        # Create new database
        python init_database.py
        if [ $? -eq 0 ]; then
            print_status "New database created successfully"
        else
            print_error "Failed to create new database"
            exit 1
        fi
    else
        print_status "Using existing database"
    fi
else
    print_status "Creating new database..."
    python init_database.py
    
    if [ $? -eq 0 ]; then
        print_status "Database created successfully"
    else
        print_error "Failed to create database"
        exit 1
    fi
fi

# =============================================================================
# 3. DATABASE HEALTH CHECK
# =============================================================================
print_step "Performing database health check..."

if [ -f "test_database.py" ]; then
    if python test_database.py >/dev/null 2>&1; then
        print_status "✅ Database health check passed"
    else
        print_warning "⚠️  Database health check failed"
        print_step "Running health check with verbose output..."
        python test_database.py
    fi
else
    print_warning "test_database.py not found, skipping health check"
fi

# =============================================================================
# 4. DATABASE BACKUP
# =============================================================================
print_step "Creating database backup..."

BACKUP_FILE="database/backups/setup_complete_backup_$(date +%Y%m%d_%H%M%S).db"
if cp instance/site.db "$BACKUP_FILE" 2>/dev/null; then
    print_status "Database backup created: $BACKUP_FILE"
else
    print_warning "Failed to create database backup"
fi

# =============================================================================
# 5. FINAL STATUS
# =============================================================================
print_header "Database Setup Complete"

# Show database info
if [ -f "instance/site.db" ]; then
    DB_SIZE=$(du -h instance/site.db | cut -f1)
    print_status "Database file: instance/site.db"
    print_status "Database size: $DB_SIZE"
    print_status "Database location: $(pwd)/instance/site.db"
else
    print_error "Database file not found after setup!"
    exit 1
fi

# Show backup info
BACKUP_COUNT=$(ls -1 database/backups/*.db 2>/dev/null | wc -l)
print_status "Backup files: $BACKUP_COUNT"

echo ""
print_status "🎉 Database setup completed successfully!"
print_status "You can now run: ./start_flask.sh"
echo ""

# =============================================================================
# 6. OPTIONAL: SHOW DATABASE SCHEMA
# =============================================================================
read -p "Do you want to see the database schema? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Database Schema Information:"
    echo ""
    
    if python -c "
from database import get_db_manager
manager = get_db_manager()
info = manager.get_database_info()
print(f'Tables: {info.get(\"table_count\", 0)}')
print(f'Size: {info.get(\"database_size_mb\", 0)} MB')
print(f'Health: {info.get(\"health_status\", \"unknown\")}')
if info.get('tables'):
    print('\\nTable List:')
    for table in info['tables']:
        print(f'  - {table}')
" 2>/dev/null; then
        print_status "Schema information displayed"
    else
        print_warning "Failed to display schema information"
    fi
fi

echo ""
print_status "Setup complete! 🚀"
