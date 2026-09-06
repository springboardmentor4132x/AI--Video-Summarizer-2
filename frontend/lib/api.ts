export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type UserRole = "content_creator" | "learner" | "educator" | "administrator";

export type User = {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  bio: string | null;
  is_active: boolean;
};

export type VideoStatus = "uploaded" | "processing" | "ready" | "failed";

export type VideoItem = {
  id: string;
  owner_id: string;
  owner_name: string | null;
  original_filename: string;
  title: string;
  description: string | null;
  status: VideoStatus;
  is_public: boolean;
  duration: number | null;
  width: number | null;
  height: number | null;
  file_size: number | null;
  error_message: string | null;
  has_thumbnail: boolean;
  has_audio: boolean;
  created_at: string;
};

export type JobItem = {
  id: string;
  video_id: string;
  job_type: string;
  status: string;
  progress: number;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type ContentStatus = "not_started" | "processing" | "completed" | "failed";
export type TranscriptItem = {
  id: string; video_id: string; status: ContentStatus; language: string | null;
  full_text: string | null; edited_text: string | null; error_message: string | null;
  created_at: string; updated_at: string;
};
export type SummaryItem = {
  id: string; video_id: string; status: ContentStatus; short_text: string | null;
  detailed_text: string | null; keywords: string[]; error_message: string | null;
  created_at: string; updated_at: string;
};
export type TopicItem = { id: string; video_id: string; start_sec: number; end_sec: number; title: string; transcript_text: string; created_at: string };
export type KeyMomentItem = { id: string; video_id: string; topic_id: string | null; start_sec: number; end_sec: number; title: string; transcript_text: string | null; score: number | null; moment_type: string; created_at: string };
export type AnalysisItem = { topics: TopicItem[]; key_moments: KeyMomentItem[] };

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("clipmind_token");
}

export function setToken(token: string) {
  localStorage.setItem("clipmind_token", token);
}

export function clearToken() {
  localStorage.removeItem("clipmind_token");
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      detail = data.detail || detail;
      if (Array.isArray(data.detail)) {
        detail = data.detail.map((d: { msg?: string }) => d.msg).join(", ");
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  register: (body: { email: string; password: string; full_name: string; role: UserRole }) =>
    request<{ access_token: string }>("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body: { email: string; password: string }) =>
    request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: () => request<User>("/users/me"),
  updateMe: (body: { full_name?: string; bio?: string }) =>
    request<User>("/users/me", { method: "PATCH", body: JSON.stringify(body) }),
  users: () => request<User[]>("/users"),
  videos: () => request<VideoItem[]>("/videos"),
  video: (id: string) => request<VideoItem>(`/videos/${id}`),
  updateVideo: (id: string, body: Partial<Pick<VideoItem, "title" | "description" | "is_public">>) =>
    request<VideoItem>(`/videos/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  processVideo: (id: string) => request<JobItem>(`/videos/${id}/process`, { method: "POST" }),
  jobs: (id: string) => request<JobItem[]>(`/videos/${id}/jobs`),
  job: (id: string) => request<JobItem>(`/jobs/${id}`),
  transcript: (id: string) => request<TranscriptItem>(`/videos/${id}/transcript`),
  updateTranscript: (id: string, text: string) => request<TranscriptItem>(`/videos/${id}/transcript`, { method: "PATCH", body: JSON.stringify({ text }) }),
  summary: (id: string) => request<SummaryItem>(`/videos/${id}/summary`),
  generateSummary: (id: string) => request<JobItem>(`/videos/${id}/summary`, { method: "POST" }),
  analysis: (id: string) => request<AnalysisItem>(`/videos/${id}/analysis`),
  rerunAnalysis: (id: string) => request<JobItem>(`/videos/${id}/analysis`, { method: "POST" }),
  health: () => request<{ status: string }>("/health"),
};

export function mediaUrl(videoId: string, kind: "stream" | "thumbnail") {
  const token = getToken() || "";
  return `${API_URL}/videos/${videoId}/${kind}?token=${encodeURIComponent(token)}`;
}

export async function uploadVideo(file: File, title: string, description: string, onProgress?: (pct: number) => void) {
  const token = getToken();
  const form = new FormData();
  form.append("file", file);
  if (title) form.append("title", title);
  if (description) form.append("description", description);

  return new Promise<VideoItem>((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}/videos/upload`);
    if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable && onProgress) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try {
          const data = JSON.parse(xhr.responseText);
          const detail = Array.isArray(data.detail)
            ? data.detail.map((d: { msg?: string }) => d.msg).join(", ")
            : data.detail;
          reject(new Error(detail || `Upload failed (${xhr.status})`));
        } catch {
          reject(new Error(`Upload failed (${xhr.status})`));
        }
      }
    };
    xhr.onerror = () => reject(new Error("Network error during upload. Check that the API is running on port 8000."));
    xhr.ontimeout = () => reject(new Error("Upload timed out. Try a smaller file."));
    xhr.timeout = 10 * 60 * 1000;
    xhr.send(form);
  });
}
