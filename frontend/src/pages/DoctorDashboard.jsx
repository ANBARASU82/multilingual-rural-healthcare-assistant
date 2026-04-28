import React, { useState } from "react";
import { ClipboardCheck, Languages, Search } from "lucide-react";

import { predictDisease, simplifyReport } from "../api.js";

export default function DoctorDashboard({ language }) {
  const [symptoms, setSymptoms] = useState("");
  const [report, setReport] = useState("");
  const [diagnosis, setDiagnosis] = useState(null);
  const [simplified, setSimplified] = useState("");
  const [loading, setLoading] = useState(false);

  async function handlePredict() {
    if (!symptoms.trim()) return;
    setLoading(true);
    try {
      setDiagnosis(await predictDisease(symptoms));
    } finally {
      setLoading(false);
    }
  }

  async function handleSimplify() {
    if (!report.trim()) return;
    setLoading(true);
    try {
      const result = await simplifyReport(report, language);
      setSimplified(result.translated || result.simplified);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="dashboard">
      <header className="page-header">
        <h2>Doctor Dashboard</h2>
        <p>Enter symptoms, review likely diagnosis, and simplify instructions for the selected language.</p>
      </header>

      <section className="dashboard-grid">
        <div className="panel">
          <div className="panel-title">
            <Search size={18} />
            Symptom Diagnosis
          </div>
          <textarea value={symptoms} onChange={(event) => setSymptoms(event.target.value)} placeholder="fever, cough, body pain" />
          <button className="primary-button" onClick={handlePredict} disabled={loading || !symptoms.trim()}>
            <ClipboardCheck size={18} />
            Predict Disease
          </button>

          {diagnosis && (
            <div className="result-box">
              <span>Likely disease</span>
              <strong>{diagnosis.disease}</strong>
              <small>Confidence: {(diagnosis.confidence * 100).toFixed(1)}% | {diagnosis.model}</small>
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-title">
            <Languages size={18} />
            Report Simplifier
          </div>
          <textarea value={report} onChange={(event) => setReport(event.target.value)} placeholder="Paste diagnosis, medicines, and dosage instructions..." />
          <button className="primary-button" onClick={handleSimplify} disabled={loading || !report.trim()}>
            Simplify Report
          </button>
          {simplified && <div className="result-box readable">{simplified}</div>}
        </div>
      </section>
    </div>
  );
}
