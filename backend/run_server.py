"""
Production-ready Flask server startup script.
Disables debug mode and reloader for stable deployment.
"""
import os
import sys

# Force production settings
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
os.environ['DEBUG'] = 'False'

print("="* 60)
print("Truth-Guard Backend Server")
print("="* 60)
print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print(f"Debug Mode: False")
print("=" * 60)

try:
    from app import app
    print("\n✅ Flask app loaded successfully")
    print(f"📡 Starting server on http://0.0.0.0:5000")
    print(f"🌐 Local access: http://localhost:5000")
    print(f"🔧 Press CTRL+C to stop\n")
    
    # Run with explicit settings to avoid reloader
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        use_reloader=False,
        threaded=True
    )
except Exception as e:
    print(f"\n❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
