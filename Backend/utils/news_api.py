import os
import requests
from typing import List, Dict


def _categorize(title: str) -> str:
    t = (title or "").lower()
    if any(k in t for k in ["election", "government", "president", "minister", "parliament", "bjp", "congress", "policy", "vote", "politic"]):
        return "Politics"
    if any(k in t for k in ["ai", "tech", "software", "microsoft", "google", "apple", "openai", "startup", "chip", "semiconductor"]):
        return "Tech"
    if any(k in t for k in ["covid", "health", "vaccine", "doctor", "hospital", "disease"]):
        return "Health"
    if any(k in t for k in ["movie", "film", "bollywood", "hollywood", "music", "celebrity", "show"]):
        return "Entertainment"
    if any(k in t for k in ["space", "nasa", "spacex", "science", "research"]):
        return "Science"
    if any(k in t for k in ["football", "cricket", "soccer", "tennis", "olympic", "nba"]):
        return "Sports"
    if any(k in t for k in ["market", "stock", "economy", "business", "startup", "funding"]):
        return "Business"
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


def fetch_trending_mix(limit_per_source: int = 10) -> List[Dict]:
    """Combine multiple sources into a single list."""
    items = []
    items += fetch_newsapi_top_headlines(page_size=limit_per_source)
    items += fetch_reddit_trending(limit=limit_per_source)
    # de-duplicate by title
    seen = set()
    unique = []
    for it in items:
        t = (it.get("title") or "").strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            unique.append(it)
    return unique
