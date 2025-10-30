import axios from "axios";

// Single source of truth for API base URL
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "";

export const postVerify = (claim, agent = "openai") => {
  return axios.post(`${API_BASE_URL}/api/verify`, { claim, agent });
};

export const postExpertVerification = (key, status, notes) => {
  let adminKey = "";
  try { adminKey = localStorage.getItem('tg_admin_key') || ""; } catch {}
  return axios.post(
    `${API_BASE_URL}/api/expert-verifications`,
    { key, status, notes },
    { headers: adminKey ? { 'X-Admin-Key': adminKey } : {} }
  );
};

const client = axios.create({
  baseURL: API_BASE_URL,
});

export default client;

// ---- Lightweight client-side cache (localStorage) ----
const CACHE_PREFIX = "tg_cache_";

function setCache(key, data) {
  try {
    const payload = { ts: Date.now(), data };
    localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(payload));
  } catch {}
}

function getCache(key, maxAgeMs = 2 * 60 * 1000) { // default 2 minutes
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    const payload = JSON.parse(raw);
    if (!payload || typeof payload.ts !== "number") return null;
    if (Date.now() - payload.ts > maxAgeMs) return null;
    return payload.data;
  } catch {
    return null;
  }
}

// Stale-while-revalidate helper for trending news
export async function fetchTrendingLiveSWR({ agent = "auto", region = "in", limit = 12, cacheMs = 2 * 60 * 1000 }) {
  const cacheKey = `trending_${region}_${agent}_${limit}`;
  const cached = getCache(cacheKey, cacheMs);
  let fresh = null;
  try {
    const res = await axios.get(`${API_BASE_URL}/api/trending/live?agent=${agent}&limit=${limit}&region=${region}`);
    fresh = Array.isArray(res.data) ? res.data : [];
    // Persist cache only if non-empty to avoid overwriting with blanks
    if (fresh && fresh.length > 0) {
      setCache(cacheKey, fresh);
    }
  } catch (e) {
    // Network error: keep using cache if present
  }
  return { cached, fresh };
}
