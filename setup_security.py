#!/usr/bin/env python3
"""
Security setup script for TruthGuard
Run this after installing requirements to configure security features.
"""

import os
import secrets
import sys

def generate_secret_key():
    """Generate a secure random secret key."""
    return secrets.token_hex(32)

def generate_encryption_key():
    """Generate Fernet encryption key."""
    try:
        from cryptography.fernet import Fernet
        return Fernet.generate_key().decode()
    except ImportError:
        print("⚠️  cryptography not installed, skipping encryption key")
        return None

def setup_env_file():
    """Create or update .env file with security keys."""
    env_path = os.path.join(os.path.dirname(__file__), 'Backend', '.env')
    env_example_path = env_path + '.example'
    
    # Check if .env already exists
    if os.path.exists(env_path):
        response = input(".env file exists. Regenerate security keys? (y/N): ")
        if response.lower() != 'y':
            print("✅ Keeping existing .env file")
            return
    
    # Generate keys
    secret_key = generate_secret_key()
    jwt_secret = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    # Create .env content
    env_content = f"""# TruthGuard Environment Configuration
# Generated: {os.popen('date').read().strip()}

# Flask Configuration
FLASK_ENV=development
SECRET_KEY={secret_key}
DEBUG=True

# Security Keys
JWT_SECRET_KEY={jwt_secret}
"""
    
    if encryption_key:
        env_content += f"ENCRYPTION_KEY={encryption_key}\n"
    
    env_content += """
# Database
DATABASE_URL=sqlite:///database/news.db

# API Keys (add your keys here)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
NEWS_API_KEY=your_newsapi_key_here

# Reddit API
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=TruthGuard/1.0

# Security Settings
RATE_LIMIT_ENABLED=True
BACKUP_ENABLED=True
AUDIT_LOG_ENABLED=True
SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
"""
    
    # Write .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    # Write example file (without secrets)
    example_content = env_content
    for key in ['SECRET_KEY', 'JWT_SECRET_KEY', 'ENCRYPTION_KEY']:
        example_content = example_content.replace(
            f"{key}=.*", f"{key}=<generate-secure-key-here>"
        )
    
    with open(env_example_path, 'w') as f:
        f.write(example_content)
    
    print(f"✅ Created {env_path}")
    print(f"✅ Created {env_example_path}")
    print("\n⚠️  IMPORTANT: Add your API keys to .env file!")

def setup_database_permissions():
    """Set secure permissions for database files."""
    db_path = os.path.join(os.path.dirname(__file__), 'Backend', 'database', 'news.db')
    
    if not os.path.exists(db_path):
        print("ℹ️  Database not found yet (will be created on first run)")
        return
    
    try:
        # Set restrictive permissions (Unix-like systems)
        os.chmod(db_path, 0o600)
        print(f"✅ Set secure permissions on {db_path}")
    except Exception as e:
        print(f"⚠️  Could not set permissions: {e}")
        print("   (This is normal on Windows)")

def create_backup_directory():
    """Create backup directory with secure permissions."""
    backup_dir = os.path.join(os.path.dirname(__file__), 'Backend', 'database', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        os.chmod(backup_dir, 0o700)
        print(f"✅ Created backup directory: {backup_dir}")
    except Exception:
        print(f"✅ Created backup directory: {backup_dir}")

def create_logs_directory():
    """Create logs directory."""
    logs_dir = os.path.join(os.path.dirname(__file__), 'Backend', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    print(f"✅ Created logs directory: {logs_dir}")

def install_security_packages():
    """Check and install security packages."""
    print("\n🔍 Checking security packages...")
    
    try:
        import bcrypt
        print("  ✅ bcrypt installed")
    except ImportError:
        print("  ❌ bcrypt not installed")
    
    try:
        import cryptography
        print("  ✅ cryptography installed")
    except ImportError:
        print("  ❌ cryptography not installed")
    
    try:
        import jwt
        print("  ✅ PyJWT installed")
    except ImportError:
        print("  ❌ PyJWT not installed")
    
    print("\n💡 To install missing packages, run:")
    print("   cd Backend && pip install -r requirements.txt")

def main():
    """Main setup routine."""
    print("=" * 60)
    print("TruthGuard Security Setup")
    print("=" * 60)
    print()
    
    try:
        # Check if we're in the right directory
        if not os.path.exists('Backend'):
            print("❌ Error: Run this script from the TruthGuard root directory")
            sys.exit(1)
        
        # Run setup steps
        install_security_packages()
        setup_env_file()
        setup_database_permissions()
        create_backup_directory()
        create_logs_directory()
        
        print("\n" + "=" * 60)
        print("✅ Security setup complete!")
        print("=" * 60)
        print("\n📋 Next steps:")
        print("1. Edit Backend/.env and add your API keys")
        print("2. Review SECURITY.md for best practices")
        print("3. Run: cd Backend && python app.py")
        print("\n⚠️  For production deployment:")
        print("   - Set FLASK_ENV=production")
        print("   - Set DEBUG=False")
        print("   - Enable HTTPS (SESSION_COOKIE_SECURE=True)")
        print("   - Set up regular database backups")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
