"""Simple script to start the Flask server without debug mode."""
import os
os.environ['FLASK_DEBUG'] = '0'
os.environ['DEBUG'] = 'False'

print("Starting Flask server...")
import app

if hasattr(app, 'app'):
    print("Flask app found, starting server on http://0.0.0.0:5000")
    app.app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)
else:
    print("ERROR: Flask app not found")
