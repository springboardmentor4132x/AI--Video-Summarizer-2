"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function login(e) {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please enter email and password.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        let msg = "Incorrect email or password.";
        if (typeof data.detail === "string") {
          msg = data.detail;
        } else if (Array.isArray(data.detail)) {
          msg = data.detail.map((d) => `${d.loc?.[d.loc.length - 1] || "field"}: ${d.msg}`).join(", ");
        }
        throw new Error(msg);
      }

      // Store real JWT token
      localStorage.setItem("clipmind_token", data.access_token);

      // Fetch logged-in user profile using JWT token
      const profileRes = await fetch("http://localhost:8000/auth/me", {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      });

      if (profileRes.ok) {
        const userProfile = await profileRes.json();
        localStorage.setItem("clipmind_user", JSON.stringify(userProfile));
      }

      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={login}>
        <Link href="/" className="back">← ClipMind AI</Link>
        <h1>Welcome back</h1>
        <p>Sign in to continue to your dashboard.</p>
        {error && <div className="error">{error}</div>}
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
        />
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
          required
        />
        <button className="btn primary full" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
        <p className="switch">Don't have an account? <Link href="/register">Register</Link></p>
      </form>
    </main>
  );
}