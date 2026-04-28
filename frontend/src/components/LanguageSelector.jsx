import React from "react";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ta", label: "Tamil" },
];

export default function LanguageSelector({ value, onChange }) {
  return (
    <select value={value} onChange={(event) => onChange(event.target.value)} aria-label="Select language">
      {LANGUAGES.map((language) => (
        <option key={language.code} value={language.code}>
          {language.label}
        </option>
      ))}
    </select>
  );
}
