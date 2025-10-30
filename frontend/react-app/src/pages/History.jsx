import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";
import { useToast } from "../context/ToastContext";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/history`);
        setHistory(res.data || []);
      } catch (err) {
        setHistory([]);
        toast({ title: "Failed to load history", message: err.message || "Unknown error", type: "error" });
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
    // eslint-disable-next-line
  }, []);

  return (
    <div className="p-8 bg-transparent text-gray-900 dark:text-gray-100 min-h-screen space-y-6">
      <header className="text-center space-y-2 mb-6">
        <h2 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400">
          News History
        </h2>
        <p className="text-md text-gray-600 dark:text-gray-300 max-w-lg mx-auto">
          All your recent browsing and verifications in one place.
        </p>
      </header>

      {loading ? (
        <p className="text-center text-gray-500">Loading history...</p>
      ) : history.length === 0 ? (
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-300">No history yet.</p>
        </div>
      ) : (
        <div className="space-y-4 max-w-4xl mx-auto">
          {history.map((item, idx) => (
            <div key={item.id} className="border border-gray-200/60 dark:border-gray-700/60 rounded-2xl p-5 bg-white/50 dark:bg-gray-800/30 backdrop-blur-md shadow-lg hover:shadow-xl transition-all fade-in-up" style={{ animationDelay: `${idx * 40}ms` }}>
              <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
                <span className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-200">
                  {item.action === "verified" ? "Verified" : "Browsed"}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">{new Date(item.created_at).toLocaleString()}</span>
              </div>
              <div className="font-bold text-lg mb-1">
                {item.url ? (
                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline text-blue-600 dark:text-blue-400">{item.title}</a>
                ) : (
                  item.title
                )}
              </div>
              {item.source && <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Source: {item.source}</div>}
              {item.summary && <div className="text-gray-700 dark:text-gray-300 text-sm">{item.summary}</div>}
              {item.category && <div className="mt-1 text-xs text-gray-400 dark:text-gray-500">Category: {item.category}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default History;
