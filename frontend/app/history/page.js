"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

export default function HistoryPage() {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchVideos() {
      const token = localStorage.getItem("clipmind_token");
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await fetch("http://localhost:8000/videos/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setVideos(data);
        } else {
          setError("Failed to load video history.");
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchVideos();
  }, []);

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
        <p className="muted">Track uploaded files stored in PostgreSQL and their current processing status.</p>
        <div className="panel">
          {loading ? (
            <p className="muted">Loading video history...</p>
          ) : error ? (
            <p className="error">{error}</p>
          ) : videos.length === 0 ? (
            <p className="empty">No uploads found.</p>
          ) : (
            <div className="table">
              <div className="row header">
                <span>Filename</span>
                <span>Status</span>
                <span>Uploaded</span>
              </div>
              {videos.map((v) => (
                <div className="row" key={v.id}>
                  <span>{v.filename}</span>
                  <span><b className="status">{v.status}</b></span>
                  <span>{new Date(v.uploaded_at).toLocaleString()}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}