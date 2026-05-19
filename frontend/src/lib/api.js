import { API_BASE_URL } from "./config";

async function readJsonOrText(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return await response.json();
  const text = await response.text();
  return text ? { detail: text } : {};
}

export async function shortenUrl({ url, customAlias, expiresInDays }) {
  const body = {
    url,
    custom_alias: customAlias || null,
    expires_in_days: expiresInDays ? Number(expiresInDays) : null
  };

  const response = await fetch(`${API_BASE_URL}/shorten`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const payload = await readJsonOrText(response);
    throw new Error(payload?.detail || `Request failed (${response.status})`);
  }

  return await response.json();
}

export async function getStats(shortCode) {
  const code = String(shortCode || "").trim();
  if (!code) throw new Error("Short code is required");

  const response = await fetch(`${API_BASE_URL}/${encodeURIComponent(code)}/stats`);

  if (!response.ok) {
    const payload = await readJsonOrText(response);
    throw new Error(payload?.detail || `Request failed (${response.status})`);
  }

  return await response.json();
}

