import React, { createContext, useContext, useMemo, useState } from "react";
import { getTranslation, languages } from "./translations.js";

const STORAGE_KEY = "cybershield_language";
const LanguageContext = createContext(null);

function getInitialLanguage() {
  const stored = localStorage.getItem(STORAGE_KEY);
  return languages.some((language) => language.code === stored) ? stored : "en";
}

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(getInitialLanguage);

  function setLanguage(nextLanguage) {
    const safeLanguage = languages.some((item) => item.code === nextLanguage) ? nextLanguage : "en";
    localStorage.setItem(STORAGE_KEY, safeLanguage);
    setLanguageState(safeLanguage);
  }

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      languages,
      t: (key) => getTranslation(language, key),
    }),
    [language],
  );

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}
