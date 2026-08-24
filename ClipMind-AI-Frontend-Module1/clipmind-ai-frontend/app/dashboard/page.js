"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [videos, setVideos] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("clipmind_token");
    if (!token) return router.push("/login");
    setUser(JSON.parse(localStorage.getItem("clipmind_user") || "{}"));
    setVideos(JSON.parse(localStorage.getItem("clipmind_videos") || "[]"));
  }, [router]);

  function logout() {
    localStorage.removeItem("clipmind_token");
    router.push("/login");
  }

  if (!user) return <div className="loading">Loading...</div>;

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">ClipMind <span>AI</span></div>
        <nav>
          <Link className="active" href="/dashboard">Dashboard</Link>
          <Link href="/upload">Upload Video</Link>
          <Link href="/history">Upload History</Link>
        </nav>
        <button className="logout" onClick={logout}>Logout</button>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">DASHBOARD</p>
            <h1>Hello, {user.name || user.email?.split("@")[0] || "User"} 👋</h1>
          </div>
          <span className="role-badge">{user.role}</span>
        </header>

        <div className="stats">
          <div className="stat"><span>Total Videos</span><strong>{videos.length}</strong></div>
          <div className="stat"><span>Processing</span><strong>{videos.filter(v => v.status === "Processing").length}</strong></div>
          <div className="stat"><span>Completed</span><strong>{videos.filter(v => v.status === "Completed").length}</strong></div>
        </div>

        <div className="grid-two">
          <div className="panel">
            <div className="panel-head"><h2>Quick Actions</h2></div>
            <div className="quick-actions">
              <Link href="/upload" className="quick">＋ Upload Video</Link>
              <Link href="/history" className="quick">◷ View History</Link>
            </div>
          </div>
          <div className="panel">
            <div className="panel-head"><h2>Access</h2></div>
            <p className="muted">Your current role is <b>{user.role}</b>. The backend will enforce permissions using JWT and RBAC.</p>
          </div>
        </div>

        <div className="panel">
          <div className="panel-head"><h2>Recent Videos</h2><Link href="/history">View all</Link></div>
          {videos.length === 0 ? <p className="empty">No videos uploaded yet.</p> :
            <div className="table">
              {videos.slice(-5).reverse().map(v => (
                <div className="row" key={v.id}>
                  <span>{v.filename}</span><span>{v.status}</span><span>{v.uploadedAt}</span>
                </div>
              ))}
            </div>}
        </div>
      </section>
    </main>
  );
}