import React from "react";
import { useTheme } from "../context/ThemeContext";
import { Moon, Sun, Shield } from "lucide-react";
import { Link } from "react-router-dom";

function Navbar({ onToggleSidebar }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="flex items-center justify-between p-4 border-b dark:border-gray-700 bg-white dark:bg-gray-900">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="w-9 h-9 flex items-center justify-center rounded-full bg-blue-600 hover:bg-blue-700 text-white shadow"
          title="Toggle menu"
        >
          {/* TruthGuard logo mark (simple shield) */}
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path d="M12 2l7 3v6c0 5-3.5 9.74-7 11-3.5-1.26-7-6-7-11V5l7-3z" />
          </svg>
        </button>
        <Link to="/" className="text-xl font-bold text-gray-800 dark:text-gray-100">TruthGuard</Link>
      </div>
      <div className="ml-auto flex items-center gap-3">
        <Link to="/admin" title="Admin" aria-label="Admin" className="w-9 h-9 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800 hover:opacity-80">
          <Shield className="w-5 h-5 text-gray-700 dark:text-gray-200" />
        </Link>
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:opacity-80 transition"
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
        >
          {theme === "light" ? (
            <Moon size={18} className="text-gray-800" />
          ) : (
            <Sun size={18} className="text-yellow-400" />
          )}
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
