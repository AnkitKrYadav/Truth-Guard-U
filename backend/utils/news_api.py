import os
import requests
import logging
from typing import List, Dict
import sqlite3
import praw

from .env_loader import load_env

load_env()

logger = logging.getLogger("news_api")


def _categorize(title: str) -> str:
    t = (title or "").lower()
    if any(k in t for k in ["election", "government", "president", "minister", "parliament", "bjp", "congress", "policy", "vote", "politic"]):
        return "Politics"
    if any(k in t for k in ["ai", "tech", "software", "microsoft", "google", "apple", "openai", "startup", "chip", "semiconductor", "robotics", "machine learning", "data", "cybersecurity"]):
        return "Tech"
    if any(k in t for k in ["covid", "health", "vaccine", "doctor", "hospital", "disease", "mental health", "medicine", "wellness", "fitness"]):
        return "Health"
    if any(k in t for k in ["movie", "film", "bollywood", "hollywood", "music", "celebrity", "show", "tv", "series", "actor", "actress", "award"]):
        return "Entertainment"
    if any(k in t for k in ["space", "nasa", "spacex", "science", "research", "astronomy", "physics", "biology", "chemistry"]):
        return "Science"
    if any(k in t for k in ["football", "cricket", "soccer", "tennis", "olympic", "nba", "sports", "athlete", "match", "tournament"]):
        return "Sports"
    if any(k in t for k in ["market", "stock", "economy", "business", "startup", "funding", "finance", "trade", "investment", "bank", "cryptocurrency"]):
        return "Business"
    if any(k in t for k in ["world", "global", "international", "foreign", "diplomacy", "united nations"]):
        return "World"
    if any(k in t for k in ["local", "city", "town", "district", "municipal", "community"]):
        return "Local"
    if any(k in t for k in ["crime", "police", "court", "law", "justice", "arrest", "investigation"]):
        return "Crime"
    if any(k in t for k in ["environment", "climate", "pollution", "wildlife", "nature", "sustainability", "green"]):
        return "Environment"
    if any(k in t for k in ["education", "school", "college", "university", "student", "teacher", "exam", "learning"]):
        return "Education"
    if any(k in t for k in ["lifestyle", "fashion", "beauty", "culture", "trend", "relationship", "parenting"]):
        return "Lifestyle"
    if any(k in t for k in ["travel", "tourism", "destination", "flight", "hotel", "trip"]):
        return "Travel"
    if any(k in t for k in ["food", "recipe", "restaurant", "cuisine", "cooking", "diet"]):
        return "Food"
    if any(k in t for k in ["opinion", "editorial", "column", "analysis", "review"]):
        return "Opinion"
    return "General"


def fetch_newsapi_top_headlines(country: str = "in", page_size: int = 10) -> List[Dict]:
    """Fetch top headlines from NewsAPI.org. Requires NEWS_API_KEY env var."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        logger.warning("NEWS_API_KEY not set; skipping NewsAPI fetch")
        return []
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": country, "pageSize": page_size, "apiKey": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            logger.warning("NewsAPI non-200 status %s: %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        if not articles:
            logger.info("NewsAPI returned 0 articles for country=%s", country)
        items = []
        for a in articles:
            title = a.get("title") or ""
            items.append({
                "title": title,
                "source": (a.get("source") or {}).get("name"),
                "summary": a.get("description") or "",
                "url": a.get("url"),
                "category": _categorize(title)
            })
        return items
    except Exception as e:
        logger.exception("NewsAPI fetch failed: %s", e)
        return []


def fetch_reddit_trending(subreddit: str = "news", limit: int = 10) -> List[Dict]:
    """Fetch trending posts from Reddit public JSON (no auth)."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    params = {"limit": limit}
    headers = {"User-Agent": "TruthGuard/1.0"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            logger.warning("Reddit non-200 status %s: %s", resp.status_code, resp.text[:200])
        resp.raise_for_status()
        data = resp.json()
        children = data.get("data", {}).get("children", [])
        if not children:
            logger.info("Reddit returned 0 posts for subreddit=%s", subreddit)
        items = []
        for c in children:
            d = c.get("data", {})
            title = d.get("title") or ""
            items.append({
                "title": title,
                "source": "Reddit",
                "summary": d.get("selftext") or "",
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "category": _categorize(title)
            })
        return items
    except Exception as e:
        logger.exception("Reddit fetch failed: %s", e)
        return []



# --- Social Media Stubs (mock data, real API integration requires setup) ---
def fetch_reddit_trending_oauth(subreddit: str = "news", limit: int = 10) -> List[Dict]:
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "TruthGuard/1.0")
    if not client_id or not client_secret:
        logger.warning("Reddit API credentials not set; skipping Reddit fetch")
        return []
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        items = []
        for submission in reddit.subreddit(subreddit).hot(limit=limit):
            items.append({
                "title": submission.title,
                "source": "Reddit",
                "summary": submission.selftext[:200] if submission.selftext else "",
                "url": f"https://reddit.com{submission.permalink}",
                "category": _categorize(submission.title)
            })
        return items
    except Exception as e:
        logger.exception("Reddit OAuth fetch failed: %s", e)
        return []
