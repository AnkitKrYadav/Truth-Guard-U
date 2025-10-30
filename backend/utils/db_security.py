"""
Database security utilities for TruthGuard
- Encrypted database connections
- Backup and restore
- Query parameterization helpers
- Data encryption at rest
"""

import sqlite3
import os
import shutil
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

# Encryption (optional, requires cryptography package)
try:
    from cryptography.fernet import Fernet
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


# ============ Database Encryption ============
class DatabaseEncryption:
    """Handle encryption for sensitive database fields."""
    
    def __init__(self, key: Optional[bytes] = None):
        if not ENCRYPTION_AVAILABLE:
            self.cipher = None
            return
        
        if key is None:
            # Generate or load encryption key
            key_file = os.path.join(os.path.dirname(__file__), '..', '.db_key')
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Secure the key file (Unix-like systems)
                try:
                    os.chmod(key_file, 0o600)
                except Exception:
                    pass
        
        self.cipher = Fernet(key) if ENCRYPTION_AVAILABLE else None
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self.cipher:
            return data  # No encryption available
        
        try:
            encrypted = self.cipher.encrypt(data.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception:
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not self.cipher:
            return encrypted_data
        
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception:
            return encrypted_data


# Global encryption instance
db_encryption = DatabaseEncryption()


# ============ Secure Database Connection ============
def get_secure_connection(db_path: str, read_only: bool = False) -> sqlite3.Connection:
    """Get a secure database connection with best practices."""
    # Use URI mode for better security options
    uri = f"file:{db_path}?mode={'ro' if read_only else 'rwc'}"
    
    conn = sqlite3.connect(uri, uri=True, timeout=30.0)
    conn.row_factory = sqlite3.Row
    
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Security pragmas
    conn.execute("PRAGMA secure_delete = ON")  # Overwrite deleted data
    conn.execute("PRAGMA auto_vacuum = FULL")  # Prevent data leakage
    
    # Performance pragmas
    conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
    
    return conn


# ============ Parameterized Query Helpers ============
class SafeQuery:
    """Helper for building safe parameterized queries."""
    
    @staticmethod
    def select(table: str, columns: List[str], where_clause: str = "", 
               params: tuple = (), limit: int = 100) -> str:
        """Build safe SELECT query with parameterization."""
        # Validate table and column names (whitelist approach)
        safe_table = SafeQuery._validate_identifier(table)
        safe_columns = [SafeQuery._validate_identifier(col) for col in columns]
        
        query = f"SELECT {', '.join(safe_columns)} FROM {safe_table}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        query += f" LIMIT {int(limit)}"
        
        return query
    
    @staticmethod
    def insert(table: str, data: Dict[str, Any]) -> tuple:
        """Build safe INSERT query with parameterization."""
        safe_table = SafeQuery._validate_identifier(table)
        columns = [SafeQuery._validate_identifier(col) for col in data.keys()]
        placeholders = ', '.join(['?' for _ in columns])
        
        query = f"INSERT INTO {safe_table} ({', '.join(columns)}) VALUES ({placeholders})"
        params = tuple(data.values())
        
        return query, params
    
    @staticmethod
    def update(table: str, data: Dict[str, Any], where_clause: str, 
               where_params: tuple = ()) -> tuple:
        """Build safe UPDATE query with parameterization."""
        safe_table = SafeQuery._validate_identifier(table)
        columns = [SafeQuery._validate_identifier(col) for col in data.keys()]
        set_clause = ', '.join([f"{col} = ?" for col in columns])
        
        query = f"UPDATE {safe_table} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + where_params
        
        return query, params
    
    @staticmethod
    def _validate_identifier(identifier: str) -> str:
        """Validate SQL identifier (table/column name) to prevent injection."""
        # Only allow alphanumeric and underscore
        if not identifier.replace('_', '').isalnum():
            raise ValueError(f"Invalid identifier: {identifier}")
        return identifier


# ============ Database Backup ============
class DatabaseBackup:
    """Handle database backups and restoration."""
    
    def __init__(self, db_path: str, backup_dir: str = None):
        self.db_path = db_path
        self.backup_dir = backup_dir or os.path.join(
            os.path.dirname(db_path), 'backups'
        )
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, prefix: str = "backup") -> str:
        """Create a timestamped backup of the database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{prefix}_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Use SQLite backup API for consistency
            source = sqlite3.connect(self.db_path)
            dest = sqlite3.connect(backup_path)
            
            with dest:
                source.backup(dest)
            
            source.close()
            dest.close()
            
            # Also create metadata
            metadata = {
                "timestamp": timestamp,
                "source": self.db_path,
                "size_bytes": os.path.getsize(backup_path)
            }
            
            metadata_path = backup_path + ".meta.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return backup_path
        
        except Exception as e:
            raise Exception(f"Backup failed: {e}")
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup."""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        try:
            # Create a backup of current DB before restoring
            self.create_backup(prefix="pre_restore")
            
            # Restore from backup
            shutil.copy2(backup_path, self.db_path)
            return True
        
        except Exception as e:
            raise Exception(f"Restore failed: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for filename in sorted(os.listdir(self.backup_dir), reverse=True):
            if filename.endswith('.db'):
                backup_path = os.path.join(self.backup_dir, filename)
                metadata_path = backup_path + ".meta.json"
                
                info = {
                    "filename": filename,
                    "path": backup_path,
                    "size_bytes": os.path.getsize(backup_path),
                    "created": datetime.fromtimestamp(
                        os.path.getctime(backup_path)
                    ).isoformat()
                }
                
                # Load metadata if available
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                            info.update(metadata)
                    except Exception:
                        pass
                
                backups.append(info)
        
        return backups
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backups, keeping only the most recent ones."""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return
        
        # Remove oldest backups
        for backup in backups[keep_count:]:
            try:
                os.remove(backup['path'])
                # Remove metadata file
                metadata_path = backup['path'] + ".meta.json"
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
            except Exception:
                pass


# ============ Audit Logging ============
class AuditLogger:
    """Log database operations for security audit trail."""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file or os.path.join(
            os.path.dirname(__file__), '..', 'logs', 'audit.log'
        )
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log(self, action: str, user: str, table: str, 
            details: Dict[str, Any] = None):
        """Log a database operation."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "table": table,
            "details": details or {}
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception:
            pass  # Don't let logging errors break the app
    
    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit log entries."""
        logs = []
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-count:]:
                    try:
                        logs.append(json.loads(line))
                    except Exception:
                        pass
        except FileNotFoundError:
            pass
        
        return logs


# Global audit logger
audit_logger = AuditLogger()
