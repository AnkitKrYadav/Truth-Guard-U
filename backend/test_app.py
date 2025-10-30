"""Simple test to check if Flask basics work"""
from flask import Flask, jsonify
import sys

print("Starting Flask test app...")
sys.stdout.flush()

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/")
def home():
    return jsonify({"message": "Test server running"})

if __name__ == "__main__":
    print("About to call app.run()...")
    sys.stdout.flush()
    try:
        app.run(debug=False, host="0.0.0.0", port=5001)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
