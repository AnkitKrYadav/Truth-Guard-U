import React from "react";
import { Link } from "react-router-dom";
import { useUserPrefs } from "../context/UserPrefsContext";
import { useAuth } from "../context/AuthContext";

const Account = () => {
  const { userPrefs } = useUserPrefs();
  const { user, isLoggedIn, isExpert, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900 px-6 py-10 text-slate-900 dark:text-slate-100">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold tracking-tight">Your Account</h1>
          <p className="text-slate-600 dark:text-slate-300 mt-2">Manage your profile, preferences, and access tools to personalize TruthGuard.</p>
        </div>

        {/* Profile Card */}
        <section className="relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 backdrop-blur shadow-sm">
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 via-blue-500/10 to-cyan-500/10 pointer-events-none"/>
          <div className="relative p-6 sm:p-8 flex flex-col sm:flex-row items-start sm:items-center gap-6">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 text-white flex items-center justify-center text-2xl font-bold shadow-lg">
              {isLoggedIn ? (user?.username?.slice(0,2) || 'TG').toUpperCase() : 'TG'}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold">{isLoggedIn ? (user?.username || 'User') : 'Guest'}</h2>
              <p className="text-sm text-slate-600 dark:text-slate-300">{isLoggedIn ? `Signed in as ${user?.role || 'user'}.` : 'Sign in to sync your preferences across devices and access expert features.'}</p>
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div>Preferred Language: <span className="font-medium">{userPrefs.preferredLanguage}</span></div>
                <div>Show Confidence: <span className="font-medium">{userPrefs.showConfidence ? "On" : "Off"}</span></div>
                <div>Default Region: <span className="font-medium">{(userPrefs.defaultRegion || 'IN').toUpperCase()}</span></div>
                <div>Default Model: <span className="font-medium">{(userPrefs.defaultModel || 'openai').toUpperCase()}</span></div>
              </div>
            </div>
            <div className="flex gap-3">
              {isLoggedIn ? (
                <button onClick={logout} className="px-4 py-2 rounded-lg bg-red-600 text-white font-semibold hover:bg-red-700 shadow">Logout</button>
              ) : (
                <>
                  <Link to="/login" className="px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 shadow">Login</Link>
                  <Link to="/signup" className="px-4 py-2 rounded-lg bg-slate-900 text-white font-semibold hover:bg-slate-800 shadow">Sign Up</Link>
                </>
              )}
            </div>
          </div>
        </section>

        {/* Quick Actions & Preferences */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          <section className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 backdrop-blur p-6 shadow-sm">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 gap-3">
              {!isExpert && (
                <Link to="/expert-signup" className="px-4 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-fuchsia-600 text-white font-semibold hover:brightness-110 shadow">Expert Signup</Link>
              )}
              <Link to="/verify" className="px-4 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold hover:brightness-110 shadow">Verify a Claim</Link>
              <Link to="/history" className="px-4 py-3 rounded-xl bg-gradient-to-r from-sky-600 to-blue-600 text-white font-semibold hover:brightness-110 shadow">View History</Link>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/60 backdrop-blur p-6 shadow-sm lg:col-span-2">
            <h3 className="text-lg font-semibold mb-4">Preferences</h3>
            <div className="grid sm:grid-cols-2 gap-4 text-sm">
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70">
                <p className="text-slate-500">Default Region</p>
                <p className="text-lg font-semibold">{(userPrefs.defaultRegion || 'IN').toUpperCase()}</p>
              </div>
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70">
                <p className="text-slate-500">Default Model</p>
                <p className="text-lg font-semibold">{(userPrefs.defaultModel || 'openai').toUpperCase()}</p>
              </div>
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70">
                <p className="text-slate-500">Confidence Badges</p>
                <p className="text-lg font-semibold">{userPrefs.showConfidence ? "Enabled" : "Hidden"}</p>
              </div>
              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/70">
                <p className="text-slate-500">Language</p>
                <p className="text-lg font-semibold">{userPrefs.preferredLanguage}</p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Account;
