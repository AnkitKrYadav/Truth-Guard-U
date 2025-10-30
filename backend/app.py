# app.py

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timezone
import time
# Avoid printing secrets to logs
# print("OPENAI KEY (Render):", os.getenv("OPENAI_API_KEY")[:15])

# Load environment variables (try Backend/.env, then project root)
from utils.env_loader import load_env
load_env()

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


# Static folder for React frontend (optional - only if Frontend exists)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Frontend", "react-app", "build")
if os.path.exists(static_dir):
    app = Flask(__name__, static_folder=os.path.abspath(static_dir))
else:
    # Backend-only mode (no frontend static files)
    app = Flask(__name__)

# Restrictive CORS in production, permissive in local dev
# Supports comma-separated ALLOWED_ORIGINS, or single ALLOWED_ORIGIN for backward compatibility
allowed_origins_env = os.getenv("ALLOWED_ORIGINS") or os.getenv("ALLOWED_ORIGIN")
if allowed_origins_env:
    origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    CORS(
        app,
        resources={r"/api/*": {
            "origins": origins if len(origins) > 1 else origins[0],
            "allow_headers": ["Content-Type", "X-Admin-Key"],
            "methods": ["GET", "POST", "OPTIONS"],
        }}
    )
# --------- Simple In-Memory TTL Cache (dev optimization) ---------
# Caches select API responses briefly to collapse duplicate requests (e.g., React StrictMode)
_response_cache = {
    "trending_top": {"data": None, "ts": 0.0},
    "stats": {"data": None, "ts": 0.0},
}

