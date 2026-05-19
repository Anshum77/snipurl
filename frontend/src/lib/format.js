export function formatDateTime(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleString();
}

export function formatUrl(value) {
  return value || "—";
}

export function getShortCodeFromInput(input) {
  const raw = String(input || "").trim();
  if (!raw) return "";
  try {
    const url = new URL(raw);
    const path = url.pathname.replace(/^\/+/, "");
    return path.split("/")[0] || "";
  } catch {
    return raw.replace(/^\/+/, "").split("/")[0] || "";
  }
}

