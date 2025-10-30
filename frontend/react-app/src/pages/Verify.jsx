import React, { useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";
import { useToast } from "../context/ToastContext";

function Verify() {
  const [claim, setClaim] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("gemini");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!claim.trim()) {
      toast({ message: "Please enter a claim", type: "warning" });
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const base = API_BASE_URL || "";
      console.log("Using API base:", base);

      const res = await axios.post(
        `${base}/api/verify`,
        { claim, agent: selectedAgent },
        { headers: { "Content-Type": "application/json" } }
      );

      setResult(res.data);
      toast({ message: "Verification complete", type: "success", timeout: 1500 });
    } catch (err) {
      console.error(err);
      // Check if it's a rate limit error (429)
      if (err.response && err.response.status === 429) {
        setResult({ error: "Please use another model." });
        toast({ title: "Rate limited", message: "Try another model", type: "warning" });
      } else {
        setResult({ error: "Error verifying claim." });
        toast({ title: "Verification failed", message: err.message || "Unknown error", type: "error" });
      }
    } finally {
      setLoading(false);
    }
  };

  const getBadgeColor = (status) => {
    if (status === "True") return "bg-green-200 text-green-800";
    if (status === "False") return "bg-red-200 text-red-800";
    return "bg-yellow-200 text-yellow-800";
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 70) return "bg-green-500";
    if (confidence >= 40) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getAgentColor = (agent) => {
    if (agent === "openai") return "bg-blue-100 text-blue-800";
    if (agent === "hf") return "bg-purple-100 text-purple-800";
    if (agent === "gemini") return "bg-green-100 text-green-800";
    if (agent === "llama") return "bg-orange-100 text-orange-800";
    return "bg-gray-100 text-gray-800";
  };

  return (
    <div className="p-8 bg-transparent text-gray-900 dark:text-gray-100 min-h-screen space-y-6">
      <header className="text-center space-y-2 mb-6">
        <h2 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400">
          Verify News
        </h2>
        <p className="text-md text-gray-600 dark:text-gray-300 max-w-lg mx-auto">
          Enter a claim and select an AI model to fact-check instantly.
        </p>
      </header>

      {/* Input Section */}
      <form
        onSubmit={handleSubmit}
        className="flex flex-col sm:flex-row gap-3 mb-6 items-center max-w-3xl mx-auto"
      >
        <input
          type="text"
          value={claim}
          onChange={(e) => setClaim(e.target.value)}
          placeholder="Enter news or claim to verify..."
          className="flex-grow p-3 border border-gray-300/60 dark:border-gray-700/60 rounded-xl bg-white/60 dark:bg-gray-800/40 backdrop-blur-md shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        />

        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="p-3 border border-gray-300/60 dark:border-gray-700/60 rounded-xl bg-white/60 dark:bg-gray-800/40 backdrop-blur-md shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        >
          <option value="openai">TruthGPT (OpenAI)</option>
          <option value="hf">DeepFact (HuggingFace)</option>
          <option value="gemini">GeminiGuard (Google)</option>
        </select>

        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white font-semibold rounded-xl hover:brightness-110 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Verifying..." : "Verify"}
        </button>
      </form>

      {/* Result Card */}
      {result && (
        <div className="p-6 border border-gray-200/60 dark:border-gray-700/60 rounded-2xl shadow-xl backdrop-blur-md bg-white/50 dark:bg-gray-800/30 text-gray-900 dark:text-gray-100 max-w-3xl mx-auto">
          {result.error ? (
            <p className="text-red-500">{result.error}</p>
          ) : (
            <>
              <div className="flex items-center gap-3 mb-3 flex-wrap">
                <p className="font-medium text-lg">
                  Claim: <span className="font-semibold">{claim}</span>
                </p>
                {result.agent && (
                  <span
                    className={`px-3 py-1 text-xs font-semibold rounded-full ${getAgentColor(
                      result.agent
                    )}`}
                  >
                    Verified by {result.agent}
                  </span>
                )}
              </div>

              <span
                className={`inline-block px-3 py-1 text-sm font-semibold rounded-full ${getBadgeColor(
                  result.status
                )}`}
              >
                {result.status}
              </span>

              <p className="mt-3 text-gray-700 dark:text-gray-300">
                {result.summary}
              </p>

              {/* Confidence Score */}
              {result.confidence !== undefined && (
                <div className="mt-4">
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                    Confidence Score:{" "}
                    <span className="font-semibold">{result.confidence}%</span>
                  </p>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-3 rounded-full transition-all duration-500 ${getConfidenceColor(
                        result.confidence
                      )}`}
                      style={{ width: `${result.confidence}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Sources */}
              {result.sources && result.sources.length > 0 && (
                <p className="mt-4 text-sm text-gray-600 dark:text-gray-300">
                  <span className="font-medium">Sources:</span>{" "}
                  {result.sources.join(", ")}
                </p>
              )}

              {/* Fallback Indicator */}
              {result.agent && result.agent !== selectedAgent && (
                <p className="mt-2 text-xs text-yellow-600 dark:text-yellow-400 font-semibold">
                  Fallback agent was used instead of your selection.
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default Verify;
