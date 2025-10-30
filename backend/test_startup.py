"""Test script to identify backend startup issues."""

print("=" * 60)
print("TESTING BACKEND STARTUP")
print("=" * 60)

# Test 1: Environment loading
print("\n[1] Testing environment loading...")
try:
    from utils.env_loader import load_env
    load_env()
    print("✅ Environment loaded")
except Exception as e:
    print(f"❌ Environment loading failed: {e}")

# Test 2: Database connection
print("\n[2] Testing database connection...")
try:
    import sqlite3
    conn = sqlite3.connect("database/news.db")
    conn.close()
    print("✅ Database connected")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Test 3: Flask import
print("\n[3] Testing Flask import...")
try:
    from flask import Flask
    print("✅ Flask imported")
except Exception as e:
    print(f"❌ Flask import failed: {e}")

# Test 4: AI agent import
print("\n[4] Testing AI agent import...")
try:
    from ai_agent import verify_claim_with_ai
    print("✅ AI agent imported")
except Exception as e:
    print(f"❌ AI agent import failed: {e}")

# Test 5: News API import
print("\n[5] Testing News API import...")
try:
    from utils.news_api import fetch_trending_mix
    print("✅ News API imported")
except Exception as e:
    print(f"❌ News API import failed: {e}")

# Test 6: Try importing full app
print("\n[6] Testing full app import...")
try:
    import app
    print("✅ App module imported")
except Exception as e:
    print(f"❌ App import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
