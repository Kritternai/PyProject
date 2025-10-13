#!/usr/bin/env python3
"""
Comprehensive troubleshooting for Google OAuth database connection error
"""
import sys, os, sqlite3, json
sys.path.append('.')

def check_environment():
    print('=== ENVIRONMENT CHECK ===')
    print('Python version:', sys.version)
    print('Current working directory:', os.getcwd())
    print('PYTHONPATH:', os.environ.get('PYTHONPATH', 'Not set'))
    
    # Check virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print('✅ Virtual environment: Active')
    else:
        print('⚠️ Virtual environment: Not detected')

def check_dependencies():
    print('\n=== DEPENDENCIES CHECK ===')
    required_packages = [
        'flask', 'sqlalchemy', 'google-auth', 'google-auth-oauthlib'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f'✅ {package}: Available')
        except ImportError:
            print(f'❌ {package}: Missing')

def check_configuration():
    print('\n=== CONFIGURATION CHECK ===')
    
    # Check .env file
    env_file = '.env'
    if os.path.exists(env_file):
        print('✅ .env file: Found')
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GOOGLE_CLIENT_ID' in content:
                print('✅ GOOGLE_CLIENT_ID: Configured')
            else:
                print('❌ GOOGLE_CLIENT_ID: Missing')
    else:
        print('❌ .env file: Not found')
    
    # Check client_secrets.json
    secrets_file = 'client_secrets.json'
    if os.path.exists(secrets_file):
        print('✅ client_secrets.json: Found')
        try:
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
                if 'web' in secrets and 'client_id' in secrets['web']:
                    print('✅ Google OAuth config: Valid')
                else:
                    print('❌ Google OAuth config: Invalid format')
        except Exception as e:
            print(f'❌ Google OAuth config: Error reading - {e}')
    else:
        print('❌ client_secrets.json: Not found')

def check_database_file():
    print('\n=== DATABASE FILE CHECK ===')
    
    db_path = 'instance/site.db'
    if os.path.exists(db_path):
        print('✅ Database file: Found')
        
        # Check file permissions
        readable = os.access(db_path, os.R_OK)
        writable = os.access(db_path, os.W_OK)
        print(f'File permissions - Read: {readable}, Write: {writable}')
        
        # Check file size
        size = os.path.getsize(db_path)
        print(f'File size: {size} bytes')
        
        # Test direct SQLite connection
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f'✅ Direct SQLite connection: Success ({len(tables)} tables)')
            
            # Test user table specifically
            cursor.execute("SELECT COUNT(*) FROM user;")
            user_count = cursor.fetchone()[0]
            print(f'✅ User table: {user_count} users')
            
            conn.close()
        except Exception as e:
            print(f'❌ Direct SQLite connection: Failed - {e}')
    else:
        print('❌ Database file: Not found')
        
        # Check instance directory
        if os.path.exists('instance'):
            print('✅ Instance directory: Found')
        else:
            print('❌ Instance directory: Not found')

def check_flask_app():
    print('\n=== FLASK APP CHECK ===')
    
    try:
        from app import create_app
        app = create_app()
        print('✅ Flask app creation: Success')
        
        # Check configuration
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f'App DB URI: {db_uri}')
        
        engine_options = app.config.get('SQLALCHEMY_ENGINE_OPTIONS')
        print(f'Engine options configured: {bool(engine_options)}')
        
        # Test app context
        with app.app_context():
            from app import db
            print('✅ Database object: Imported')
            
            # Test connection
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(db.text('SELECT 1'))
                    print('✅ SQLAlchemy connection: Success')
            except Exception as e:
                print(f'❌ SQLAlchemy connection: Failed - {e}')
                return False
                
            # Test UserModel
            try:
                from app.models.user import UserModel
                count = UserModel.query.count()
                print(f'✅ UserModel query: Success ({count} users)')
                return True
            except Exception as e:
                print(f'❌ UserModel query: Failed - {e}')
                return False
                
    except Exception as e:
        print(f'❌ Flask app creation: Failed - {e}')
        import traceback
        traceback.print_exc()
        return False

def check_google_oauth_flow():
    print('\n=== GOOGLE OAUTH FLOW CHECK ===')
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app import db
            from app.models.user import UserModel
            import uuid
            
            # Simulate the exact operations from Google OAuth callback
            test_email = "troubleshoot@test.com"
            
            print(f'Testing OAuth flow with: {test_email}')
            
            # Step 1: Health check
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text('SELECT 1'))
                print('✅ Health check: Passed')
            except Exception as e:
                print(f'❌ Health check: Failed - {e}')
                return False
            
            # Step 2: User query
            try:
                user = UserModel.query.filter_by(email=test_email).first()
                print(f'✅ User query: {"Found" if user else "Not found"}')
            except Exception as e:
                print(f'❌ User query: Failed - {e}')
                return False
            
            # Step 3: User creation (if needed)
            if not user:
                try:
                    user = UserModel(
                        id=str(uuid.uuid4()),
                        username="troubleshoot",
                        email=test_email,
                        password_hash="oauth_google",
                        first_name="Test",
                        email_verified=True
                    )
                    db.session.add(user)
                    db.session.commit()
                    print('✅ User creation: Success')
                    
                    # Clean up
                    db.session.delete(user)
                    db.session.commit()
                    print('✅ Cleanup: Success')
                    
                except Exception as e:
                    print(f'❌ User creation: Failed - {e}')
                    try:
                        db.session.rollback()
                    except:
                        pass
                    return False
            
            return True
            
    except Exception as e:
        print(f'❌ OAuth flow test: Failed - {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    print('🔍 GOOGLE OAUTH DATABASE CONNECTION TROUBLESHOOT')
    print('=' * 60)
    
    check_environment()
    check_dependencies()
    check_configuration() 
    check_database_file()
    flask_ok = check_flask_app()
    
    if flask_ok:
        oauth_ok = check_google_oauth_flow()
        
        print('\n' + '=' * 60)
        if oauth_ok:
            print('🎉 DIAGNOSIS: All tests passed!')
            print('The database connection should work in Google OAuth.')
            print('If you still see errors, they might be:')
            print('- Race conditions in concurrent requests')
            print('- Session state issues during OAuth redirect')
            print('- Temporary database locks')
        else:
            print('❌ DIAGNOSIS: OAuth flow simulation failed')
            print('Check the error messages above for specific issues.')
    else:
        print('\n' + '=' * 60)
        print('❌ DIAGNOSIS: Basic Flask app database connection failed')
        print('Fix the database connection issues before testing OAuth.')
    
    print('\n📋 NEXT STEPS:')
    print('1. Fix any ❌ issues found above')
    print('2. Check Flask server logs when OAuth error occurs')
    print('3. Consider using PostgreSQL for production')
    print('4. Test OAuth flow in browser and check console/network tabs')

if __name__ == "__main__":
    main()