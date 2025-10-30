# TruthGuard Security & Data Protection Guide

## 🔒 Security Implementation Overview

### 1. **Password Security**
- **Bcrypt hashing**: Industry-standard password hashing with salt
- **No plaintext storage**: Passwords are never stored in readable form
- **Fallback mechanism**: SHA-256 with salt if bcrypt unavailable

### 2. **Input Sanitization**
All user inputs are sanitized to prevent:
- **XSS (Cross-Site Scripting)**: HTML/JavaScript injection
- **SQL Injection**: Malicious database queries
- **Command Injection**: System command execution

### 3. **Database Security**

#### SQLite Best Practices
```python
# Parameterized queries (prevents SQL injection)
cursor.execute("SELECT * FROM users WHERE username=?", (username,))

# Enable security features
PRAGMA secure_delete = ON    # Overwrite deleted data
PRAGMA auto_vacuum = FULL     # Prevent data remnants
PRAGMA foreign_keys = ON      # Enforce referential integrity
```

#### Database Encryption (Optional)
- Field-level encryption for sensitive data (email, personal info)
- Uses Fernet symmetric encryption (cryptography library)
- Encryption key stored securely outside database

#### Automated Backups
```python
from utils.db_security import DatabaseBackup

backup = DatabaseBackup('database/news.db')
backup.create_backup()  # Creates timestamped backup
backup.cleanup_old_backups(keep_count=10)  # Retain last 10
```

### 4. **Rate Limiting**
Prevents abuse and DoS attacks:
```python
@rate_limit(max_requests=100, window_seconds=60)
def api_endpoint():
    # Limits to 100 requests per minute per IP
```

### 5. **Authentication & Authorization**
- **JWT tokens**: Secure session management
- **Role-based access**: User, Expert, Admin roles
- **Token expiration**: Automatic logout after 24 hours
- **Refresh tokens**: Optional for long sessions

### 6. **Security Headers**
Protects against common attacks:
```
X-Content-Type-Options: nosniff        # Prevent MIME sniffing
X-Frame-Options: DENY                  # Prevent clickjacking
X-XSS-Protection: 1; mode=block        # XSS filter
Strict-Transport-Security              # Force HTTPS
```

### 7. **CSRF Protection**
- CSRF tokens for state-changing operations
- Validation before processing sensitive actions

### 8. **Audit Logging**
Track all database operations:
```json
{
  "timestamp": "2025-10-30T10:30:00",
  "action": "DELETE",
  "user": "admin@example.com",
  "table": "users",
  "details": {"user_id": "123"}
}
```

---

## 🛡️ Data Protection Measures

### Personal Data Handling

#### Data Minimization
- Only collect necessary information
- No unnecessary tracking or profiling
- Anonymous usage where possible

#### Data Encryption
**In Transit:**
- HTTPS/TLS for all API communications
- Secure WebSocket connections (if used)

**At Rest:**
- Encrypted sensitive fields (optional)
- Secure file permissions (600 for sensitive files)
- Database stored outside web root

#### Data Retention
```python
# Automatic cleanup of old data
DELETE FROM news_history WHERE created_at < date('now', '-90 days');
DELETE FROM news_likes WHERE created_at < date('now', '-365 days');
```

### User Privacy

#### GDPR/Privacy Compliance
1. **Right to Access**: API endpoint to export user data
2. **Right to Deletion**: Complete user data removal
3. **Right to Rectification**: Update personal information
4. **Data Portability**: JSON export of user data

#### Anonymous Usage
- Guest browsing without account
- IP addresses not permanently stored
- Analytics aggregated and anonymized

---

## 🔧 Implementation Guide

### Step 1: Install Security Packages
```bash
cd Backend
pip install bcrypt cryptography PyJWT
```

### Step 2: Enable Security Features in App
```python
from utils.security import (
    hash_password, verify_password,
    sanitize_string, rate_limit,
    add_security_headers
)
from utils.db_security import (
    get_secure_connection,
    DatabaseBackup,
    audit_logger
)

# Use secure database connections
conn = get_secure_connection('database/news.db')

# Hash passwords before storing
hashed = hash_password(user_password)

# Sanitize all inputs
safe_username = sanitize_username(request.form['username'])

# Apply rate limiting
@app.route("/api/verify")
@rate_limit(max_requests=50, window_seconds=60)
def verify():
    pass

# Add security headers
@app.after_request
def after_request(response):
    return add_security_headers(response)
```

