import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

const AuthContext = createContext(null);

const LS_KEY = "tg_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (raw) setUser(JSON.parse(raw));
    } catch {}
  }, []);

  const login = (info) => {
    const u = info || { username: "guest", role: "user" };
    setUser(u);
    try { localStorage.setItem(LS_KEY, JSON.stringify(u)); } catch {}
  };

  const logout = () => {
    setUser(null);
    try { localStorage.removeItem(LS_KEY); } catch {}
  };

  const setRole = (role) => {
    if (!user) return;
    const next = { ...user, role };
    setUser(next);
    try { localStorage.setItem(LS_KEY, JSON.stringify(next)); } catch {}
  };

  const value = useMemo(() => ({
    user, login, logout, setRole,
    isLoggedIn: !!user,
    isExpert: user?.role === "expert" || user?.role === "admin",
    isAdmin: user?.role === "admin",
  }), [user]);

  return (
    <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext) || { user: null };
}
