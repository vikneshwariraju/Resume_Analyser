// All backend calls live here, so the components never deal with URLs or fetch details.
const BASE = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request(path, options) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, options);
  } catch {
    throw new Error("Cannot reach the server. Check that the backend is running, then try again.");
  }
  let body = null;
  try {
    body = await res.json();
  } catch {
    /* non-JSON response */
  }
  if (!res.ok) {
    const detail = body && body.detail;
    throw new Error(typeof detail === "string" ? detail : "Something went wrong. Please try again.");
  }
  return body;
}

export const getOptions = () => request("/api/options");
export const getSamples = () => request("/api/samples");

export function analyze({ file, sample, style, level, focus }) {
  const form = new FormData();
  if (file) form.append("file", file);
  else if (sample) form.append("sample", sample);
  form.append("style", style);
  form.append("level", level);
  if (focus.length) form.append("focus", focus.join(","));
  return request("/api/analyze", { method: "POST", body: form });
}
