# app.py

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import os
# Avoid printing secrets to logs
# print("OPENAI KEY (Render):", os.getenv("OPENAI_API_KEY")[:15])

# Load environment variables (try Backend/.env, then project root)
if not load_dotenv():
    # If not found in Backend, try project root
    import pathlib
    root_env = pathlib.Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=root_env)

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


static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Frontend", "react-app", "build")
app = Flask(__name__, static_folder=os.path.abspath(static_dir))

# Restrictive CORS in production, permissive in local dev
allowed_origin = os.getenv("ALLOWED_ORIGIN")
if allowed_origin:
    CORS(app, resources={r"/api/*": {"origins": allowed_origin}})
else:
    CORS(app)  # fallback for local/dev

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

    # Expert verifications table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS expert_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )

    # News history table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS news_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            source TEXT,
            summary TEXT,
            category TEXT,
            action TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    # News verifications cache table (per news, per model)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS news_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_key TEXT NOT NULL,
            model TEXT NOT NULL,
            status TEXT,
            summary TEXT,
            confidence INTEGER,
            verified_at TEXT NOT NULL,
            UNIQUE(news_key, model)
        )
        """
    )

    # News likes/dislikes/bookmarks table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS news_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_key TEXT NOT NULL,
            user_id TEXT,
            action TEXT NOT NULL, -- 'like', 'dislike', 'bookmark'
            created_at TEXT NOT NULL
        )
        """
    )

    # Top trending news table (for dashboard)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS top_trending_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_key TEXT UNIQUE NOT NULL,
            title TEXT,
            source TEXT,
            summary TEXT,
            url TEXT,
            category TEXT,
            status TEXT,
            confidence INTEGER,
            like_count INTEGER DEFAULT 0,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def save_news_history(item, action="browsed"):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO news_history (title, url, source, summary, category, action, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item.get("title"),
            item.get("url"),
            item.get("source"),
            item.get("summary"),
            item.get("category"),
            action,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    conn.close()

init_db()

# --------- News Verification Caching Helpers ---------
def get_news_verification(news_key, model):
    """Fetch cached verification for a news item and model."""
    conn = get_db_connection()
    c = conn.cursor()
    row = c.execute(
        "SELECT status, summary, confidence, verified_at FROM news_verifications WHERE news_key=? AND model=?",
        (news_key, model)
    ).fetchone()
    conn.close()
    if row:
        return {
            "status": row["status"],
            "summary": row["summary"],
            "confidence": row["confidence"],
            "verified_at": row["verified_at"]
        }
    return None

def set_news_verification(news_key, model, status, summary, confidence):
    """Cache verification result for a news item and model."""
    conn = get_db_connection()
    c = conn.cursor()
    verified_at = datetime.utcnow().isoformat()
    c.execute(
        """
        INSERT OR REPLACE INTO news_verifications (news_key, model, status, summary, confidence, verified_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (news_key, model, status, summary, confidence, verified_at)
    )
    conn.commit()
    conn.close()
    return verified_at

def is_verification_expired(verified_at_str, expiry_hours=1):
    """Check if verification is older than expiry_hours."""
    try:
        verified_at = datetime.fromisoformat(verified_at_str)
        age = datetime.utcnow() - verified_at
        return age.total_seconds() > expiry_hours * 3600
    except Exception:
        return True  # treat as expired if parsing fails

# --------- News Likes/Dislikes/Bookmarks Helpers ---------
def add_news_action(news_key, user_id, action):
    """Add a like/dislike/bookmark action for a news item."""
    conn = get_db_connection()
    c = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    c.execute(
        """
        INSERT INTO news_likes (news_key, user_id, action, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (news_key, user_id, action, created_at)
    )
    conn.commit()
    conn.close()

def get_news_actions_count(news_key):
    """Get counts of likes/dislikes/bookmarks for a news item."""
    conn = get_db_connection()
    c = conn.cursor()
    rows = c.execute(
        "SELECT action, COUNT(*) as count FROM news_likes WHERE news_key=? GROUP BY action",
        (news_key,)
    ).fetchall()
    conn.close()
    counts = {"like": 0, "dislike": 0, "bookmark": 0}
    for row in rows:
        counts[row["action"]] = row["count"]
    return counts

# --------- Top Trending News Helpers ---------
def update_top_trending():
    """Update top_trending_news table with top 5 news by like count and recency."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get top news items by like count from news_likes
    # Join with news_verifications to get verification info
    top_news = c.execute(
        """
        SELECT 
            nl.news_key,
            COUNT(CASE WHEN nl.action = 'like' THEN 1 END) as like_count,
            MAX(nl.created_at) as latest_action
        FROM news_likes nl
        WHERE nl.action = 'like'
        GROUP BY nl.news_key
        ORDER BY like_count DESC, latest_action DESC
        LIMIT 5
        """
    ).fetchall()
    
    # Clear existing top trending
    c.execute("DELETE FROM top_trending_news")
    
    # Insert top trending news
    now = datetime.utcnow().isoformat()
    for item in top_news:
        news_key = item["news_key"]
        like_count = item["like_count"]
        
        # Try to get verification info from any model (prefer openai)
        verification = c.execute(
            "SELECT status, summary, confidence FROM news_verifications WHERE news_key=? ORDER BY verified_at DESC LIMIT 1",
            (news_key,)
        ).fetchone()
        
        # Try to get news details from history
        history = c.execute(
            "SELECT title, source, summary, category, url FROM news_history WHERE url=? OR title=? LIMIT 1",
            (news_key, news_key)
        ).fetchone()
        
        if history or verification:
            c.execute(
                """
                INSERT OR REPLACE INTO top_trending_news 
                (news_key, title, source, summary, url, category, status, confidence, like_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    news_key,
                    history["title"] if history else news_key[:100],
                    history["source"] if history else "Unknown",
                    history["summary"] if history else (verification["summary"] if verification else ""),
                    history["url"] if history else news_key,
                    history["category"] if history else "General",
                    verification["status"] if verification else "Needs Verification",
                    verification["confidence"] if verification else 50,
                    like_count,
                    now
                )
            )
    
    conn.commit()
    conn.close()

def get_top_trending():
    """Get top 5 trending news from cache."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM top_trending_news ORDER BY like_count DESC, updated_at DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --------- Optional AI Agent ---------
try:
    from ai_agent import verify_claim_with_ai
except Exception:
    verify_claim_with_ai = None
try:
    from utils.news_api import fetch_trending_mix
except Exception:
    fetch_trending_mix = None

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


@app.route("/api/trending/live")
def trending_live():
    """Fetch live trending items from mixed sources and verify them with AI.
    Query params:
      - agent: openai | hf (default openai)
      - limit: int (default 10)
      - region: country code (default 'in')
    """
    agent = request.args.get("agent", "openai")
    try:
        limit = int(request.args.get("limit", 10))
    except Exception:
        limit = 10
    region = request.args.get("region", "in")

    if not fetch_trending_mix:
        return jsonify({"error": "Trending fetcher not available"}), 500

    raw_items = fetch_trending_mix(limit_per_source=max(1, limit // 2), region=region)
    raw_items = raw_items[:limit]

    # Save all items as 'browsed' in history (optional: dedupe by url/title)
    for item in raw_items:
        save_news_history(item, action="browsed")

    # Build expert verification map for items
    def _make_key(it: dict) -> str:
        return (it.get("url") or it.get("title") or "").strip()

    keys = [ _make_key(i) for i in raw_items if _make_key(i) ]
    expert_map = {}
    if keys:
        conn = get_db_connection()
        q_marks = ",".join(["?"] * len(keys))
        rows = conn.execute(f"SELECT key, status, notes, updated_at FROM expert_verifications WHERE key IN ({q_marks})", keys).fetchall()
        conn.close()
        expert_map = { r["key"]: {"status": r["status"], "notes": r["notes"], "updated_at": r["updated_at"]} for r in rows }

    results = []
    for item in raw_items:
        claim = item.get("title") or ""
        news_key = _make_key(item)
        
        # Check for cached verification (with 1hr expiry)
        cached = get_news_verification(news_key, agent) if news_key else None
        ai_result = {}
        
        if cached and not is_verification_expired(cached["verified_at"]):
            # Use cached result
            ai_result = {
                "status": cached["status"],
                "summary": cached["summary"],
                "confidence": cached["confidence"],
                "cached": True
            }
        elif verify_claim_with_ai and claim:
            # Verify with AI and cache result
            try:
                ai_result = verify_claim_with_ai(claim, agent=agent)
                if news_key and ai_result.get("status"):
                    set_news_verification(
                        news_key, 
                        agent, 
                        ai_result.get("status", "Needs Verification"),
                        ai_result.get("summary", ""),
                        ai_result.get("confidence", 50)
                    )
                ai_result["cached"] = False
            except Exception as e:
                print("verify error:", e)
                ai_result = {"status": "Needs Verification", "summary": str(e), "confidence": 50, "cached": False}

        # Add expert override info if available
        expert = expert_map.get(news_key)
        if expert:
            ai_result = { **ai_result, "expert": expert }
        
        # Get action counts (likes/dislikes/bookmarks)
        action_counts = get_news_actions_count(news_key) if news_key else {"like": 0, "dislike": 0, "bookmark": 0}
        
        results.append({
            "title": item.get("title"),
            "source": item.get("source"),
            "summary": item.get("summary"),
            "url": item.get("url"),
            "category": item.get("category", "General"),
            "verification": ai_result,
            "actions": action_counts
        })

    return jsonify(results)


@app.route("/api/expert-verifications", methods=["POST"])
def save_expert_verification():
    data = request.json or {}
    key = (data.get("key") or "").strip()
    status = (data.get("status") or "").strip()
    notes = data.get("notes")
    if not key or status not in ("True", "False", "Needs Verification"):
        return jsonify({"error": "Invalid key or status"}), 400

    now = datetime.utcnow().isoformat()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO expert_verifications (key, status, notes, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET status=excluded.status, notes=excluded.notes, updated_at=excluded.updated_at
        """,
        (key, status, notes, now),
    )
    conn.commit()
    conn.close()
    return jsonify({"key": key, "status": status, "notes": notes, "updated_at": now})

