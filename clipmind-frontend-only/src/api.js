/**
 * api.js
 * ------
 * Backend ke saath saari communication yahan se hoti hai.
 * Token localStorage mein store hota hai aur har protected
 * request ke saath Authorization header mein bheja jaata hai.
 */

const BASE_URL = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("clipmind_token");
}

async function request(path, { method = "GET", body, isFormData = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!isFormData) headers["Content-Type"] = "application/json";

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: isFormData ? body : body ? JSON.stringify(body) : undefined,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong. Please try again.");
  }
  return data;
}

export const api = {
  register: (payload) => request("/api/auth/register", { method: "POST", body: payload }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: payload }),
  me: () => request("/api/auth/me"),
  dashboard: () => request("/api/dashboard/"),
  uploadVideo: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/api/videos/upload", { method: "POST", body: formData, isFormData: true });
  },
  
  history: () => request("/api/videos/history"),
  videoStatus: (id) => request(`/api/videos/${id}/status`),

  // Module 2 - Transcript
  generateTranscript: (videoId) =>
    request(`/api/videos/${videoId}/transcript/generate`, { method: "POST" }),
  getTranscript: (videoId) => request(`/api/videos/${videoId}/transcript`),

  // Module 2 - Summary
  generateSummary: (videoId) =>
    request(`/api/videos/${videoId}/summary/generate`, { method: "POST" }),
  getSummary: (videoId) => request(`/api/videos/${videoId}/summary`),

  saveToken: (token) => localStorage.setItem("clipmind_token", token),
  logout: () => localStorage.removeItem("clipmind_token"),
  isLoggedIn: () => !!getToken(),
};
