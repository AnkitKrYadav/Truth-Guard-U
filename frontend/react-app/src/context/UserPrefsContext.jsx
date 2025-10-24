import React, { createContext, useContext, useEffect, useState } from "react";

const UserPrefsContext = createContext();

export const UserPrefsProvider = ({ children }) => {
  const [userPrefs, setUserPrefs] = useState(() => {
    try {
      const saved = localStorage.getItem("tg_user_prefs");
      return saved ? JSON.parse(saved) : {
        preferredLanguage: "English",
        showConfidence: true,
        defaultRegion: "in",
        defaultModel: "openai",
        compactCards: false,
      };
    } catch {
      return {
        preferredLanguage: "English",
        showConfidence: true,
        defaultRegion: "in",
        defaultModel: "openai",
        compactCards: false,
      };
    }
  });

  useEffect(() => {
    try { localStorage.setItem("tg_user_prefs", JSON.stringify(userPrefs)); } catch {}
  }, [userPrefs]);

  const updatePrefs = (prefs) =>
    setUserPrefs((prev) => ({ ...prev, ...prefs }));

  return (
    <UserPrefsContext.Provider value={{ userPrefs, updatePrefs }}>
      {children}
    </UserPrefsContext.Provider>
  );
};

export const useUserPrefs = () => useContext(UserPrefsContext);