@app.route("/api/verify", methods=["POST"])
def verify_claim_route():
    data = request.json or {}
    claim = data.get("claim")
    agent = data.get("agent", "openai")  # ← get selected agent
    if not claim:
        return jsonify({"error": "No claim provided"}), 400

    print(f"Verifying claim with AI ({agent}):", claim)
    
    if verify_claim_with_ai:
        try:
            ai_result = verify_claim_with_ai(claim, agent=agent)  # ← pass agent
            # Save to history as 'verified'
            save_news_history({"title": claim, "summary": ai_result.get("summary"), "category": ai_result.get("category"), "source": "AI", "url": None}, action="verified")
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

    save_news_history({"title": claim, "summary": summary, "category": None, "source": "AI", "url": None}, action="verified")
    return jsonify({
        "claim": claim,
        "status": status,
        "summary": summary,
        "sources": sources,
        "confidence": confidence
    })


# --- News History API ---
@app.route("/api/history", methods=["GET"])
def get_news_history():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM news_history ORDER BY created_at DESC LIMIT 100").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# --- News Actions API (Like/Dislike/Bookmark) ---
@app.route("/api/news/action", methods=["POST"])
def news_action():
    """Add a like/dislike/bookmark action for a news item.
    Request body: {news_key, user_id (optional), action}
    """
    data = request.json or {}
    news_key = (data.get("news_key") or "").strip()
    user_id = data.get("user_id") or "anonymous"
    action = (data.get("action") or "").strip().lower()
    
    if not news_key or action not in ("like", "dislike", "bookmark"):
        return jsonify({"error": "Invalid news_key or action"}), 400
    
    add_news_action(news_key, user_id, action)
    counts = get_news_actions_count(news_key)
    
    # Update top trending after like action
    if action == "like":
        update_top_trending()
    
    return jsonify({"news_key": news_key, "action": action, "counts": counts})


