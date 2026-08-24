"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function HistoryPage() {
  const [videos, setVideos] = useState([]);
  useEffect(() => setVideos(JSON.parse(localStorage.getItem("clipmind_videos") || "[]")), []);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">ClipMind <span>AI</span></div>
        <nav>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/upload">Upload Video</Link>
          <Link className="active" href="/history">Upload History</Link>
        </nav>
      </aside>
      <section className="content">
        <p className="eyebrow">VIDEO MANAGEMENT</p>
        <h1>Upload History</h1>
        <p className="muted">Track uploaded files and their current processing status.</p>
        <div className="panel">
          {videos.length === 0 ? <p className="empty">No uploads found.</p> :
            <div className="table">
              <div className="row header"><span>Filename</span><span>Status</span><span>Uploaded</span></div>
              {videos.slice().reverse().map(v => (
                <div className="row" key={v.id}>
                  <span>{v.filename}</span>
                  <span><b className="status">{v.status}</b></span>
                  <span>{v.uploadedAt}</span>
                </div>
              ))}
            </div>}
        </div>
      </section>
    </main>
  );
}