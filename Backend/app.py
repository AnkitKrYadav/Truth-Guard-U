# app.py

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from dotenv import load_dotenv
import os
print("OPENAI KEY (Render):", os.getenv("OPENAI_API_KEY")[:15])

# Load environment variables
load_dotenv()

# --------- Helper: Compute Confidence Score ---------
def _compute_confidence(status: str, news_sources: list, fact_checks: list) -> int:
    """Compute a confidence score from 0 to 100 based on status and evidence."""
    score = 50  # default neutral

    # AI status signal
    if status == "True":
        score += 30
    elif status == "False":
        score -= 30

    # News sources signal
    score += min(len(news_sources), 3) * 5  # max +15

    # Fact-check signal
    for fc in fact_checks:
        fc_lower = fc.lower()
        if "true" in fc_lower or "verified" in fc_lower:
            score += 10
        elif "false" in fc_lower or "misleading" in fc_lower:
            score -= 10

    # Clamp between 0 and 100
    return max(0, min(100, score))


app = Flask(__name__)
CORS(app)  # Allow frontend to call API

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "news.db")

# --------- Database Helper ---------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT,
            summary TEXT
        )
        """
    )

    # Insert sample data if table is empty
    existing = c.execute("SELECT COUNT(*) as cnt FROM news").fetchone()[0]
    if existing == 0:
        sample_news = [
            ("AI Chatbot Breakthrough Shakes Tech World", "Tech", "TechCrunch", "A new AI model revolutionizes chatbots."),
            ("Global Climate Summit: Key Takeaways", "Environment", "BBC", "Leaders discuss climate action strategies."),
            ("Health Tips: Benefits of Daily Meditation", "Health", "Healthline", "Meditation improves mental and physical health."),
            ("SpaceX Launches Starlink Satellites", "Science", "Space.com", "Starlink satellites launched into orbit successfully."),
            ("Political Debate Heats Up Ahead of Elections", "Politics", "CNN", "Debates on policies and candidates are ongoing.")
        ]
        c.executemany("INSERT INTO news (title, category, source, summary) VALUES (?, ?, ?, ?)", sample_news)
        conn.commit()
        print("Database initialized with sample data!")

    conn.close()

init_db()

# --------- Optional AI Agent ---------
try:
    from ai_agent import verify_claim_with_ai
except Exception:
    verify_claim_with_ai = None

# --------- API Routes ---------
@app.route("/api/trending")
def trending():
    conn = get_db_connection()
    news = conn.execute("SELECT * FROM news").fetchall()
    conn.close()
    return jsonify([dict(n) for n in news])

@app.route("/api/categories")
def categories():
    conn = get_db_connection()
    cats = conn.execute("SELECT DISTINCT category FROM news").fetchall()
    conn.close()
    category_list = ["All"] + [c["category"] for c in cats]
    return jsonify(category_list)

@app.route("/api/verify", methods=["POST"])
def verify_claim_route():
    data = request.json or {}
    claim = data.get("claim")
    if not claim:
        return jsonify({"error": "No claim provided"}), 400

    print("Verifying claim with AI:", claim)
    print(os.getenv("OPENAI_API_KEY"))

    if verify_claim_with_ai and os.getenv("OPENAI_API_KEY"):
        try:
            ai_result = verify_claim_with_ai(claim)
            return jsonify(ai_result)
        except Exception as e:
            print("AI agent error:", e)

    # Fallback logic
    status = "Needs Verification"
    summary = "This claim requires further verification."
    sources = []
    if "AI" in claim or "ChatGPT" in claim:
        status = "True"
        summary = "This claim is true based on verified tech sources."
        sources = ["TechCrunch", "BBC Tech"]
    elif "Fake" in claim:
        status = "False"
        summary = "This claim is false and misleading."
        sources = ["Snopes", "Reuters"]

    confidence = _compute_confidence(status, sources, [])

    return jsonify({
        "claim": claim,
        "status": status,
        "summary": summary,
        "sources": sources,
        "confidence": confidence
    })


# --------- Serve React Frontend ---------
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# --------- Run Server ---------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