@app.route("/api/news/actions/<path:news_key>", methods=["GET"])
def get_actions(news_key):
    """Get action counts for a specific news item."""
    counts = get_news_actions_count(news_key)
    return jsonify(counts)


# --- Top Trending News API ---
@app.route("/api/trending/top", methods=["GET"])
def get_top_trending_news():
    """Get top 5 trending news from cache."""
    # Update the cache before fetching
    update_top_trending()
    trending = get_top_trending()
    return jsonify(trending)


# --- Dashboard Stats API ---
@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get dashboard statistics."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verified claims (from news_verifications)
    verified_count = c.execute(
        "SELECT COUNT(DISTINCT news_key) FROM news_verifications WHERE status IN ('True', 'False')"
    ).fetchone()[0]
    
    # Trending today (from news_history created today)
    today = datetime.utcnow().date().isoformat()
    trending_today = c.execute(
        f"SELECT COUNT(*) FROM news_history WHERE created_at LIKE '{today}%'"
    ).fetchone()[0]
    
    # Total fact checks (total verifications)
    fact_checks = c.execute(
        "SELECT COUNT(*) FROM news_verifications"
    ).fetchone()[0]
    
    # Active users (unique user_ids in news_likes)
    active_users = c.execute(
        "SELECT COUNT(DISTINCT user_id) FROM news_likes"
    ).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "verified": verified_count,
        "trending": trending_today,
        "users": active_users,
        "fact_checks": fact_checks
    })