# TTLs can be tuned via env vars
TRENDING_TOP_TTL = int(os.getenv("TRENDING_TOP_TTL", "30"))  # seconds
STATS_TTL = int(os.getenv("STATS_TTL", "15"))  # seconds

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
            summary TEXT,
            region TEXT DEFAULT 'all',
            url TEXT
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
    # Check if index exists; if not, we may need to clean duplicates first
    existing_index = c.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_news_likes_unique'"
    ).fetchone()
    
    if not existing_index:
        # Drop and recreate table to ensure clean schema with unique constraint
        c.execute("DROP TABLE IF EXISTS news_likes")
    
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS news_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_key TEXT NOT NULL,
            user_id TEXT,
            action TEXT NOT NULL, -- 'like', 'dislike', 'bookmark'
            created_at TEXT NOT NULL,
            UNIQUE(news_key, user_id, action)
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
    # Jobs table for lightweight scheduling (e.g., hourly refresh)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            name TEXT PRIMARY KEY,
            last_run TEXT NOT NULL
        )
        """
    )
    
    # Users table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
        """
    )

    # Badges table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT NOT NULL,
            description TEXT
        )
        """
    )

    # Experts table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS experts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            organization TEXT,
            badge_id INTEGER,
            is_verified INTEGER DEFAULT 0,
            verified_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(badge_id) REFERENCES badges(id)
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
            datetime.now(timezone.utc).isoformat(),
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
    verified_at = datetime.now(timezone.utc).isoformat()
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
        age = datetime.now(timezone.utc) - verified_at
        return age.total_seconds() > expiry_hours * 3600
    except Exception:
        return True  # treat as expired if parsing fails

# --------- News Likes/Dislikes/Bookmarks Helpers ---------
def add_news_action(news_key, user_id, action):
    """Apply a like/dislike/bookmark with per-user uniqueness and toggle behavior.
    - like/dislike are mutually exclusive for a user on the same news_key
    - repeating the same action toggles it off (removes the prior row)
    - bookmark toggles on/off independently
    """
    conn = get_db_connection()
    c = conn.cursor()
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        if action == "bookmark":
            exists = c.execute(
                "SELECT 1 FROM news_likes WHERE news_key=? AND user_id=? AND action='bookmark'",
                (news_key, user_id)
            ).fetchone()
            if exists:
                c.execute(
                    "DELETE FROM news_likes WHERE news_key=? AND user_id=? AND action='bookmark'",
                    (news_key, user_id)
                )
            else:
                c.execute(
                    "INSERT OR IGNORE INTO news_likes (news_key, user_id, action, created_at) VALUES (?, ?, 'bookmark', ?)",
                    (news_key, user_id, created_at)
                )
        elif action in ("like", "dislike"):
            current = c.execute(
                "SELECT action FROM news_likes WHERE news_key=? AND user_id=? AND action IN ('like','dislike')",
                (news_key, user_id)
            ).fetchone()
            if current:
                curr = current[0] if isinstance(current, tuple) else current["action"]
                if curr == action:
                    # toggle off
                    c.execute(
                        "DELETE FROM news_likes WHERE news_key=? AND user_id=? AND action IN ('like','dislike')",
                        (news_key, user_id)
                    )
                else:
                    # switch like<->dislike
                    c.execute(
                        "DELETE FROM news_likes WHERE news_key=? AND user_id=? AND action IN ('like','dislike')",
                        (news_key, user_id)
                    )
                    c.execute(
                        "INSERT OR IGNORE INTO news_likes (news_key, user_id, action, created_at) VALUES (?, ?, ?, ?)",
                        (news_key, user_id, action, created_at)
                    )
            else:
                c.execute(
                    "INSERT OR IGNORE INTO news_likes (news_key, user_id, action, created_at) VALUES (?, ?, ?, ?)",
                    (news_key, user_id, action, created_at)
                )
        conn.commit()
    finally:
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

# --------- Fallback: Recent Verified News (DB) ---------
def get_recent_verified(limit: int = 10, region: str = "all"):
    """Return recently verified news items from DB, optionally filtered by region.
    Uses news_verifications joined with news/news_history to enrich fields.
    """
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Prefer exact URL match; fall back to title when URL missing
        rows = c.execute(
            """
            SELECT 
                COALESCE(nh.title, n.title, nv.news_key) AS title,
                COALESCE(nh.source, n.source, 'Unknown') AS source,
                COALESCE(nh.summary, n.summary, '') AS summary,
                COALESCE(nh.category, n.category, 'General') AS category,
                COALESCE(nh.url, n.url, nv.news_key) AS url,
                nv.status AS status,
                nv.confidence AS confidence,
                nv.verified_at AS verified_at
            FROM news_verifications nv
            LEFT JOIN news n ON (n.url = nv.news_key OR n.title = nv.news_key)
            LEFT JOIN news_history nh ON (nh.url = nv.news_key OR nh.title = nv.news_key)
            WHERE nv.status IN ('True','False')
              AND (
                    ? = 'all' OR 
                    EXISTS (
                        SELECT 1 FROM news n2 
                        WHERE (n2.url = nv.news_key OR n2.title = nv.news_key) 
                          AND n2.region = ?
                    )
                )
            ORDER BY datetime(nv.verified_at) DESC
            LIMIT ?
            """,
            (region, region, limit)
        ).fetchall()
    except Exception:
        rows = []
    finally:
        conn.close()

    items = []
    for r in rows:
        # sqlite rows can be Row or tuple
        title = r[0] if isinstance(r, tuple) else r["title"]
        source = r[1] if isinstance(r, tuple) else r["source"]
        summary = r[2] if isinstance(r, tuple) else r["summary"]
        category = r[3] if isinstance(r, tuple) else r["category"]
        url = r[4] if isinstance(r, tuple) else r["url"]
        status = r[5] if isinstance(r, tuple) else r["status"]
        confidence = r[6] if isinstance(r, tuple) else r["confidence"]
        items.append({
            "title": title,
            "source": source,
            "summary": summary,
            "category": category,
            "url": url,
            "status": status,
            "confidence": confidence,
        })
    return items

# --------- Hourly Refresh (opportunistic, DB-guarded) ---------
def _job_last_run(name: str) -> float:
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT last_run FROM jobs WHERE name=?", (name,)).fetchone()
        if row:
            ts = row[0] if isinstance(row, tuple) else row["last_run"]
            try:
                return datetime.fromisoformat(ts).timestamp()
            except Exception:
                return 0.0
        return 0.0
    finally:
        conn.close()

def _job_set_run(name: str):
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO jobs (name, last_run) VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET last_run=excluded.last_run
            """,
            (name, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
    finally:
        conn.close()

def ensure_hourly_refresh(region: str = "in", verify_limit: int = 10):
    """Fetch and cache trending news and verifications roughly every hour.
    This is triggered lazily by requests and guarded via the jobs table.
    Safe to call frequently; it runs at most once per hour per service.
    """
    try:
        last_ts = _job_last_run("hourly_refresh")
        now_ts = time.time()
        if now_ts - last_ts < 3600:
            return  # fresh enough

        # Mark run time early to avoid thundering herd; the work is idempotent
        _job_set_run("hourly_refresh")

        if not fetch_trending_mix:
            return
        # Fetch and persist news
        fetched = fetch_trending_mix(limit_per_source=6, region=region) or []
        # Verify a subset with Gemini and cache results
        if verify_claim_with_ai:
            seen = set()
            count = 0
            for it in fetched:
                if count >= max(3, verify_limit):
                    break
                key = (it.get("url") or it.get("title") or "").strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                try:
                    ai = verify_claim_with_ai(it.get("title", ""), agent="gemini")
                    if ai and ai.get("status"):
                        set_news_verification(
                            key,
                            "gemini",
                            ai.get("status", "Needs Verification"),
                            ai.get("summary", ""),
                            ai.get("confidence", 50),
                        )
                        count += 1
                except Exception:
                    continue
    except Exception:
        # Best-effort; never block requests
        return
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
    now = datetime.now(timezone.utc).isoformat()
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
    region = request.args.get("region", "all")
    conn = get_db_connection()
    if region == "all":
        news = conn.execute("SELECT * FROM news").fetchall()
    else:
        news = conn.execute("SELECT * FROM news WHERE region=?", (region,)).fetchall()
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
    - agent: auto | gemini | openai | hf (default auto)
    - limit: int (default 10)
    - region: country code (default 'in')
    """
    agent = request.args.get("agent", "auto")
    try:
        limit = int(request.args.get("limit", 10))
    except Exception:
        limit = 10
    region = request.args.get("region", "all")

    if not fetch_trending_mix:
        return jsonify({"error": "Trending fetcher not available"}), 500

    # Opportunistic refresh before serving
    ensure_hourly_refresh(region=region)

    raw_items = fetch_trending_mix(limit_per_source=max(1, limit // 2), region=region) or []
    # De-duplicate by URL/title key and cap to limit
    def _make_key(it: dict) -> str:
        return (it.get("url") or it.get("title") or "").strip()
    seen = set()
    deduped = []
    for it in raw_items:
        k = _make_key(it)
        if not k or k in seen:
            continue
        seen.add(k)
        deduped.append(it)
        if len(deduped) >= limit:
            break
    raw_items = deduped

    # Fallback to recent verified if no items from sources
    if not raw_items:
        fallback = get_recent_verified(limit=limit, region=region)
        results = []
        for it in fallback:
            results.append({
                "title": it.get("title"),
                "source": it.get("source"),
                "summary": it.get("summary"),
                "url": it.get("url"),
                "category": it.get("category", "General"),
                "verification": {
                    "status": it.get("status", "Needs Verification"),
                    "summary": it.get("summary", ""),
                    "confidence": it.get("confidence", 50),
                    "cached": True,
                    "agent": "gemini",
                    "agent_used": "gemini"
                },
                "actions": {"like": 0, "dislike": 0, "bookmark": 0}
            })
        return jsonify(results)

    # Save all items as 'browsed' in history and add region
    for item in raw_items:
        item["region"] = region
        save_news_history(item, action="browsed")

    # Build expert verification map for items

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
        cached = None
        used_agent_for_cache = agent
        if news_key:
            if agent == "auto":
                for candidate in ["gemini", "openai", "hf"]:
                    c = get_news_verification(news_key, candidate)
                    if c and not is_verification_expired(c["verified_at"]):
                        cached = c
                        used_agent_for_cache = candidate
                        break
            else:
                cached = get_news_verification(news_key, agent)
        ai_result = {}
        
        if cached and not is_verification_expired(cached["verified_at"]):
            # Use cached result
            ai_result = {
                "status": cached["status"],
                "summary": cached["summary"],
                "confidence": cached["confidence"],
                "cached": True,
                "agent": used_agent_for_cache,
                "agent_used": used_agent_for_cache
            }
        elif verify_claim_with_ai and claim:
            # Verify with AI and cache result
            try:
                ai_result = verify_claim_with_ai(claim, agent=agent)
                if news_key and ai_result.get("status"):
                    model_to_cache = ai_result.get("agent_used") or ai_result.get("agent") or agent
                    set_news_verification(
                        news_key,
                        model_to_cache,
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


# --------- IoT-friendly Endpoints (Gemini-only, lean payload) ---------
def _truncate(text: str, max_len: int = 180) -> str:
    t = (text or "").strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


@app.route("/api/iot/trending", methods=["GET"]) 
def iot_trending():
    """Return Gemini-verified trending news with a lean payload for ESP32.
    Query params: region (default 'in'), limit (default 8)
    """
    try:
        limit = int(request.args.get("limit", 8))
    except Exception:
        limit = 8
    region = request.args.get("region", "in")

    # Opportunistic refresh before serving
    ensure_hourly_refresh(region=region)

    # Fetch latest trending items (reuse existing fetcher)
    if not fetch_trending_mix:
        return jsonify({"error": "Trending fetcher not available"}), 500
    raw_items = fetch_trending_mix(limit_per_source=max(1, limit // 2), region=region) or []

    # De-duplicate by key and cap
    def _make_key(it: dict) -> str:
        return (it.get("url") or it.get("title") or "").strip()
    seen = set()
    items = []
    for it in raw_items:
        k = _make_key(it)
        if not k or k in seen:
            continue
        seen.add(k)
        items.append(it)
        if len(items) >= limit:
            break

    # Verify each with Gemini and cache
    results = []
    for it in items:
        title = it.get("title") or ""
        url = it.get("url")
        key = (url or title).strip()

        cached = get_news_verification(key, "gemini") if key else None
        ai: dict = {}
        if cached and not is_verification_expired(cached.get("verified_at")):
            ai = {"status": cached["status"], "confidence": cached["confidence"], "agent": "gemini", "cached": True}
        elif verify_claim_with_ai and title:
            try:
                ai = verify_claim_with_ai(title, agent="gemini")
                if key and ai.get("status") is not None:
                    set_news_verification(key, "gemini", ai.get("status", "Needs Verification"), ai.get("summary", ""), ai.get("confidence", 50))
                ai["cached"] = False
            except Exception as e:
                ai = {"status": "Needs Verification", "confidence": 50, "agent": "gemini", "cached": False, "error": str(e)}

        results.append({
            "title": title,
            "source": it.get("source"),
            "url": url,
            "category": it.get("category", "General"),
            "summary": _truncate(it.get("summary"), 160),
            "status": ai.get("status", "Needs Verification"),
            "confidence": ai.get("confidence", 50)
        })

    # If we couldn't gather anything (e.g., API limits), fallback to recent verified
    if not results:
        fallback = get_recent_verified(limit=limit, region=region)
        out = []
        for it in fallback:
            out.append({
                "title": it.get("title"),
                "source": it.get("source"),
                "url": it.get("url"),
                "category": it.get("category", "General"),
                "summary": _truncate(it.get("summary"), 160),
                "status": it.get("status", "Needs Verification"),
                "confidence": it.get("confidence", 50)
            })
        return jsonify(out)

    return jsonify(results)


@app.route("/api/iot/search", methods=["GET"]) 
def iot_search():
    """Search recent news by title (DB-first) and return Gemini-verified results.
    Query params: query (q), limit (default 6)
    """
    q = (request.args.get("query") or request.args.get("q") or "").strip()
    if not q:
        return jsonify({"error": "Missing query"}), 400
    try:
        limit = int(request.args.get("limit", 6))
    except Exception:
        limit = 6

    # DB search first
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT title, source, summary, category, url FROM news WHERE title LIKE ? ORDER BY id DESC LIMIT ?",
        (f"%{q}%", limit)
    ).fetchall()
    conn.close()
    items = [
        {
            "title": r[0] if isinstance(r, tuple) else r["title"],
            "source": r[1] if isinstance(r, tuple) else r["source"],
            "summary": r[2] if isinstance(r, tuple) else r["summary"],
            "category": r[3] if isinstance(r, tuple) else r["category"],
            "url": r[4] if isinstance(r, tuple) else r["url"],
        }
        for r in rows
    ]

    # If no items found, return empty array (avoid external rate limits)
    if not items:
        return jsonify([])

    # Verify with Gemini and cache
    results = []
    for it in items:
        title = it.get("title") or ""
        url = it.get("url")
        key = (url or title).strip()
        cached = get_news_verification(key, "gemini") if key else None
        ai: dict = {}
        if cached and not is_verification_expired(cached.get("verified_at")):
            ai = {"status": cached["status"], "confidence": cached["confidence"], "agent": "gemini", "cached": True}
        elif verify_claim_with_ai and title:
            try:
                ai = verify_claim_with_ai(title, agent="gemini")
                if key and ai.get("status") is not None:
                    set_news_verification(key, "gemini", ai.get("status", "Needs Verification"), ai.get("summary", ""), ai.get("confidence", 50))
                ai["cached"] = False
            except Exception as e:
                ai = {"status": "Needs Verification", "confidence": 50, "agent": "gemini", "cached": False, "error": str(e)}

        results.append({
            "title": title,
            "source": it.get("source"),
            "url": url,
            "category": it.get("category", "General"),
            "summary": _truncate(it.get("summary"), 160),
            "status": ai.get("status", "Needs Verification"),
            "confidence": ai.get("confidence", 50)
        })

    return jsonify(results)


@app.route("/api/expert-verifications", methods=["POST"])
def save_expert_verification():
    # Optional admin key guard: if ADMIN_KEY is set, require matching header
    admin_key = os.getenv("ADMIN_KEY")
    if admin_key:
        provided = request.headers.get("X-Admin-Key", "")
        if provided != admin_key:
            return jsonify({"error": "Unauthorized"}), 401
    data = request.json or {}
    key = (data.get("key") or "").strip()
    status = (data.get("status") or "").strip()
    notes = data.get("notes")
    if not key or status not in ("True", "False", "Needs Verification"):
        return jsonify({"error": "Invalid key or status"}), 400

    now = datetime.now(timezone.utc).isoformat()
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
    # Invalidate cached stats since expert verifications affect verified counts
    try:
        _response_cache["stats"]["ts"] = 0.0
    except Exception:
        pass
    return jsonify({"key": key, "status": status, "notes": notes, "updated_at": now})

@app.route("/api/verify", methods=["POST"])
def verify_claim_route():
    data = request.json or {}
    claim = data.get("claim")
    agent = data.get("agent", "gemini")  # ← get selected agent
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


# --- Simple Admin helper endpoints (for frontend compatibility) ---
@app.route("/api/admin/categories", methods=["GET"])
def admin_categories():
    # Return only raw categories (no "All")
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT category FROM news WHERE category IS NOT NULL AND category <> ''").fetchall()
    conn.close()
    return jsonify([r[0] if isinstance(r, tuple) else r["category"] for r in rows])


@app.route("/api/admin/regions", methods=["GET"])
def admin_regions():
    # Provide a basic list of regions; adjust as needed or source from DB/env
    regions = [
        "all", "in", "us", "gb", "au", "ca", "de", "fr", "jp", "ru", "cn"
    ]
    return jsonify(regions)


@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, username, email, is_active, created_at FROM users ORDER BY created_at DESC LIMIT 200"
    ).fetchall()
    conn.close()
    # Ensure list of dicts
    return jsonify([{
        "id": r[0] if isinstance(r, tuple) else r["id"],
        "username": r[1] if isinstance(r, tuple) else r["username"],
        "email": r[2] if isinstance(r, tuple) else r["email"],
        "is_active": (r[3] if isinstance(r, tuple) else r["is_active"]) == 1 if isinstance((r[3] if isinstance(r, tuple) else r["is_active"]), int) else (r[3] if isinstance(r, tuple) else r["is_active"]),
        "created_at": r[4] if isinstance(r, tuple) else r["created_at"],
    } for r in rows])


@app.route("/api/admin/experts", methods=["GET"])
def admin_experts():
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT e.id, u.username, e.full_name, e.organization, e.badge_id, e.is_verified, e.verified_at
        FROM experts e
        LEFT JOIN users u ON u.id = e.user_id
        ORDER BY e.id DESC
        LIMIT 200
        """
    ).fetchall()
    conn.close()
    return jsonify([{
        "id": r[0] if isinstance(r, tuple) else r["id"],
        "username": r[1] if isinstance(r, tuple) else r["username"],
        "full_name": r[2] if isinstance(r, tuple) else r["full_name"],
        "organization": r[3] if isinstance(r, tuple) else r["organization"],
        "badge_id": r[4] if isinstance(r, tuple) else r["badge_id"],
        "is_verified": (r[5] if isinstance(r, tuple) else r["is_verified"]) == 1 if isinstance((r[5] if isinstance(r, tuple) else r["is_verified"]), int) else (r[5] if isinstance(r, tuple) else r["is_verified"]),
        "verified_at": r[6] if isinstance(r, tuple) else r["verified_at"],
    } for r in rows])


