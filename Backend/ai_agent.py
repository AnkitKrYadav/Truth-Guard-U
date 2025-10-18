"""
ai_agent.py
Enhanced AI agent handlers for Truth-Guard.

Agents supported:
- OpenAI (gpt)
- HuggingFace (inference API)
- Google Gemini (via API)
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import requests
import time

# Optional imports
try:
    import openai
except ImportError:
    openai = None

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

try:
    from huggingface_hub import login as hf_login
except ImportError:
    hf_login = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Logging setup
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
FACTCHECK_API_KEY = os.getenv("FACTCHECK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

if genai and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# ---------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------
def _safe_json_parse(text: str) -> Any:
    """Try to safely parse a JSON object from text."""
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass
    return None


def _compute_confidence(ai_status: str, news_sources: list, fact_checks: list) -> int:
    """Compute confidence score 0–100."""
    score = 50
    if ai_status == "True":
        score += 30
    elif ai_status == "False":
        score -= 30
    score += min(len(news_sources), 3) * 5
    for fc in fact_checks:
        fc_l = fc.lower()
        if "true" in fc_l or "verified" in fc_l:
            score += 10
        elif "false" in fc_l or "fake" in fc_l:
            score -= 10
    return max(0, min(100, score))


def fetch_news_sources(claim: str, limit: int = 3) -> List[str]:
    if not NEWS_API_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {"q": claim, "apiKey": NEWS_API_KEY, "pageSize": max(1, min(limit, 3))}
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [a.get("source", {}).get("name") for a in articles if a.get("source")][:limit]
    except requests.exceptions.HTTPError as he:
        status = getattr(he.response, "status_code", None)
        if status == 429:
            _logger.info("fetch_news_sources rate-limited (429). Skipping enrichment.")
        elif status and 400 <= status < 500:
            _logger.info("fetch_news_sources client error %s. Skipping enrichment.", status)
        else:
            _logger.warning("fetch_news_sources error: %s", he)
        return []
    except Exception as e:
        _logger.warning("fetch_news_sources error: %s", e)
        return []


def fetch_factcheck_claims(claim: str, limit: int = 3) -> List[str]:
    if not FACTCHECK_API_KEY:
        return []
    try:
        url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        params = {"query": claim, "key": FACTCHECK_API_KEY, "pageSize": max(1, min(limit, 3))}
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        items = resp.json().get("claims", [])
        return [item.get("text", "") for item in items[:limit]]
    except requests.exceptions.HTTPError as he:
        status = getattr(he.response, "status_code", None)
        if status == 429:
            _logger.info("fetch_factcheck_claims rate-limited (429). Skipping enrichment.")
        elif status and 400 <= status < 500:
            _logger.info("fetch_factcheck_claims client error %s. Skipping enrichment.", status)
        else:
            _logger.warning("fetch_factcheck_claims error: %s", he)
        return []
    except Exception as e:
        _logger.warning("fetch_factcheck_claims error: %s", e)
        return []


# ---------------------------------------------------------------------
# AI Agents
# ---------------------------------------------------------------------

def openai_agent(claim: str) -> Dict[str, Any]:
    """Use OpenAI GPT model."""
    if not OPENAI_API_KEY:
        return {"status": "Needs Verification", "summary": "OpenAI key missing.", "sources": [], "confidence": 50}
    try:
        from langchain_openai import ChatOpenAI
        try:
            from langchain.schema import HumanMessage  # older versions
        except Exception:
            from langchain_core.messages import HumanMessage  # newer versions

        llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name=OPENAI_MODEL, temperature=0.2)
        prompt = f"""
        You are a fact-checking assistant. Analyze this claim and respond in JSON format:
        {{
            "status": "True / False / Needs Verification",
            "summary": "...",
            "sources": ["..."]
        }}
        Claim: {claim}
        """

        # Use invoke() per LangChain deprecation notice
        resp = llm.invoke([HumanMessage(content=prompt)])
        data = _safe_json_parse(resp.content if hasattr(resp, "content") else str(resp))
        if not data:
            data = {"status": "Needs Verification", "summary": "AI could not parse.", "sources": []}
        return data
    except Exception as e:
        _logger.warning("OpenAI agent failed: %s", e)
        return {"status": "Needs Verification", "summary": str(e), "sources": [], "confidence": 50}


def huggingface_agent(claim: str) -> Dict[str, Any]:
    """Call HuggingFace Inference API for fact-checking."""
    
    # Check if API key is valid
    if not HF_API_KEY:
        return {
            "status": "Needs Verification", 
            "summary": "HuggingFace requires an API key. Get a free key at https://huggingface.co/settings/tokens (Create a 'Read' token)", 
            "sources": [], 
            "confidence": 50
        }
    
    # Try multiple available models
    models_to_try = [
        "distilbert/distilbert-base-uncased-finetuned-sst-2-english",  # Correct namespace
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "facebook/bart-large-mnli"
    ]
    
    for model_name in models_to_try:
        url = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": claim}
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            
            _logger.info(f"HF API Response Status for {model_name}: {resp.status_code}")
            
            if resp.status_code == 404:
                _logger.warning(f"Model {model_name} not found, trying next...")
                continue
            
            if resp.status_code == 403:
                return {
                    "status": "Needs Verification",
                    "summary": "Your HuggingFace API key is invalid or has been revoked. Please create a new 'Read' token at https://huggingface.co/settings/tokens and update your .env file.",
                    "sources": [],
                    "confidence": 50
                }
            
            if resp.status_code == 401:
                return {
                    "status": "Needs Verification",
                    "summary": "Authentication failed. Please verify your HuggingFace API key in the .env file.",
                    "sources": [],
                    "confidence": 50
                }
            
            resp.raise_for_status()
            result = resp.json()
            
            # Check for model loading error
            if isinstance(result, dict) and "error" in result:
                error_msg = result.get("error", "")
                if "loading" in error_msg.lower():
                    return {"status": "Needs Verification", "summary": "Model is loading, please try again in a moment.", "sources": [], "confidence": 50}
                _logger.warning(f"Model error: {error_msg}, trying next model...")
                continue
            
            # Parse response (works for both sentiment and NLI models)
            if isinstance(result, list) and result:
                # Handle nested list structure
                top_results = result[0] if isinstance(result[0], list) else result
                
                if isinstance(top_results, list) and top_results:
                    top_result = top_results[0]
                else:
                    top_result = top_results
                
                if isinstance(top_result, dict):
                    label = top_result.get("label", "").upper()
                    score = top_result.get("score", 0)
                    
                    # Map result to fact-check status
                    status = "Needs Verification"
                    if "POSITIVE" in label or "ENTAILMENT" in label:
                        summary = f"HuggingFace AI analysis suggests this might be plausible. ({label}, confidence: {score:.1%}). Independent verification recommended."
                    elif "NEGATIVE" in label or "CONTRADICTION" in label:
                        summary = f"HuggingFace AI analysis suggests skepticism. ({label}, confidence: {score:.1%}). Independent verification recommended."
                    else:
                        summary = f"HuggingFace AI analysis: {label} (confidence: {score:.1%}). Manual fact-checking recommended."
                    
                    confidence = int(score * 100)
                    
                    return {
                        "status": status, 
                        "summary": summary, 
                        "sources": [f"HuggingFace AI ({model_name.split('/')[-1]})"], 
                        "confidence": confidence
                    }
            
            # If we got here, response format was unexpected, try next model
            _logger.warning(f"Unexpected response format from {model_name}, trying next...")
            continue
            
        except Exception as e:
            _logger.warning(f"HuggingFace model {model_name} failed: %s", e)
            continue
    
    # All models failed
    return {
        "status": "Needs Verification", 
        "summary": "HuggingFace AI service temporarily unavailable. Please try OpenAI or check back later.", 
        "sources": [], 
        "confidence": 50
    }


def llama_agent(claim: str) -> Dict[str, Any]:
    """Use local Ollama (LLaMA) model."""
    try:
        from ollama import chat
        res = chat(model="llama3", messages=[{"role": "user", "content": claim}])
        content = res.get("message", {}).get("content", "")
        parsed = _safe_json_parse(content) or {"status": "Needs Verification", "summary": content, "sources": []}
        return parsed
    except Exception as e:
        _logger.warning("LLaMA agent failed: %s", e)
        return {"status": "Needs Verification", "summary": str(e), "sources": [], "confidence": 50}


def gemini_agent(claim: str) -> Dict[str, Any]:
    """Use Google Gemini API for fact-checking."""
    if not GEMINI_API_KEY:
        return {
            "status": "Needs Verification",
            "summary": "Google Gemini API key missing. Get a free key at https://aistudio.google.com/app/apikey",
            "sources": [],
            "confidence": 50
        }
    
    if not genai:
        return {
            "status": "Needs Verification",
            "summary": "Google Generative AI package not installed. Run: pip install google-generativeai",
            "sources": [],
            "confidence": 50
        }
    
    try:
        # Use the official SDK and default model from env
        model = genai.GenerativeModel(GEMINI_MODEL)

        json_skeleton = (
            '{\n'
            '    "status": "True / False / Needs Verification",\n'
            '    "summary": "brief explanation",\n'
            '    "sources": ["source1", "source2"]\n'
            '}\n'
        )
        prompt = (
            "You are a fact-checking assistant. Analyze the following claim and determine if it is True, False, or Needs Verification.\n"
            "Give a short summary and 1-3 credible sources (if available). Respond ONLY in JSON format:\n\n"
            f"{json_skeleton}\n"
            f"Claim: {claim}"
        )

        response = model.generate_content(prompt)

        _logger.info(f"Gemini API call successful")

        # Parse response
        if response and getattr(response, "text", None):
            ai_result = _safe_json_parse(response.text)

            if ai_result:
                return ai_result
            else:
                # Fallback if JSON parsing fails
                return {
                    "status": "Needs Verification",
                    "summary": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                    "sources": ["Google Gemini AI"],
                    "confidence": 50
                }

        return {
            "status": "Needs Verification",
            "summary": "No response from Gemini API.",
            "sources": [],
            "confidence": 50
        }

    except Exception as e:
        error_msg = str(e)
        _logger.warning(f"Gemini agent failed: {error_msg}")
        
        # Provide helpful error messages
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return {
                "status": "Needs Verification",
                "summary": "Google Gemini API key is invalid. Get a new key at https://aistudio.google.com/app/apikey",
                "sources": [],
                "confidence": 50,
                "error_code": 401
            }
        elif "404" in error_msg or "not found" in error_msg.lower():
            return {
                "status": "Needs Verification",
                "summary": "Gemini API access issue. Make sure Gemini API is enabled in your Google Cloud project.",
                "sources": [],
                "confidence": 50,
                "error_code": 404
            }
        elif "429" in error_msg or "quota" in error_msg.lower():
            # Try to extract retry seconds if present
            retry_after: Optional[int] = None
            try:
                # Look for 'retry_delay {\n  seconds: N' pattern
                marker = "retry_delay {"
                if marker in error_msg:
                    seg = error_msg.split(marker, 1)[1]
                    # find 'seconds:' after marker
                    parts = seg.split("seconds:", 1)
                    if len(parts) > 1:
                        num = parts[1].split("\n", 1)[0].strip()
                        retry_after = int(float(num))
            except Exception:
                retry_after = None
            return {
                "status": "Needs Verification",
                "summary": f"Gemini rate limited. Please retry later.",
                "sources": [],
                "confidence": 50,
                "error_code": 429,
                "retry_after": retry_after
            }
        else:
            return {
                "status": "Needs Verification",
                "summary": f"Gemini error: {error_msg[:100]}. Try OpenAI or HuggingFace instead.",
                "sources": [],
                "confidence": 50,
                "error_code": 500
            }


# ---------------------------------------------------------------------
# Main Verify Function
# ---------------------------------------------------------------------
def verify_claim_with_ai(claim: str, agent: str = "gemini") -> Dict[str, Any]:
    """Dispatch to selected agent."""
    _logger.info(f"🔍 Verifying claim with agent ({agent}): {claim}")

    chosen = agent
    ai_result: Dict[str, Any]

    if agent == "auto":
        # Try Gemini -> OpenAI -> HF
        for candidate in ["gemini", "openai", "hf"]:
            _logger.info("Trying agent: %s", candidate)
            if candidate == "gemini":
                ai_result = gemini_agent(claim)
            elif candidate == "openai":
                ai_result = openai_agent(claim)
            else:
                ai_result = huggingface_agent(claim)

            error_code = ai_result.get("error_code") if isinstance(ai_result, dict) else None
            if error_code == 429:
                # Immediate fallback without sleeping to keep API responsive
                _logger.info("Agent %s rate-limited. Falling back.", candidate)
                chosen = candidate  # keep track for logging even if falling back
                continue
            # Accept first non-rate-limited response
            chosen = candidate
            break
        else:
            # All failed in rate-limit manner
            ai_result = {"status": "Needs Verification", "summary": "All AI providers rate-limited. Please retry.", "sources": [], "confidence": 50}
    else:
        if agent == "openai":
            ai_result = openai_agent(claim)
        elif agent == "hf":
            ai_result = huggingface_agent(claim)
        elif agent == "gemini":
            ai_result = gemini_agent(claim)
        elif agent == "llama":
            ai_result = llama_agent(claim)
        else:
            ai_result = {"status": "Needs Verification", "summary": "Unknown agent.", "sources": [], "confidence": 50}

    # Combine with external sources
    news_sources = fetch_news_sources(claim)
    fact_checks = fetch_factcheck_claims(claim)
    ai_result["sources"] = list(set(ai_result.get("sources", []) + news_sources + fact_checks))
    ai_result["confidence"] = _compute_confidence(ai_result.get("status", ""), news_sources, fact_checks)
    # Report actual used agent
    ai_result["agent"] = chosen
    ai_result["agent_used"] = chosen
    return ai_result


if __name__ == "__main__":
    test_claim = "Elon Musk is the CEO of Tesla."
    for a in ["openai", "hf", "llama"]:
        print(f"\n=== {a.upper()} ===")
        print(json.dumps(verify_claim_with_ai(test_claim, a), indent=2))
