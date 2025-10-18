import React, { useEffect, useState } from "react";
import StatsWidget from "../components/StatsWidget";
import NewsCard from "../components/NewsCard";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";

const Trending = () => {
  const [trendingNews, setTrendingNews] = useState([]);
  const [categories, setCategories] = useState(["All"]);
  const [filter, setFilter] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
  const newsRes = await axios.get(`${API_BASE_URL}/api/trending`);
        setTrendingNews(newsRes.data);

  const catRes = await axios.get(`${API_BASE_URL}/api/categories`);
        setCategories(catRes.data);
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

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
      <h1 className="text-3xl font-bold text-gray-900">Trending Topics</h1>

      {/* Stats Widgets */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {statsData.map((stat, idx) => (
          <StatsWidget key={idx} {...stat} />
        ))}
      </div>

      {/* Category Filters */}
      <div className="flex gap-4 overflow-x-auto py-4">
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
      </div>

      {/* News Cards */}
      {loading ? (
        <p>Loading trending news...</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredNews.map((news) => (
            <NewsCard
              key={news.id}
              title={news.title}
              source={news.source}
              summary={news.summary}
              category={news.category}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Trending;
