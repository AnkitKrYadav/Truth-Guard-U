import React, { useEffect, useState } from "react";
import StatsWidget from "../components/StatsWidget";
import NewsCard from "../components/NewsCard";
import axios from "axios";
import { API_BASE_URL, postExpertVerification } from "../utils/api";

const Trending = () => {
  const [trendingNews, setTrendingNews] = useState([]);
  const [categories, setCategories] = useState(["All"]);
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);
  const [agent, setAgent] = useState("openai");
  const [region, setRegion] = useState("in");
  const [submitting, setSubmitting] = useState(null); // key of item being submitted

  const fetchTrending = async () => {
    setLoading(true);
    try {
      let usedAgent = agent;
      let newsRes;
      try {
        newsRes = await axios.get(`${API_BASE_URL}/api/trending/live?agent=${agent}&limit=12&region=${region}`);
      } catch (err) {
        // If OpenAI is rate-limited, fallback to HuggingFace
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
      const derivedCats = ["All", ...Array.from(new Set(items.map(i => i.category).filter(Boolean)))];
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

  useEffect(() => {
    fetchTrending();
    // eslint-disable-next-line
  }, [agent, region]);

  const filteredNews = trendingNews.filter(
    (item) => filter === "All" || item.category === filter
  );

  // Stats based on categories
const statsData = [
  { title: "Total Trending News", value: trendingNews.length, icon: "📊", bgColor: "bg-blue-100" },
  { title: "Politics", value: trendingNews.filter(n => n.category === "Politics").length, icon: "🗳️", bgColor: "bg-red-100" },
  { title: "Health", value: trendingNews.filter(n => n.category === "Health").length, icon: "❤️", bgColor: "bg-green-100" },
  { title: "Tech", value: trendingNews.filter(n => n.category === "Tech").length, icon: "💻", bgColor: "bg-yellow-100" },
  { title: "Entertainment", value: trendingNews.filter(n => n.category === "Entertainment").length, icon: "🎬", bgColor: "bg-purple-100" },
];


  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Trending Topics</h1>
        <button
          onClick={fetchTrending}
          className="ml-4 px-4 py-2 rounded bg-blue-600 text-white font-semibold hover:bg-blue-700 transition"
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      {/* Stats Widgets */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {statsData.map((stat, idx) => (
          <StatsWidget key={idx} {...stat} />
        ))}
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-4 overflow-x-auto py-4">
        {/* Category Filters */}
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-4 py-2 rounded-full font-medium transition ${
              filter === cat
                ? "bg-blue-600 text-white"
                : "bg-gray-200 text-gray-700 hover:bg-blue-500 hover:text-white"
            }`}
          >
            {cat}
          </button>
        ))}

        {/* Region Toggle */}
        <div className="flex items-center gap-2 ml-2">
          <span className="text-sm text-gray-600 dark:text-gray-300">Region:</span>
          <select
            value={region}
            onChange={e => setRegion(e.target.value)}
            className="px-2 py-1 rounded border border-gray-300 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="in">India</option>
            <option value="us">USA</option>
            <option value="gb">UK</option>
            <option value="au">Australia</option>
            <option value="ca">Canada</option>
            <option value="de">Germany</option>
            <option value="fr">France</option>
            <option value="jp">Japan</option>
            <option value="ru">Russia</option>
            <option value="cn">China</option>
          </select>
        </div>

        {/* Agent Toggle */}
        <div className="ml-auto flex items-center gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-300">Model:</span>
          <button
            onClick={() => setAgent("openai")}
            className={`px-3 py-1 rounded ${agent === "openai" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"}`}
          >
            OpenAI
          </button>
          <button
            onClick={() => setAgent("hf")}
            className={`px-3 py-1 rounded ${agent === "hf" ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"}`}
          >
            HuggingFace
          </button>
        </div>
      </div>

      {/* News Cards */}
      {loading ? (
        <p>Loading trending news...</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredNews.map((news) => {
            const v = news.verification || {};
            const status = v.status;
            const conf = v.confidence;
            const expert = v.expert;
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
              <div key={news.id} className="relative">
                {status && (
                  <span className={`absolute top-2 right-2 text-xs font-semibold px-2 py-1 rounded-full z-10 ${
                    (expert?.status || status) === 'True' ? 'bg-green-200 text-green-800' : (expert?.status || status) === 'False' ? 'bg-red-200 text-red-800' : 'bg-yellow-200 text-yellow-800'
                  }`}>
                    {(expert?.status || status)}{conf !== undefined ? ` • ${conf}%` : ''}{expert ? ' • Expert' : ''}{v.cached ? ' • Cached' : ''}
                  </span>
                )}
                <NewsCard
                  title={news.title}
                  source={news.source}
                  summary={news.summary}
                  category={news.category}
                  url={news.url}
                />
                
                {/* Professional Action Buttons */}
                <div className="mt-3 flex items-center justify-between gap-2 flex-wrap">
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
