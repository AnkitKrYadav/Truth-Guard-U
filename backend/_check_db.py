import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "database", "news.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("=== Database Tables ===")
for t in tables:
    print(f"  - {t[0]}")

print("\n=== News Table Schema ===")
schema = c.execute("PRAGMA table_info(news)").fetchall()
for col in schema:
    print(f"  {col[1]} ({col[2]})")

print("\n=== Sample Counts ===")
for table in [t[0] for t in tables]:
    try:
        count = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")
    except Exception as e:
        print(f"  {table}: error ({e})")

conn.close()
print("\n[OK] Database check complete")
