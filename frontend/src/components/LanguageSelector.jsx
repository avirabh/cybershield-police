import React from "react";
import { Languages } from "lucide-react";
import { useLanguage } from "../i18n/LanguageContext.jsx";

export default function LanguageSelector({ compact = false }) {
  const { language, setLanguage, languages, t } = useLanguage();

  return (
    <label className={`language-selector ${compact ? "language-selector-compact" : ""}`}>
      <span>
        <Languages size={15} />
        {!compact && t("common.language")}
      </span>
      <select value={language} onChange={(event) => setLanguage(event.target.value)}>
        {languages.map((item) => (
          <option key={item.code} value={item.code}>
            {compact ? item.code.toUpperCase() : item.nativeLabel}
          </option>
        ))}
      </select>
    </label>
  );
}
