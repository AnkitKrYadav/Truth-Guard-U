import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";

function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/history`);
        setHistory(res.data || []);
      } catch (err) {
        setHistory([]);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
      <h2 className="text-2xl font-semibold mb-4">News Browsing & Verification History</h2>
      {loading ? (
        <p>Loading history...</p>
      ) : history.length === 0 ? (
        <p className="text-gray-600 dark:text-gray-300">No history yet.</p>
      ) : (
        <div className="space-y-4">
          {history.map((item) => (
            <div key={item.id} className="border rounded-lg p-4 bg-white dark:bg-gray-800 shadow">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                  {item.action === "verified" ? "Verified" : "Browsed"}
                </span>
                <span className="text-xs text-gray-500">{new Date(item.created_at).toLocaleString()}</span>
              </div>
              <div className="font-bold text-lg mb-1">
                {item.url ? (
                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="hover:underline">{item.title}</a>
                ) : (
                  item.title
                )}
              </div>
              {item.source && <div className="text-sm text-gray-500 mb-1">Source: {item.source}</div>}
              {item.summary && <div className="text-gray-700 dark:text-gray-300 text-sm">{item.summary}</div>}
              {item.category && <div className="mt-1 text-xs text-gray-400">Category: {item.category}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default History;
