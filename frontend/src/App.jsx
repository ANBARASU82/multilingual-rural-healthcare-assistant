import React, { useState } from "react";
import { Activity, Languages, MessageCircle, Stethoscope } from "lucide-react";

import Chatbot from "./components/Chatbot.jsx";
import LanguageSelector from "./components/LanguageSelector.jsx";
import DoctorDashboard from "./pages/DoctorDashboard.jsx";

export default function App() {
  const [language, setLanguage] = useState("en");
  const [view, setView] = useState("patient");

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Activity size={24} />
          </div>
          <div>
            <h1>Rural Health AI</h1>
            <p>Simple guidance from reports and symptoms</p>
          </div>
        </div>

        <nav className="nav-buttons" aria-label="Main view">
          <button className={view === "patient" ? "active" : ""} onClick={() => setView("patient")}>
            <MessageCircle size={18} />
            Patient
          </button>
          <button className={view === "doctor" ? "active" : ""} onClick={() => setView("doctor")}>
            <Stethoscope size={18} />
            Doctor
          </button>
        </nav>

        <div className="language-panel">
          <div className="panel-title">
            <Languages size={18} />
            Language
          </div>
          <LanguageSelector value={language} onChange={setLanguage} />
        </div>
      </aside>

      <section className="workspace">
        {view === "patient" ? (
          <Chatbot language={language} />
        ) : (
          <DoctorDashboard language={language} />
        )}
      </section>
    </main>
  );
}
