"""
ai_agent.py

Clean AI agent helpers for Truth-Guard.

Functions:
- fetch_news_sources(claim, limit=3): returns list of news source names (uses NewsAPI)
- fetch_factcheck_claims(claim, limit=3): returns short fact-check texts (uses FactCheck Tools API)
- verify_claim_with_ai(claim): calls OpenAI to produce a JSON result: {status, summary, sources, confidence}
"""

import os
import json
import logging
from typing import List, Dict, Any
import requests

try:
    import openai
except ImportError:
    openai = None

# Setup logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
FACTCHECK_API_KEY = os.getenv("FACTCHECK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


def fetch_news_sources(claim: str, limit: int = 3) -> List[str]:
    """Fetch top news source names related to the claim using NewsAPI."""
    if not NEWS_API_KEY:
        _logger.debug("No NEWS_API_KEY configured; skipping news fetch")
        return []

    try:
        url = "https://newsapi.org/v2/everything"
        params = {"q": claim, "apiKey": NEWS_API_KEY, "pageSize": limit}
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [a.get("source", {}).get("name") for a in articles if a.get("source")][:limit]
    except Exception as e:
        _logger.warning("fetch_news_sources error: %s", e)
        return []


def fetch_factcheck_claims(claim: str, limit: int = 3) -> List[str]:
    """Fetch short fact-check claim texts using Google Fact Check Tools API."""
    if not FACTCHECK_API_KEY:
        _logger.debug("No FACTCHECK_API_KEY configured; skipping factcheck fetch")
        return []

    try:
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {"query": claim, "key": FACTCHECK_API_KEY, "pageSize": limit}
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        items = resp.json().get("claims", [])
        return [item.get("text", "") for item in items[:limit]]
    except Exception as e:
        _logger.warning("fetch_factcheck_claims error: %s", e)
        return []


def _safe_json_parse(text: str) -> Any:
    """Attempt to parse JSON from text, even if embedded in extra text."""
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start:end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            pass
    return None


def _compute_confidence(ai_status: str, news_sources: list, fact_checks: list) -> int:
    """Compute confidence score from 0 to 100."""
    score = 50  # default neutral

    # AI signal
    if ai_status == "True":
        score += 30
    elif ai_status == "False":
        score -= 30

    # News sources signal
    score += min(len(news_sources), 3) * 5  # up to +15

    # Fact-check signal
    for fc in fact_checks:
        fc_lower = fc.lower()
        if "true" in fc_lower or "verified" in fc_lower:
            score += 10
        elif "false" in fc_lower or "misleading" in fc_lower:
            score -= 10

    return max(0, min(100, score))


def verify_claim_with_ai(claim: str) -> Dict[str, Any]:
    """
    Call OpenAI to analyze a claim and return JSON with:
    {
        "status": "True" | "False" | "Needs Verification",
        "summary": "...",
        "sources": ["source1", ...],
        "confidence": 0-100
    }
    """
    if not OPENAI_API_KEY:
        return {
            "status": "Needs Verification",
            "summary": "No OpenAI API key configured.",
            "sources": [],
            "confidence": 50
        }

    prompt = f"""
    You are a fact-checking assistant. Analyze the following claim and determine if it is True, False, or Needs Verification.
    Give a short summary and 1-3 credible sources (if available). Respond only in JSON format:

    {{
        "status": "True / False / Needs Verification",
        "summary": "...",
        "sources": ["source1", "source2"]
    }}

    Claim: {claim}
    """

    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage

        print("trying langchain")

        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL, temperature=0.2)
        response = llm([HumanMessage(content=prompt)])
        ai_result = _safe_json_parse(response.content)
    except Exception as e:
        _logger.warning("AI verification failed: %s", e)
        ai_result = None

    if not ai_result:
        ai_result = {
            "status": "Needs Verification",
            "summary": "AI could not parse the response.",
            "sources": []
        }

    # Combine with external sources for confidence
    news_sources = fetch_news_sources(claim)
    fact_checks = fetch_factcheck_claims(claim)
    confidence = _compute_confidence(ai_result.get("status", "Needs Verification"), news_sources, fact_checks)

    ai_result["sources"] = list(set(ai_result.get("sources", []) + news_sources + fact_checks))
    ai_result["confidence"] = confidence
    return ai_result


if __name__ == "__main__":
    # Quick local test
    test_claim = "ChatGPT can pass advanced exams"
    result = verify_claim_with_ai(test_claim)
    print(json.dumps(result, indent=2))