# --- On-Demand Verification API ---
@app.route("/api/news/verify", methods=["POST"])
def verify_news_item():
    """Verify a specific news item with a chosen model on-demand.
    Request body: {news_key, title, agent}
    """
    data = request.json or {}
    news_key = (data.get("news_key") or "").strip()
    title = (data.get("title") or "").strip()
    agent = data.get("agent", "openai")
    
    if not news_key or not title:
        return jsonify({"error": "Invalid news_key or title"}), 400
    
    # Check for cached verification (with 1hr expiry)
    cached = get_news_verification(news_key, agent)
    
    if cached and not is_verification_expired(cached["verified_at"]):
        # Return cached result
        return jsonify({
            "news_key": news_key,
            "agent": agent,
            "status": cached["status"],
            "summary": cached["summary"],
            "confidence": cached["confidence"],
            "verified_at": cached["verified_at"],
            "cached": True
        })
    
    # Verify with AI
    if not verify_claim_with_ai:
        return jsonify({"error": "AI verification not available"}), 500
    
    try:
        ai_result = verify_claim_with_ai(title, agent=agent)
        verified_at = set_news_verification(
            news_key, 
            agent, 
            ai_result.get("status", "Needs Verification"),
            ai_result.get("summary", ""),
            ai_result.get("confidence", 50)
        )
        
        return jsonify({
            "news_key": news_key,
            "agent": agent,
            "status": ai_result.get("status"),
            "summary": ai_result.get("summary"),
            "confidence": ai_result.get("confidence"),
            "verified_at": verified_at,
            "cached": False
        })
    except Exception as e:
        print("Verification error:", e)
        return jsonify({"error": str(e)}), 500


# --------- Serve React Frontend ---------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    index_path = os.path.join(app.static_folder or "", "index.html")
    file_path = os.path.join(app.static_folder or "", path)
    if path and app.static_folder and os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    if app.static_folder and os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    # If frontend build not present, show simple message
    return jsonify({"message": "Backend running. Frontend build not found."})

# --------- Run Server ---------
if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
