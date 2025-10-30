import React, { useEffect, useRef, useState } from "react";
import StatsWidget from "../components/StatsWidget";
import NewsCard from "../components/NewsCard";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";

const Dashboard = () => {
  const [trendingNews, setTrendingNews] = useState([]);
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const didFetchRef = useRef(false); // Guard double fetch in React StrictMode (dev)

  useEffect(() => {
    if (didFetchRef.current) return; // prevent duplicate calls in dev
    didFetchRef.current = true;

    async function fetchData() {
      try {
        // Fetch top trending news from database (not live API)
        const resNews = await axios.get(`${API_BASE_URL}/api/trending/top`);
        setTrendingNews(resNews.data || []);

        // Fetch real stats from backend
        const resStats = await axios.get(`${API_BASE_URL}/api/stats`);
        const statsData = [
          { title: "Verified Claims", value: resStats.data.verified || 0, icon: "✅", bgColor: "bg-green-100" },
          { title: "Trending Today", value: resStats.data.trending || 0, icon: "🔥", bgColor: "bg-red-100" },
          { title: "Active Users", value: resStats.data.users || 0, icon: "👤", bgColor: "bg-blue-100" },
          { title: "Fact Checks Completed", value: resStats.data.fact_checks || 0, icon: "📊", bgColor: "bg-yellow-100" }
        ];
        setStats(statsData);
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="p-8 bg-transparent text-gray-900 dark:text-gray-100 min-h-screen space-y-8">
      {/* Hero Section */}
      <header className="text-center space-y-3 mb-8">
        <h1 className="text-5xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400">
          TruthGuard Dashboard
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Real-time fact checking and trending news at your fingertips.
        </p>
      </header>

      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <StatsWidget
            key={idx}
            {...stat}
            className="fade-in-up"
            style={{ animationDelay: `${idx * 70}ms` }}
          />
        ))}
      </div>

      {/* Trending News Section */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Top 5 Trending News of Today</h2>
          <span className="text-sm text-gray-500 dark:text-gray-400 font-medium px-3 py-1 rounded-full bg-white/50 dark:bg-gray-800/30 backdrop-blur-md border border-gray-200/60 dark:border-gray-700/60">
            {new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })}
          </span>
        </div>
        {loading ? (
          <p className="text-gray-700 dark:text-gray-300">Loading news...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {trendingNews.map((news, idx) => (
              <div key={idx} className="fade-in-up h-full" style={{ animationDelay: `${idx * 80}ms` }}>
                <NewsCard {...news} />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default Dashboard;
