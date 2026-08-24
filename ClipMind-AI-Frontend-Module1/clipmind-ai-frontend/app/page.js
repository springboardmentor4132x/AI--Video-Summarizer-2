import Link from "next/link";

export default function Home() {
  return (
    <main className="landing">
      <div className="hero-card">
        <div className="brand">ClipMind <span>AI</span></div>
        <p className="eyebrow">VIDEO LEARNING PLATFORM</p>
        <h1>Upload, process and manage learning videos in one place.</h1>
        <p className="hero-text">
          A clean foundation for authentication, role-based dashboards,
          video uploads, history and FFmpeg processing.
        </p>
        <div className="actions">
          <Link className="btn primary" href="/login">Login</Link>
          <Link className="btn secondary" href="/register">Create account</Link>
        </div>
      </div>
    </main>
  );
}