const API_URL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.hostname}:5000`;

async function postJson(path, payload) {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

export function predictDisease(text) {
  return postJson("/predict", { text });
}

export function simplifyReport(text, target_language) {
  return postJson("/simplify", { text, target_language });
}

export function translateText(text, target_language) {
  return postJson("/translate", { text, target_language });
}

export async function processReportImage(file, targetLanguage) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_language", targetLanguage);

  const response = await fetch(`${API_URL}/report-image`, {
    method: "POST",
    body: formData,
  });

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : { error: await response.text() };
  if (!response.ok) throw new Error(data.error || "Image processing failed");
  return data;
}

export async function playVoice(text, language) {
  const response = await fetch(`${API_URL}/voice`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
  });
  if (!response.ok) throw new Error("Voice generation failed");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  new Audio(url).play();
}
