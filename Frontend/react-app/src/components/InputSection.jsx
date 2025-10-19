import React, { useState } from "react";
import { Search } from "lucide-react";

function InputSection() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleVerify = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ claim: query }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Failed to verify claim. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-md flex items-center gap-3 text-gray-900 dark:text-gray-100">
        <Search className="w-6 h-6 text-gray-500 dark:text-gray-300" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Paste a news headline, link, or claim..."
          className="flex-grow focus:outline-none bg-transparent text-gray-800 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-100"
        />
        <button
          onClick={handleVerify}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg transition"
        >
          {loading ? "Verifying..." : "Verify"}
        </button>
      </div>

      {error && (
        <div className="text-red-500 font-semibold">{error}</div>
      )}

      {result && (
        <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-xl shadow-inner">
          <p>
            <strong>Claim:</strong> {result.claim}
          </p>
          <p>
            <strong>Status:</strong>{" "}
            <span
              className={
                result.status === "True"
                  ? "text-green-600"
                  : result.status === "False"
                  ? "text-red-600"
                  : "text-yellow-600"
              }
            >
              {result.status}
            </span>
          </p>
          <p>
            <strong>Summary:</strong> {result.summary}
          </p>
          {result.sources && result.sources.length > 0 && (
            <p>
              <strong>Sources:</strong> {result.sources.join(", ")}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default InputSection;