### Step 3: Setup Automated Backups
```python
# In app.py or background job
from utils.db_security import DatabaseBackup
import schedule

backup = DatabaseBackup('database/news.db')

# Daily backups
schedule.every().day.at("02:00").do(backup.create_backup)
schedule.every().week.do(lambda: backup.cleanup_old_backups(keep_count=30))
```

### Step 4: Enable Audit Logging
```python
from utils.db_security import audit_logger

# Log sensitive operations
@app.route("/api/admin/delete-user", methods=["POST"])
def delete_user():
    user_id = request.json['user_id']
    
    # Perform deletion
    # ...
    
    # Log the action
    audit_logger.log(
        action="DELETE_USER",
        user=request.user['username'],
        table="users",
        details={"user_id": user_id}
    )
```

---

## 🚨 Security Checklist

### Production Deployment

- [ ] Enable HTTPS/TLS (use Let's Encrypt, Cloudflare, or Render SSL)
- [ ] Set strong `SECRET_KEY` in environment variables
- [ ] Disable Flask debug mode (`DEBUG=False`)
- [ ] Use environment variables for all secrets (`.env` file)
- [ ] Set secure session cookie flags:
  ```python
  app.config['SESSION_COOKIE_SECURE'] = True
  app.config['SESSION_COOKIE_HTTPONLY'] = True
  app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
  ```
- [ ] Configure CORS properly (not `*` for production)
- [ ] Enable rate limiting on all public endpoints
- [ ] Set up automated database backups
- [ ] Configure audit logging
- [ ] Review and minimize permissions
- [ ] Set up monitoring and alerts
- [ ] Use Web Application Firewall (WAF) if available

### Database Security

- [ ] Store database outside web root
- [ ] Set file permissions: `chmod 600 news.db`
- [ ] Enable WAL mode for concurrent access
- [ ] Regular backups (daily minimum)
- [ ] Test restore procedure
- [ ] Encrypt sensitive fields
- [ ] Use parameterized queries everywhere
- [ ] No SQL in user inputs
- [ ] Limit database user permissions

### API Security

- [ ] Validate all inputs
- [ ] Sanitize outputs (prevent XSS)
- [ ] Rate limit all endpoints
- [ ] Require authentication for sensitive operations
- [ ] Use CSRF tokens for state changes
- [ ] Log authentication failures
- [ ] Implement request timeout
- [ ] Validate content types
- [ ] Limit request body size

---

## 📊 Monitoring & Incident Response

### Log Monitoring
```python
# Check audit logs for suspicious activity
from utils.db_security import audit_logger

recent_logs = audit_logger.get_recent_logs(count=1000)
failed_logins = [log for log in recent_logs if log['action'] == 'LOGIN_FAILED']
```

### Security Alerts
Set up alerts for:
- Repeated failed login attempts
- Unusual API usage patterns
- Database errors or crashes
- Backup failures
- Rate limit violations

### Incident Response Plan
1. **Detect**: Monitor logs and metrics
2. **Contain**: Block malicious IPs, disable compromised accounts
3. **Investigate**: Review audit logs, check data integrity
4. **Recover**: Restore from backup if needed
5. **Post-Incident**: Update security measures, document lessons

---

## 🔐 Environment Variables (Production)

```bash
# .env file (never commit to git!)
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://...  # or sqlite path
JWT_SECRET_KEY=<another-strong-key>
ENCRYPTION_KEY=<fernet-key>

# API Keys (never expose!)
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
NEWS_API_KEY=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# Security settings
SESSION_COOKIE_SECURE=True
RATE_LIMIT_ENABLED=True
BACKUP_ENABLED=True
AUDIT_LOG_ENABLED=True
```

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [SQLite Security](https://www.sqlite.org/security.html)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [cryptography Library](https://cryptography.io/)

---

## 🆘 Support

For security concerns or to report vulnerabilities:
- Email: security@truthguard.app (if available)
- Create a private security advisory on GitHub
- Never post security issues publicly

**Remember**: Security is an ongoing process, not a one-time setup. Regular audits and updates are essential!
