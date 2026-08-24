"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("Learner");
  const [error, setError] = useState("");

  function login(e) {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter email and password.");
      return;
    }
    localStorage.setItem("clipmind_user", JSON.stringify({ email, role }));
    localStorage.setItem("clipmind_token", "demo-jwt-token");
    router.push("/dashboard");
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={login}>
        <Link href="/" className="back">← ClipMind AI</Link>
        <h1>Welcome back</h1>
        <p>Sign in to continue to your dashboard.</p>
        {error && <div className="error">{error}</div>}
        <label>Email</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
        <label>Password</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
        <label>Role</label>
        <select value={role} onChange={e => setRole(e.target.value)}>
          <option>Content Creator</option>
          <option>Learner</option>
          <option>Educator</option>
          <option>Administrator</option>
        </select>
        <button className="btn primary full">Login</button>
        <p className="switch">Don't have an account? <Link href="/register">Register</Link></p>
      </form>
    </main>
  );
}