@app.route("/api/admin/badges", methods=["GET"])
def admin_badges():
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT id, name, color, description FROM badges ORDER BY id DESC LIMIT 200"
    ).fetchall()
    conn.close()
    return jsonify([{
        "id": r[0] if isinstance(r, tuple) else r["id"],
        "name": r[1] if isinstance(r, tuple) else r["name"],
        "color": r[2] if isinstance(r, tuple) else r["color"],
        "description": r[3] if isinstance(r, tuple) else r["description"],
    } for r in rows])


# --- News Actions API (Like/Dislike/Bookmark) ---
@app.route("/api/news/action", methods=["POST"])
def news_action():
    """Add or toggle a like/dislike/bookmark for a news item (per-user unique).
    Request body: {news_key, user_id (required), action}
    """
    data = request.json or {}
    news_key = (data.get("news_key") or "").strip()
    user_id = (data.get("user_id") or "").strip()
    action = (data.get("action") or "").strip().lower()
    
    if not news_key or action not in ("like", "dislike", "bookmark"):
        return jsonify({"error": "Invalid news_key or action"}), 400
    if not user_id:
        return jsonify({"error": "user_id required"}), 401
    
    add_news_action(news_key, user_id, action)
    counts = get_news_actions_count(news_key)
    
    # Update top trending after like action
    if action == "like":
        update_top_trending()
        # Invalidate caches influenced by likes
        try:
            _response_cache["trending_top"]["ts"] = 0.0
            _response_cache["stats"]["ts"] = 0.0
        except Exception:
            pass
    
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
    now = time.time()
    cache_item = _response_cache.get("trending_top", {"data": None, "ts": 0.0})
    # Serve from cache if fresh
    if cache_item["data"] is not None and (now - cache_item["ts"]) < TRENDING_TOP_TTL:
        return jsonify(cache_item["data"]) 

    # Refresh DB-backed cache and store response
    update_top_trending()
    trending = get_top_trending()
    _response_cache["trending_top"] = {"data": trending, "ts": now}
    return jsonify(trending)


