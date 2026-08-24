"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function upload(e) {
    e.preventDefault();
    setMessage("");

    if (!file) return setMessage("Please select a video file.");
    
    const allowed = [".mp4", ".avi", ".mov", ".mkv", ".webm"];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    if (!allowed.includes(ext)) {
      return setMessage("Invalid video format. Use MP4, WebM, MOV, AVI, or MKV.");
    }

    const token = localStorage.getItem("clipmind_token");
    if (!token) {
      setMessage("You must be logged in to upload videos.");
      return router.push("/login");
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/videos/upload", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Video upload failed.");
      }

      setMessage("Video uploaded successfully and saved to PostgreSQL!");
      setTimeout(() => router.push("/history"), 1000);
    } catch (err) {
      setMessage(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">ClipMind <span>AI</span></div>
        <nav>
          <Link href="/dashboard">Dashboard</Link>
          <Link className="active" href="/upload">Upload Video</Link>
          <Link href="/history">Upload History</Link>
        </nav>
      </aside>
      <section className="content narrow">
        <p className="eyebrow">VIDEO MANAGEMENT</p>
        <h1>Upload Video</h1>
        <p className="muted">Upload your video to store metadata in PostgreSQL and save the file for AI processing.</p>

        <form className="upload-card" onSubmit={upload}>
          <div className="dropzone">
            <div className="upload-icon">↑</div>
            <h2>Choose a video file</h2>
            <p>MP4, WebM, MOV, AVI or MKV</p>
            <input type="file" accept="video/*" onChange={e => setFile(e.target.files[0])} />
            {file && <strong>{file.name}</strong>}
          </div>
          {message && (
            <div className={message.includes("successfully") ? "success" : "error"}>
              {message}
            </div>
          )}
          <button className="btn primary full" disabled={loading}>
            {loading ? "Uploading..." : "Validate & Upload"}
          </button>
        </form>
      </section>
    </main>
  );
}