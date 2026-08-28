"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function HistoryPage() {
  const router = useRouter();
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selectedVideo, setSelectedVideo] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("summary"); // 'summary' or 'transcript'
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function fetchVideos() {
      const token = localStorage.getItem("clipmind_token");
      if (!token) {
        setLoading(false);
        router.push("/login");
        return;
      }

      try {
        const res = await fetch("http://localhost:8000/videos/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.status === 401) {
          localStorage.removeItem("clipmind_token");
          setError("Your session has expired. Please log in again.");
          setTimeout(() => router.push("/login"), 1500);
          return;
        }

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
  }, [router]);

  const openSummaryModal = async (video) => {
    setSelectedVideo(video);
    setSummaryLoading(true);
    setSummaryData(null);
    setActiveTab("summary");
    setCopied(false);

    const token = localStorage.getItem("clipmind_token");
    try {
      const res = await fetch(`http://localhost:8000/videos/${video.id}/summary`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.status === 401) {
        localStorage.removeItem("clipmind_token");
        router.push("/login");
        return;
      }

      if (res.ok) {
        const data = await res.json();
        setSummaryData(data);
      } else {
        setSummaryData({
          summary: "Failed to generate AI summary for this video.",
          takeaways: ["Verify backend connection", "Check API permissions"],
          transcript: "Could not fetch transcript."
        });
      }
    } catch (err) {
      setSummaryData({
        summary: `Error: ${err.message}`,
        takeaways: ["Could not connect to AI summarization server"],
        transcript: "Transcript error."
      });
    } finally {
      setSummaryLoading(false);
    }
  };

  const copyTranscript = () => {
    if (summaryData?.transcript) {
      navigator.clipboard.writeText(summaryData.transcript);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

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
        <p className="muted">Track uploaded files stored in PostgreSQL and view AI summaries & full transcripts.</p>

        <div className="panel">
          {loading ? (
            <p className="muted">Loading video history...</p>
          ) : error ? (
            <div style={{ textAlign: "center", padding: "20px" }}>
              <p className="error" style={{ marginBottom: "12px" }}>{error}</p>
              <Link href="/login" className="btn primary sm">Go to Login 🔑</Link>
            </div>
          ) : videos.length === 0 ? (
            <p className="empty">No uploads found.</p>
          ) : (
            <div className="table">
              <div className="row header">
                <span>Filename</span>
                <span>Format</span>
                <span>Status</span>
                <span>Uploaded</span>
                <span>AI Summary & Transcript</span>
              </div>
              {videos.map((v) => (
                <div className="row" key={v.id}>
                  <span>{v.filename}</span>
                  <span><code className="tag">{(v.file_type || "mp4").toUpperCase()}</code></span>
                  <span><b className="status">{v.status}</b></span>
                  <span>{new Date(v.uploaded_at).toLocaleDateString()}</span>
                  <span>
                    <button 
                      className="btn secondary sm"
                      onClick={() => openSummaryModal(v)}
                      style={{ padding: "4px 12px", fontSize: "0.85rem", cursor: "pointer" }}
                    >
                      View Details ✨
                    </button>
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Dynamic Gemini AI Summary & Transcript Modal */}
        {selectedVideo && (
          <div style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.65)",
            backdropFilter: "blur(4px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
            padding: "20px"
          }}>
            <div style={{
              background: "#12141c",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "12px",
              maxWidth: "650px",
              width: "100%",
              padding: "28px",
              boxShadow: "0 20px 50px rgba(0,0,0,0.5)",
              color: "#fff",
              position: "relative"
            }}>
              <button 
                onClick={() => setSelectedVideo(null)}
                style={{
                  position: "absolute",
                  top: "16px",
                  right: "16px",
                  background: "transparent",
                  border: "none",
                  color: "#aaa",
                  fontSize: "1.2rem",
                  cursor: "pointer"
                }}
              >
                ✕
              </button>

              <p style={{ color: "#6366f1", fontSize: "0.8rem", fontWeight: 700, letterSpacing: "1px", textTransform: "uppercase" }}>
                CLIPMIND AI VIDEO INTELLIGENCE
              </p>
              <h2 style={{ marginTop: "4px", marginBottom: "16px" }}>{selectedVideo.filename}</h2>

              {/* Navigation Tabs */}
              <div style={{ display: "flex", gap: "10px", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "12px", marginBottom: "20px" }}>
                <button
                  onClick={() => setActiveTab("summary")}
                  style={{
                    background: activeTab === "summary" ? "#6366f1" : "transparent",
                    color: activeTab === "summary" ? "#fff" : "#94a3b8",
                    border: "1px solid " + (activeTab === "summary" ? "#6366f1" : "rgba(255,255,255,0.1)"),
                    padding: "6px 14px",
                    borderRadius: "6px",
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    cursor: "pointer"
                  }}
                >
                  🧠 Executive Summary
                </button>
                <button
                  onClick={() => setActiveTab("transcript")}
                  style={{
                    background: activeTab === "transcript" ? "#6366f1" : "transparent",
                    color: activeTab === "transcript" ? "#fff" : "#94a3b8",
                    border: "1px solid " + (activeTab === "transcript" ? "#6366f1" : "rgba(255,255,255,0.1)"),
                    padding: "6px 14px",
                    borderRadius: "6px",
                    fontSize: "0.85rem",
                    fontWeight: 600,
                    cursor: "pointer"
                  }}
                >
                  📜 Full Audio Transcript
                </button>
              </div>

              {summaryLoading ? (
                <div style={{ padding: "30px 0", textAlign: "center" }}>
                  <p style={{ color: "#818cf8", fontSize: "1rem" }}>⚡ Processing AI Summary & Speech-to-Text Transcript...</p>
                </div>
              ) : summaryData ? (
                activeTab === "summary" ? (
                  <>
                    <div style={{ background: "#1a1d2b", padding: "16px", borderRadius: "8px", marginBottom: "16px" }}>
                      <h4 style={{ color: "#e2e8f0", marginBottom: "8px" }}>🧠 Executive Summary</h4>
                      <p style={{ color: "#94a3b8", fontSize: "0.9rem", lineHeight: "1.5" }}>
                        {summaryData.summary}
                      </p>
                    </div>

                    <div style={{ marginBottom: "20px" }}>
                      <h4 style={{ color: "#e2e8f0", marginBottom: "8px" }}>📌 Key Takeaways</h4>
                      <ul style={{ color: "#94a3b8", fontSize: "0.88rem", paddingLeft: "20px", lineHeight: "1.6" }}>
                        {summaryData.takeaways.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </>
                ) : (
                  <div style={{ marginBottom: "20px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <h4 style={{ color: "#e2e8f0" }}>📜 Full Audio Transcript (Whisper Speech-to-Text)</h4>
                      <button
                        onClick={copyTranscript}
                        style={{
                          background: "rgba(99,102,241,0.2)",
                          color: "#818cf8",
                          border: "1px solid rgba(99,102,241,0.4)",
                          padding: "4px 10px",
                          borderRadius: "4px",
                          fontSize: "0.75rem",
                          cursor: "pointer"
                        }}
                      >
                        {copied ? "Copied! ✓" : "Copy Transcript 📋"}
                      </button>
                    </div>
                    <div style={{
                      background: "#1a1d2b",
                      padding: "16px",
                      borderRadius: "8px",
                      maxHeight: "220px",
                      overflowY: "auto",
                      border: "1px solid rgba(255,255,255,0.05)"
                    }}>
                      <p style={{ color: "#cbd5e1", fontSize: "0.88rem", lineHeight: "1.6", whiteSpace: "pre-wrap" }}>
                        {summaryData.transcript}
                      </p>
                    </div>
                  </div>
                )
              ) : null}

              <button 
                className="btn primary full" 
                onClick={() => setSelectedVideo(null)}
                style={{ padding: "10px", width: "100%", cursor: "pointer" }}
              >
                Close Modal
              </button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}