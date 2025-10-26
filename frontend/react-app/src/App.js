import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Verify from "./pages/Verify";
import Trending from "./pages/Trending";
import History from "./pages/History";
import Settings from "./pages/Settings";
import About from "./pages/About";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ExpertSignup from "./pages/ExpertSignup";
import AdminDashboard from "./pages/AdminDashboard";
import Account from "./pages/Account";

import { ThemeProvider } from "./context/ThemeContext";
import { UserPrefsProvider } from "./context/UserPrefsContext";
import "./index.css";

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const toggleSidebar = () => setSidebarCollapsed((s) => !s);
  return (
    <ThemeProvider>
      <UserPrefsProvider>
        <Router>
          <div className="p-6 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex h-screen">
            <Sidebar collapsed={sidebarCollapsed} />
            <div className="flex flex-col flex-grow">
              <Navbar onToggleSidebar={toggleSidebar} />
              <main className="flex-grow overflow-y-auto">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/verify" element={<Verify />} />
                  <Route path="/trending" element={<Trending />} />
                  <Route path="/history" element={<History />} />
                  <Route path="/settings" element={<Settings />} />
                  <Route path="/account" element={<Account />} />
                  <Route path="/admin" element={<AdminDashboard />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/signup" element={<Signup />} />
                  <Route path="/expert-signup" element={<ExpertSignup />} />
                  <Route path="/about" element={<About />} />
                </Routes>
              </main>
            </div>
          </div>
        </Router>
      </UserPrefsProvider>
    </ThemeProvider>
  );
}

export default App;
