import React, { useEffect, useState } from "react";
import StatsWidget from "../components/StatsWidget";
import NewsCard from "../components/NewsCard";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";

const Dashboard = () => {
  const [trendingNews, setTrendingNews] = useState([]);
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch news
  const resNews = await axios.get(`${API_BASE_URL}/api/trending`);
        setTrendingNews(resNews.data);

        // Build stats with real numbers
        const statsData = [
          { title: "Verified Claims", value: resNews.data.length, icon: "✅", bgColor: "bg-green-100" },
          { title: "Trending Today", value: resNews.data.length, icon: "🔥", bgColor: "bg-red-100" },
          { title: "New Users", value: 320, icon: "👤", bgColor: "bg-blue-100" }, // placeholder
          { title: "Fact Checks Completed", value: 980, icon: "📊", bgColor: "bg-yellow-100" } // placeholder
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
    <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen space-y-6">
      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <StatsWidget key={idx} {...stat} />
        ))}
      </div>

      {/* Trending News Section */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Trending News</h2>
        {loading ? (
          <p className="text-gray-700 dark:text-gray-300">Loading news...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {trendingNews.map((news, idx) => (
              <NewsCard key={idx} {...news} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
