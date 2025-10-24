import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useUserPrefs } from "../context/UserPrefsContext";

const Account = () => {
  const { userPrefs } = useUserPrefs();

  return (
    <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen space-y-6">
      <h1 className="text-3xl font-bold">Account</h1>

      <div className="grid gap-6 grid-cols-1 lg:grid-cols-2">
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-xl font-bold">TG</div>
            <div>
              <h2 className="text-xl font-semibold">Your Profile</h2>
              <p className="text-sm text-gray-600 dark:text-gray-300">You’re browsing as a guest. Use Login or Signup to personalize your experience.</p>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div>Preferred Language: <span className="font-medium">{userPrefs.preferredLanguage}</span></div>
            <div>Show Confidence: <span className="font-medium">{userPrefs.showConfidence ? "On" : "Off"}</span></div>
            <div>Default Region: <span className="font-medium">{(userPrefs.defaultRegion || 'IN').toUpperCase()}</span></div>
            <div>Default Model: <span className="font-medium">{(userPrefs.defaultModel || 'openai').toUpperCase()}</span></div>
          </div>
        </section>

        <section className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-100 dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-3">Authentication</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Link to="/login" className="px-4 py-3 text-center rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 shadow">Login</Link>
            <Link to="/signup" className="px-4 py-3 text-center rounded-lg bg-green-600 text-white font-semibold hover:bg-green-700 shadow">User Signup</Link>
            <Link to="/expert-signup" className="px-4 py-3 text-center rounded-lg bg-purple-600 text-white font-semibold hover:bg-purple-700 shadow">Expert Signup</Link>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Account;
