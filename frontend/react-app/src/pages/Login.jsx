import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const { login } = useAuth();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    // Mock client-side login; integrate API later
    setTimeout(() => {
      login({ username, role: "user" });
      navigate("/account");
    }, 300);
  };

  return (
    <div className="max-w-md mx-auto mt-16 p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">User Login</h2>
        <button onClick={() => navigate(-1)} className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-200 dark:bg-gray-700 hover:opacity-80" title="Back">
          <ArrowLeft className="w-5 h-5 text-gray-800 dark:text-gray-200" />
        </button>
      </div>
      <form onSubmit={handleLogin} className="space-y-4">
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
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
        {error && <div className="text-red-500 dark:text-red-400 text-sm">{error}</div>}
        <button
          type="submit"
          className="w-full py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition shadow"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600 dark:text-gray-300">Don't have an account? <a href="/signup" className="text-blue-600 hover:underline">Sign up</a></p>
    </div>
  );
};

export default Login;
