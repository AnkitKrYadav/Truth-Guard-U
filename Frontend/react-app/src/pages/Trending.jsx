import React, { useEffect, useState } from "react";
import StatsWidget from "../components/StatsWidget";
import NewsCard from "../components/NewsCard";
import axios from "axios";
import { API_BASE_URL, postExpertVerification } from "../utils/api";

const Trending = () => {
  const [trendingNews, setTrendingNews] = useState([]);
  const [categories, setCategories] = useState(["All"]);
  const [regions, setRegions] = useState(["in"]);
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState("auto");
  const [region, setRegion] = useState("in");
  const [submitting, setSubmitting] = useState(null);

  const fetchTrending = async () => {
    setLoading(true);
    try {
      let usedAgent = agent;
      let newsRes;
      try {
        newsRes = await axios.get(`${API_BASE_URL}/api/trending/live?agent=${agent}&limit=12&region=${region}`);
      } catch (err) {
        // If selected agent is rate-limited and it's OpenAI, fallback to HuggingFace
        if (agent === "openai" && err.response && err.response.status === 429) {
          usedAgent = "hf";
          newsRes = await axios.get(`${API_BASE_URL}/api/trending/live?agent=hf&limit=12&region=${region}`);
        } else {
          throw err;
        }
      }
      const items = (newsRes.data || []).map((n) => ({
        id: n.id || n.url || n.title,
        title: n.title,
        source: n.source,
        summary: n.summary,
        category: n.category || "General",
        url: n.url,
        verification: n.verification,
        actions: n.actions || { like: 0, dislike: 0, bookmark: 0 },
      }));
      setTrendingNews(items);
      // Only show categories that have news
      const categoryCounts = items.reduce((acc, item) => {
        acc[item.category] = (acc[item.category] || 0) + 1;
        return acc;
      }, {});
      const derivedCats = ["All", ...Object.keys(categoryCounts)];
      setCategories(derivedCats);
      if (agent === "openai" && usedAgent === "hf") {
        window.alert("OpenAI rate limit reached. Showing HuggingFace results instead.");
      }
    } catch (err) {
      console.error("Error fetching data:", err);
    } finally {
      setLoading(false);
    }
  };

  // Debounce data fetching on agent/region changes
  useEffect(() => {
    const t = setTimeout(() => {
      fetchTrending();
    }, 400);
    return () => clearTimeout(t);
    // eslint-disable-next-line
  }, [agent, region]);

  useEffect(() => {
    // Fetch categories and regions from backend
    async function fetchFilters() {
      try {
        const catsRes = await axios.get(`${API_BASE_URL}/api/admin/categories`);
        setCategories(["All", ...catsRes.data]);
        const regionsRes = await axios.get(`${API_BASE_URL}/api/admin/regions`);
        const raw = regionsRes?.data;
        let list = [];
        if (Array.isArray(raw)) {
          list = raw;
        } else if (raw && Array.isArray(raw?.regions)) {
          list = raw.regions;
        } else if (raw && typeof raw === "object") {
          // Try to pull values from an object shape
          const vals = Object.values(raw).flat();
          list = vals.filter(Boolean);
        }
        // Ensure we always have a sane default set
        if (!list || list.length === 0) {
          list = ["all", "in", "us", "gb", "au", "ca", "de", "fr", "jp", "ru", "cn"];
        }
        // Dedupe and normalize with 'all' first
        const normalized = Array.from(new Set(["all", ...list.map(String)])).filter(Boolean);
        setRegions(normalized);
        // Ensure currently selected region is valid
        if (!normalized.includes(region)) {
          setRegion(normalized[0] || "all");
        }
      } catch (err) {
        // fallback to defaults
        setCategories(["All", "Politics", "Tech", "Health", "Entertainment", "Science", "Sports", "Business", "World", "Local", "Crime", "Environment", "Education", "Lifestyle", "Travel", "Food", "Opinion", "General"]);
        setRegions(["in", "us", "gb", "au", "ca", "de", "fr", "jp", "ru", "cn"]);
      }
    }
    fetchFilters();
  }, []);

  const filteredNews = trendingNews.filter(
    (item) => filter === "All" || item.category === filter
  );

  // Stats: Always show main categories
  // Only show stats for categories with news (plus Total Trending News)
  const totalIcon = (
    <svg className="w-7 h-7" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M3 20h18v1H3z"/>
      <rect x="6" y="9" width="3" height="9" rx="1"></rect>
      <rect x="11" y="5" width="3" height="13" rx="1"></rect>
      <rect x="16" y="11" width="3" height="7" rx="1"></rect>
    </svg>
  );
  const allStats = [
    { title: "Politics", icon: "🗳️", bgColor: "bg-red-100", darkBg: "dark:bg-red-900/40" },
    { title: "Tech", icon: "💻", bgColor: "bg-yellow-100", darkBg: "dark:bg-yellow-900/30" },
    { title: "Health", icon: "❤️", bgColor: "bg-green-100", darkBg: "dark:bg-green-900/30" },
    { title: "Entertainment", icon: "🎬", bgColor: "bg-purple-100", darkBg: "dark:bg-purple-900/30" },
    { title: "Science", icon: "🔬", bgColor: "bg-indigo-100", darkBg: "dark:bg-indigo-900/30" },
    { title: "Sports", icon: "🏅", bgColor: "bg-orange-100", darkBg: "dark:bg-orange-900/30" },
    { title: "Business", icon: "💼", bgColor: "bg-teal-100", darkBg: "dark:bg-teal-900/30" },
    { title: "World", icon: "🌎", bgColor: "bg-cyan-100", darkBg: "dark:bg-cyan-900/30" },
    { title: "Local", icon: "🏠", bgColor: "bg-gray-200", darkBg: "dark:bg-gray-800/40" },
    { title: "Crime", icon: "🚔", bgColor: "bg-pink-100", darkBg: "dark:bg-pink-900/30" },
    { title: "Environment", icon: "🌱", bgColor: "bg-green-200", darkBg: "dark:bg-green-900/30" },
    { title: "Education", icon: "🎓", bgColor: "bg-blue-200", darkBg: "dark:bg-blue-900/30" },
    { title: "Lifestyle", icon: "💃", bgColor: "bg-pink-200", darkBg: "dark:bg-pink-900/30" },
    { title: "Travel", icon: "✈️", bgColor: "bg-yellow-200", darkBg: "dark:bg-yellow-900/30" },
    { title: "Food", icon: "🍔", bgColor: "bg-orange-200", darkBg: "dark:bg-orange-900/30" },
    { title: "Opinion", icon: "💬", bgColor: "bg-gray-300", darkBg: "dark:bg-gray-800/40" },
    { title: "General", icon: "📰", bgColor: "bg-gray-100", darkBg: "dark:bg-gray-800/40" },
  ];
  const catsWithNews = Array.from(new Set(trendingNews.map(n => n.category).filter(Boolean)));
  const statsData = [
    { title: "Total Trending News", value: trendingNews.length, icon: totalIcon, bgColor: "bg-blue-100", darkBg: "dark:bg-blue-900/30" },
    ...allStats
      .filter(stat => catsWithNews.includes(stat.title))
      .map(stat => ({
        ...stat,
        value: trendingNews.filter(n => n.category === stat.title).length
      }))
  ];


  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Trending Topics</h1>
        <button
          onClick={fetchTrending}
          className="ml-4 inline-flex items-center justify-center h-10 w-10 rounded-full border border-blue-200 bg-blue-50 text-blue-600 hover:bg-blue-100 hover:border-blue-300 transition shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading}
          aria-label="Refresh trending news"
        >
          <svg
            className={`w-5 h-5 ${loading ? "animate-spin" : ""}`}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="23 4 23 10 17 10" />
            <polyline points="1 20 1 14 7 14" />
            <path d="M3.51 9a9 9 0 0114.73-3.36L23 10" />
            <path d="M20.49 15a9 9 0 01-14.73 3.36L1 14" />
          </svg>
        </button>
      </div>

      {/* Stats Widgets */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {statsData.map((stat, idx) => (
          <StatsWidget
            key={idx}
            {...stat}
            className="fade-in-up"
            style={{ animationDelay: `${idx * 70}ms` }}
          />
        ))}
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 overflow-x-auto py-4">
        {/* Category Filters */}
        {/* Only show categories with news (plus All) */}
        {(() => {
          const catsWithNews = Array.from(new Set(trendingNews.map(n => n.category).filter(Boolean)));
          const catsToShow = ["All", ...catsWithNews];
          return catsToShow.map((cat, idx) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-4 py-2 rounded-full font-medium transition ${
                filter === cat
                  ? "bg-blue-600 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-blue-500 hover:text-white"
              } fade-in-up`}
              style={{ animationDelay: `${idx * 40}ms` }}
            >
              {cat}
            </button>
          ));
        })()}

        {/* Region Toggle */}
        <div className="flex items-center gap-2 ml-2">
          <span className="text-sm text-gray-600 dark:text-gray-300">Region:</span>
          <select
            value={region}
            onChange={e => setRegion(e.target.value)}
            className="px-2 py-1 rounded border border-gray-300 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            {(Array.isArray(regions) ? regions : []).map(r => (
              <option key={r} value={r}>{r === "all" ? "All Regions" : r.toUpperCase()}</option>
            ))}
          </select>
        </div>

        {/* Agent Toggle */}
        <div className="ml-auto flex items-center gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-300">Model:</span>
          <button
            onClick={() => setAgent("auto")}
            className={`px-3 py-1 rounded transition-colors duration-200 ${
              agent === "auto" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-blue-500 hover:text-white"
            } fade-in-up`}
            style={{ animationDelay: "0ms" }}
          >
            Auto
          </button>
          <button
            onClick={() => setAgent("gemini")}
            className={`px-3 py-1 rounded transition-colors duration-200 ${
              agent === "gemini" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-blue-500 hover:text-white"
            } fade-in-up`}
            style={{ animationDelay: "40ms" }}
          >
            Gemini
          </button>
          <button
            onClick={() => setAgent("openai")}
            className={`px-3 py-1 rounded transition-colors duration-200 ${
              agent === "openai" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-blue-500 hover:text-white"
            } fade-in-up`}
            style={{ animationDelay: "80ms" }}
          >
            OpenAI
          </button>
          <button
            onClick={() => setAgent("hf")}
            className={`px-3 py-1 rounded transition-colors duration-200 ${
              agent === "hf" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700 hover:bg-blue-500 hover:text-white"
            } fade-in-up`}
            style={{ animationDelay: "120ms" }}
          >
            HuggingFace
          </button>
        </div>
      </div>

      {/* News Cards */}
      {loading ? (
        <p>Loading trending news...</p>
      ) : filteredNews.length === 0 ? (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-6 text-center">
          <svg className="w-16 h-16 mx-auto mb-4 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">No Trending News Available</h3>
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
            We're currently unable to fetch trending news. This may be due to API rate limits or temporary service issues.
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Try again in a few minutes, or contact support if the issue persists.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredNews.map((news, idx) => {
            const v = news.verification || {};
            const status = v.status;
            const conf = v.confidence;
            const expert = v.expert;
            const providerRaw = (v.agent_used || v.agent || "");
            const provider = providerRaw === "hf" ? "HuggingFace" : providerRaw === "llama" ? "LLaMA" : providerRaw === "openai" ? "OpenAI" : providerRaw === "gemini" ? "Gemini" : providerRaw;
            const key = news.url || news.title;
            const actions = news.actions || { like: 0, dislike: 0, bookmark: 0 };
            
            const handleAction = async (action) => {
              try {
                await axios.post(`${API_BASE_URL}/api/news/action`, {
                  news_key: key,
                  action: action,
                });
                // Refresh to update counts
                await fetchTrending();
              } catch (err) {
                console.error("Error performing action:", err);
              }
            };

            const handleVerify = async () => {
              try {
                setSubmitting(key);
                await axios.post(`${API_BASE_URL}/api/news/verify`, {
                  news_key: key,
                  title: news.title,
                  agent: agent,
                });
                // Refresh to show updated verification
                await fetchTrending();
              } catch (err) {
                console.error("Error verifying news:", err);
              } finally {
                setSubmitting(null);
              }
            };

            return (
              <div
                key={news.id}
                className="flex flex-col gap-2 border border-gray-200 dark:border-gray-700 rounded-xl p-4 bg-white dark:bg-gray-900 shadow-sm fade-in-up"
                style={{ animationDelay: `${idx * 60}ms` }}
              >
                {status && (
                  <div className={`flex flex-wrap items-center gap-2 mb-2`}>
                    <span
                      className={`text-xs font-semibold px-2 py-1 rounded-full ${
                        (expert?.status || status) === 'True'
                          ? 'bg-green-200 text-green-800'
                          : (expert?.status || status) === 'False'
                          ? 'bg-red-200 text-red-800'
                          : 'bg-yellow-200 text-yellow-800'
                      }`}
                      title={provider ? `Verified via ${provider}` : undefined}
                    >
                      {(expert?.status || status)}
                      {conf !== undefined ? ` • ${conf}%` : ''}
                      {expert ? ' • Expert' : ''}
                      {v.cached ? ' • Cached' : ''}
                      {provider ? ` • via ${provider}` : ''}
                    </span>
                  </div>
                )}
                <NewsCard
                  title={news.title}
                  source={news.source}
                  summary={news.summary}
                  category={news.category}
                  url={news.url}
                  expert={expert}
                  frameless
                />
                
                {/* Professional Action Buttons */}
                <div className="mt-3 pt-2 flex items-center justify-between gap-2 flex-wrap border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleAction("like")}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium bg-green-50 hover:bg-green-100 text-green-700 border border-green-200 transition shadow-sm"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                      </svg>
                      {actions.like > 0 && <span>{actions.like}</span>}
                    </button>
                    
                    <button
                      onClick={() => handleAction("dislike")}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 transition shadow-sm"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.105-1.79l-.05-.025A4 4 0 0011.055 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
                      </svg>
                      {actions.dislike > 0 && <span>{actions.dislike}</span>}
                    </button>
                    
                    <button
                      onClick={() => handleAction("bookmark")}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 transition shadow-sm"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
                      </svg>
                      {actions.bookmark > 0 && <span>{actions.bookmark}</span>}
                    </button>
                  </div>
                  
                  <button
                    onClick={handleVerify}
                    disabled={submitting === key}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200 transition shadow-sm disabled:opacity-50"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Verify
                  </button>
                </div>
                
                {/* Expert Verification Controls - Keep for admin/expert use */}
                <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Expert Override:</p>
                  <div className="flex items-center gap-2">
                    <button
                      disabled={submitting === key}
                      onClick={async () => {
                        setSubmitting(key);
                        try {
                          await postExpertVerification(key, "True");
                          await fetchTrending();
                        } finally {
                          setSubmitting(null);
                        }
                      }}
                      className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border border-green-400 text-green-600 bg-green-50 hover:bg-green-100 transition disabled:opacity-50"
                    >
                      ✓ True
                    </button>
                    <button
                      disabled={submitting === key}
                      onClick={async () => {
                        setSubmitting(key);
                        try {
                          await postExpertVerification(key, "False");
                          await fetchTrending();
                        } finally {
                          setSubmitting(null);
                        }
                      }}
                      className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border border-red-400 text-red-600 bg-red-50 hover:bg-red-100 transition disabled:opacity-50"
                    >
                      ✗ False
                    </button>
                    <button
                      disabled={submitting === key}
                      onClick={async () => {
                        setSubmitting(key);
                        try {
                          await postExpertVerification(key, "Needs Verification");
                          await fetchTrending();
                        } finally {
                          setSubmitting(null);
                        }
                      }}
                      className="flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border border-yellow-400 text-yellow-600 bg-yellow-50 hover:bg-yellow-100 transition disabled:opacity-50"
                    >
                      ? Review
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Trending;
