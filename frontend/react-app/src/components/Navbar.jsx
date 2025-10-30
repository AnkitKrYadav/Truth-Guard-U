import React from "react";
import { useTheme } from "../context/ThemeContext";
import { Moon, Sun, Shield } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar({ onToggleSidebar }) {
  const { theme, toggleTheme } = useTheme();
    const { user, isLoggedIn, logout } = useAuth();

  return (
    <nav className="flex items-center justify-between p-4 border-b border-gray-200/50 dark:border-gray-700/50 bg-white/60 dark:bg-gray-900/40 backdrop-blur-md shadow-sm">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="w-10 h-10 flex items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-blue-500 hover:brightness-110 text-white shadow-lg hover:shadow-xl transition-all duration-200"
          title="Toggle menu"
        >
          {/* TruthGuard logo mark (simple shield) */}
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M12 2l7 3v6c0 5-3.5 9.74-7 11-3.5-1.26-7-6-7-11V5l7-3z" />
          </svg>
        </button>
        <Link to="/" className="text-2xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-blue-400">TruthGuard</Link>
      </div>
      <div className="ml-auto flex items-center gap-3">
        <Link to="/admin" title="Admin" aria-label="Admin" className="w-10 h-10 flex items-center justify-center rounded-xl bg-white/80 dark:bg-gray-800/70 border border-gray-200/60 dark:border-gray-700/60 backdrop-blur-md hover:shadow-lg hover:bg-white dark:hover:bg-gray-800 transition-all duration-200">
          <Shield className="w-5 h-5 text-gray-700 dark:text-gray-200" />
        </Link>
        <button
          onClick={toggleTheme}
          className="p-2.5 rounded-xl bg-white/80 dark:bg-gray-800/70 border border-gray-200/60 dark:border-gray-700/60 backdrop-blur-md hover:shadow-lg hover:bg-white dark:hover:bg-gray-800 transition-all duration-200"
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {theme === "light" ? (
            <Moon size={18} className="text-gray-800" />
          ) : (
            <Sun size={18} className="text-yellow-400" />
          )}
        </button>
          {isLoggedIn ? (
            <div className="flex items-center gap-2">
              <Link to="/account" className="px-4 py-2 rounded-xl bg-white/80 dark:bg-gray-800/70 border border-gray-200/60 dark:border-gray-700/60 backdrop-blur-md text-sm font-medium hover:shadow-lg hover:bg-white dark:hover:bg-gray-800 transition-all duration-200">{user?.username || "Account"}</Link>
              <button onClick={logout} className="px-4 py-2 rounded-xl bg-gradient-to-r from-red-500 to-rose-600 text-white text-sm font-medium hover:brightness-110 shadow-md hover:shadow-lg transition-all duration-200">Logout</button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login" className="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-blue-500 text-white text-sm font-medium hover:brightness-110 shadow-md hover:shadow-lg transition-all duration-200">Login</Link>
              <Link to="/signup" className="px-4 py-2 rounded-xl bg-gradient-to-r from-gray-900 to-gray-800 text-white text-sm font-medium hover:brightness-110 shadow-md hover:shadow-lg transition-all duration-200">Sign up</Link>
            </div>
          )}
      </div>
    </nav>
  );
}

export default Navbar;
