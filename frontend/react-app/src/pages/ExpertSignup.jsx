import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";

const ExpertSignup = ({ onSignup }) => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [organization, setOrganization] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await axios.post(`${API_BASE_URL}/api/auth/expert-signup`, {
        username,
        email,
        password,
        full_name: fullName,
        organization,
      });
      if (onSignup) onSignup(res.data);
    } catch (err) {
      setError(err.response?.data?.error || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-16 p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Expert Signup</h2>
        <button onClick={() => navigate(-1)} className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700 hover:opacity-80" title="Back">
          <ArrowLeft className="w-5 h-5 text-gray-800 dark:text-gray-200" />
        </button>
      </div>
      <form onSubmit={handleSignup} className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          className="w-full px-3 py-2 border rounded bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          className="w-full px-3 py-2 border rounded bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full px-3 py-2 border rounded bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
          required
        />
        <input
          type="text"
          placeholder="Full Name"
          value={fullName}
          onChange={e => setFullName(e.target.value)}
          className="w-full px-3 py-2 border rounded bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
          required
        />
        <input
          type="text"
          placeholder="Organization (optional)"
          value={organization}
          onChange={e => setOrganization(e.target.value)}
          className="w-full px-3 py-2 border rounded bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100"
        />
        {error && <div className="text-red-500 dark:text-red-400 text-sm">{error}</div>}
        <button
          type="submit"
          className="w-full py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition shadow"
          disabled={loading}
        >
          {loading ? "Signing up..." : "Signup as Expert"}
        </button>
      </form>
    </div>
  );
};

export default ExpertSignup;
