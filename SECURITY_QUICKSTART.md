# Security & Database Protection - Quick Start

## 🎯 What We've Implemented

### 1. **Password Security Module** (`Backend/utils/security.py`)
```python
from utils.security import hash_password, verify_password

# Hash password before storing
hashed = hash_password("user_password")

# Verify login
if verify_password("user_password", hashed):
    # Login successful
```

### 2. **Database Security Module** (`Backend/utils/db_security.py`)
```python
from utils.db_security import DatabaseBackup, get_secure_connection, audit_logger

# Secure database connection with encryption & foreign keys
conn = get_secure_connection('database/news.db')

# Create backup
backup = DatabaseBackup('database/news.db')
backup.create_backup()

# Log security events
audit_logger.log("DELETE_USER", user="admin", table="users", details={...})
```

### 3. **Input Sanitization**
```python
from utils.security import sanitize_string, sanitize_email, sanitize_username

# Prevent XSS & injection attacks
safe_username = sanitize_username(user_input)
safe_email = sanitize_email(email_input)
safe_text = sanitize_string(content)
```

### 4. **Rate Limiting**
```python
from utils.security import rate_limit

@app.route("/api/verify")
@rate_limit(max_requests=50, window_seconds=60)  # 50 requests per minute
def verify_news():
    # Your code here
```

## 🚀 Quick Setup

### Step 1: Install Security Packages
```bash
cd Backend
pip install bcrypt cryptography PyJWT
```

### Step 2: Run Security Setup Script
```bash
python setup_security.py
```
This will:
- Generate secure secret keys
- Create `.env` file with configuration
- Set up backup and log directories
- Configure secure file permissions

### Step 3: Add Your API Keys
Edit `Backend/.env`:
```bash
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
# ... etc
```

## 🛡️ Key Security Features

| Feature | Purpose | Status |
|---------|---------|--------|
| **Bcrypt Password Hashing** | Secure password storage | ✅ Ready |
| **Input Sanitization** | Prevent XSS/injection | ✅ Ready |
| **SQL Parameterization** | Prevent SQL injection | ✅ Ready |
| **Rate Limiting** | Prevent DoS/abuse | ✅ Ready |
| **Database Encryption** | Encrypt sensitive fields | ✅ Optional |
| **Automated Backups** | Data recovery | ✅ Ready |
| **Audit Logging** | Track all operations | ✅ Ready |
| **JWT Auth** | Secure sessions | ✅ Ready |
| **HTTPS/TLS** | Encrypted communication | ⚠️ Production only |
| **Security Headers** | XSS/clickjacking protection | ✅ Ready |

## 📊 Database Protection

### Automatic Backups
```python
# In app.py or cron job
from utils.db_security import DatabaseBackup

backup = DatabaseBackup('database/news.db')

# Create daily backup
backup.create_backup(prefix="daily")

# Keep only last 30 backups
backup.cleanup_old_backups(keep_count=30)
```

### Secure Database Queries
```python
# ✅ GOOD: Parameterized (prevents injection)
cursor.execute("SELECT * FROM users WHERE username=?", (username,))

# ❌ BAD: String concatenation (vulnerable!)
cursor.execute(f"SELECT * FROM users WHERE username='{username}'")
```

### Database Encryption (Optional)
```python
from utils.db_security import db_encryption

# Encrypt sensitive data before storing
encrypted_email = db_encryption.encrypt(user_email)

# Decrypt when needed
original_email = db_encryption.decrypt(encrypted_email)
```

## 🔐 Production Checklist

Before deploying to production:

```bash
# Backend/.env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<generate-strong-64-char-key>
SESSION_COOKIE_SECURE=True  # Requires HTTPS
RATE_LIMIT_ENABLED=True
BACKUP_ENABLED=True
```

**Must-do:**
1. ✅ Enable HTTPS (Render provides free SSL)
2. ✅ Set strong SECRET_KEY (64+ random characters)
3. ✅ Disable debug mode
4. ✅ Configure CORS properly (not `*`)
5. ✅ Set up automated backups
6. ✅ Enable audit logging
7. ✅ Review database permissions
8. ✅ Never commit .env file to git

## 🚨 Emergency Response

### If Database Gets Corrupted
```python
from utils.db_security import DatabaseBackup

backup = DatabaseBackup('database/news.db')

# List available backups
backups = backup.list_backups()

# Restore from backup
backup.restore_backup(backups[0]['path'])
```

### If Suspicious Activity Detected
```python
from utils.db_security import audit_logger

# Check recent activity
logs = audit_logger.get_recent_logs(count=1000)

# Look for patterns
failed_logins = [log for log in logs if 'FAILED' in log['action']]
```

## 📚 Documentation

- **Full Security Guide**: See `SECURITY.md`
- **Code Examples**: Check `Backend/utils/security.py`
- **Database Tools**: Check `Backend/utils/db_security.py`

## 💡 Tips

### For Development
- Keep DEBUG=True for easier debugging
- Use localhost without HTTPS (it's okay)
- Test rate limiting with small limits
- Practice backup/restore procedures

### For Production
- Always use HTTPS (mandatory)
- Set DEBUG=False (critical!)
- Use strong, random SECRET_KEY
- Enable all security headers
- Set up monitoring and alerts
- Schedule regular backups (daily minimum)
- Review audit logs weekly

## 🆘 Common Issues

### "ModuleNotFoundError: No module named 'bcrypt'"
```bash
cd Backend
pip install bcrypt cryptography PyJWT
```

### "Database is locked"
- Enable WAL mode (already done in secure connection)
- Check for long-running transactions
- Ensure proper connection closing

### "Permission denied" on database file
```bash
chmod 600 Backend/database/news.db
chmod 700 Backend/database/backups
```

## 📞 Need Help?

- Check `SECURITY.md` for detailed information
- Review code examples in `utils/` directory
- Test in development first
- Use audit logs to track issues

---

**Remember**: Security is a continuous process. Review and update regularly! 🔒
