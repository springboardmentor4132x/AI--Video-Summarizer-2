"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  function upload(e) {
    e.preventDefault();
    if (!file) return setMessage("Please select a video file.");
    const allowed = ["video/mp4", "video/webm", "video/quicktime", "video/x-matroska"];
    if (!allowed.includes(file.type)) return setMessage("Invalid video format. Use MP4, WebM, MOV or MKV.");

    const max = 500 * 1024 * 1024;
    if (file.size > max) return setMessage("File is too large. Maximum size is 500 MB.");

    const videos = JSON.parse(localStorage.getItem("clipmind_videos") || "[]");
    videos.push({
      id: Date.now(),
      filename: file.name,
      size: file.size,
      status: "Processing",
      uploadedAt: new Date().toLocaleString()
    });
    localStorage.setItem("clipmind_videos", JSON.stringify(videos));
    setMessage("Video validated and added to the processing queue.");
    setTimeout(() => router.push("/history"), 800);
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
        <p className="muted">Select a video. The frontend validates the file before sending it to the FastAPI upload endpoint.</p>

        <form className="upload-card" onSubmit={upload}>
          <div className="dropzone">
            <div className="upload-icon">↑</div>
            <h2>Choose a video file</h2>
            <p>MP4, WebM, MOV or MKV · Max 500 MB</p>
            <input type="file" accept="video/*" onChange={e => setFile(e.target.files[0])} />
            {file && <strong>{file.name}</strong>}
          </div>
          {message && <div className={message.includes("added") ? "success" : "error"}>{message}</div>}
          <button className="btn primary full">Validate & Upload</button>
        </form>
      </section>
    </main>
  );
}