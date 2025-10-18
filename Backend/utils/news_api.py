import os
import requests
from typing import List, Dict


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
        return []
    url = "https://newsapi.org/v2/top-headlines"
    params = {"country": country, "pageSize": page_size, "apiKey": api_key}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
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
    except Exception:
        return []


def fetch_reddit_trending(subreddit: str = "news", limit: int = 10) -> List[Dict]:
    """Fetch trending posts from Reddit public JSON (no auth)."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    params = {"limit": limit}
    headers = {"User-Agent": "TruthGuardBot/1.0 (by u/yourbot)"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        children = data.get("data", {}).get("children", [])
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
    except Exception:
        return []



# --- Social Media Stubs (mock data, real API integration requires setup) ---
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
    """Combine multiple sources into a single list. Region is a country code (e.g. 'in', 'us')."""
    items = []
    items += fetch_newsapi_top_headlines(country=region, page_size=limit_per_source)
    items += fetch_reddit_trending(limit=limit_per_source)
    # items += fetch_facebook_trending(region=region, limit=limit_per_source)  # removed mock Facebook
    # items += fetch_instagram_trending(region=region, limit=limit_per_source)  # removed mock Instagram
    # Explicitly drop any Twitter/Facebook/Instagram-sourced mock entries
    items = [it for it in items if (it.get("source") or "").lower() not in ("twitter", "facebook", "instagram")]
    # de-duplicate by title
    seen = set()
    unique = []
    for it in items:
        t = (it.get("title") or "").strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            unique.append(it)
    return unique