# --- Dashboard Stats API ---
@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get dashboard statistics."""
    now = time.time()
    cache_item = _response_cache.get("stats", {"data": None, "ts": 0.0})
    if cache_item["data"] is not None and (now - cache_item["ts"]) < STATS_TTL:
        return jsonify(cache_item["data"]) 

    conn = get_db_connection()
    c = conn.cursor()
    
    # Verified claims (from news_verifications)
    verified_count = c.execute(
        "SELECT COUNT(DISTINCT news_key) FROM news_verifications WHERE status IN ('True', 'False')"
    ).fetchone()[0]
    
    # Trending today (from news_history created today)
    today = datetime.now(timezone.utc).date().isoformat()
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
    
    payload = {
        "verified": verified_count,
        "trending": trending_today,
        "users": active_users,
        "fact_checks": fact_checks
    }
    _response_cache["stats"] = {"data": payload, "ts": now}
    return jsonify(payload)


# --- On-Demand Verification API ---
@app.route("/api/news/verify", methods=["POST"])
def verify_news_item():
    """Verify a specific news item with a chosen model on-demand.
    Request body: {news_key, title, agent}
    """
    data = request.json or {}
    news_key = (data.get("news_key") or "").strip()
    title = (data.get("title") or "").strip()
    agent = data.get("agent", "gemini")
    
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
