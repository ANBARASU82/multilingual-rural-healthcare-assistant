import React, { useState } from "react";
import { FileImage, Send, Volume2 } from "lucide-react";

import { playVoice, processReportImage, simplifyReport } from "../api.js";

export default function Chatbot({ language }) {
  const [report, setReport] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Paste a medical report or upload a report image. I will simplify it and translate it." },
  ]);
  const [loading, setLoading] = useState(false);
  const [latestOutput, setLatestOutput] = useState("");

  async function handleSimplify() {
    if (!report.trim()) return;
    setLoading(true);
    setMessages((items) => [...items, { role: "user", text: report }]);

    try {
      const result = await simplifyReport(report, language);
      const output = result.translated || result.simplified;
      setLatestOutput(output);
      setMessages((items) => [...items, { role: "assistant", text: output }]);
      setReport("");
    } catch (error) {
      setMessages((items) => [...items, { role: "assistant", text: error.message }]);
    } finally {
      setLoading(false);
    }
  }

  async function handleImage(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setMessages((items) => [...items, { role: "user", text: `Uploaded report image: ${file.name}` }]);

    try {
      const result = await processReportImage(file, language);
      const output = result.translated || result.simplified;
      setLatestOutput(output);
      setMessages((items) => [...items, { role: "assistant", text: output }]);
    } catch (error) {
      setMessages((items) => [...items, { role: "assistant", text: error.message }]);
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  }

  return (
    <div className="chat-layout">
      <header className="page-header">
        <h2>Patient Chatbot</h2>
        <p>Converts report text or report images into simple regional-language instructions.</p>
      </header>

      <div className="chat-window" aria-live="polite">
        {messages.map((message, index) => (
          <div key={`${message.role}-${index}`} className={`message ${message.role}`}>
            {message.text}
          </div>
        ))}
        {loading && <div className="message assistant">Processing...</div>}
      </div>

      <div className="composer">
        <textarea
          value={report}
          onChange={(event) => setReport(event.target.value)}
          placeholder="Paste medical report text here..."
        />
        <div className="composer-actions">
          <label className="icon-button" title="Upload report image">
            <FileImage size={20} />
            <input type="file" accept="image/*" onChange={handleImage} />
          </label>
          <button className="icon-button" onClick={() => latestOutput && playVoice(latestOutput, language)} title="Play voice">
            <Volume2 size={20} />
          </button>
          <button className="primary-button" onClick={handleSimplify} disabled={loading || !report.trim()}>
            <Send size={18} />
            Simplify Report
          </button>
        </div>
      </div>
    </div>
  );
}