def fetch_twitter_trending(region: str = "in", limit: int = 10) -> List[Dict]:
    # TODO: Integrate Twitter/X API (requires dev account)
    # For now, return mock data
    return [
        {
            "title": f"Trending on Twitter in {region} #{i+1}",
            "source": "Twitter",
            "summary": f"Sample trending tweet {i+1} in {region}.",
            "url": None,
            "category": "General"
        } for i in range(limit)
    ]

def fetch_facebook_trending(region: str = "in", limit: int = 10) -> List[Dict]:
    # TODO: Integrate Facebook Graph API
    return [
        {
            "title": f"Facebook hot topic {i+1} in {region}",
            "source": "Facebook",
            "summary": f"Sample Facebook post {i+1} in {region}.",
            "url": None,
            "category": "General"
        } for i in range(limit)
    ]

def fetch_instagram_trending(region: str = "in", limit: int = 10) -> List[Dict]:
    # TODO: Integrate Instagram API
    return [
        {
            "title": f"Instagram trend {i+1} in {region}",
            "source": "Instagram",
            "summary": f"Sample Instagram post {i+1} in {region}.",
            "url": None,
            "category": "General"
        } for i in range(limit)
    ]

def fetch_trending_mix(limit_per_source: int = 10, region: str = "in") -> List[Dict]:
    """Fetch trending news from APIs, save to DB, and return deduped list."""
    items = []
    items += fetch_newsapi_top_headlines(country=region, page_size=limit_per_source)
    items += fetch_reddit_trending_oauth(subreddit="news", limit=limit_per_source)
    # TODO: Add Twitter fetcher here if keys are set
    # items += fetch_twitter_trending_oauth(region=region, limit=limit_per_source)

    # Save all fetched news to DB (deduped by title/url)
    db_path = os.path.join(os.path.dirname(__file__), "..", "database", "news.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for it in items:
        title = (it.get("title") or "").strip()
        url = (it.get("url") or "").strip()
        category = it.get("category") or "General"
        source = it.get("source") or "Unknown"
        summary = it.get("summary") or ""
        region_val = region or "all"
        # Deduplicate by title+source
        if not title:
            continue
        try:
            c.execute(
                "INSERT OR IGNORE INTO news (title, category, source, summary, region, url) VALUES (?, ?, ?, ?, ?, ?)",
                (title, category, source, summary, region_val, url)
            )
        except Exception as e:
            logger.warning(f"DB insert failed for news: {title[:40]}... {e}")
    conn.commit()
    # Query back trending news from DB
    rows = c.execute(
        "SELECT title, category, source, summary, region, url FROM news WHERE region=? ORDER BY id DESC LIMIT ?",
        (region_val, limit_per_source * 3)
    ).fetchall()
    conn.close()
    unique = []
    seen = set()
    for r in rows:
        t = (r[0] if isinstance(r, tuple) else r["title"]).strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            unique.append({
                "title": r[0] if isinstance(r, tuple) else r["title"],
                "category": r[1] if isinstance(r, tuple) else r["category"],
                "source": r[2] if isinstance(r, tuple) else r["source"],
                "summary": r[3] if isinstance(r, tuple) else r["summary"],
                "region": r[4] if isinstance(r, tuple) else r["region"],
                "url": r[5] if isinstance(r, tuple) else r["url"]
            })
    # Fallback: if DB is empty, provide sample trending items
    if not unique:
        logger.warning("fetch_trending_mix returned 0 items from DB; using fallback")
        unique = [
            {
                "title": "Breaking: Global climate summit reaches historic agreement",
                "source": "Sample News",
                "summary": "World leaders agree on new carbon reduction targets at COP30.",
                "url": None,
                "category": "Environment"
            },
            {
                "title": "Tech giants announce joint AI safety initiative",
                "source": "Sample Tech",
                "summary": "Major AI companies pledge to share safety research and best practices.",
                "url": None,
                "category": "Tech"
            },
            {
                "title": "Local health officials warn of flu season peak",
                "source": "Sample Health",
                "summary": "Residents urged to get vaccinated as flu cases rise.",
                "url": None,
                "category": "Health"
            },
            {
                "title": "New economic data shows job growth accelerating",
                "source": "Sample Business",
                "summary": "Latest employment report exceeds economist expectations.",
                "url": None,
                "category": "Business"
            },
            {
                "title": "Sports: Championship finals set for this weekend",
                "source": "Sample Sports",
                "summary": "Top teams prepare for decisive matches across multiple leagues.",
                "url": None,
                "category": "Sports"
            },
        ]
    return unique
