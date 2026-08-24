"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirm: "", role: "Learner" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function register(e) {
    e.preventDefault();
    setError("");

    if (!form.name || !form.email || !form.password) {
      return setError("Please fill all required fields.");
    }
    if (form.password !== form.confirm) {
      return setError("Passwords do not match.");
    }
    if (form.password.length < 8) {
      return setError("Password must be at least 8 characters long.");
    }

    setLoading(true);

    try {
      const formattedRole = form.role.toLowerCase().replace(" ", "_");
      const res = await fetch("http://localhost:8000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name,
          email: form.email,
          password: form.password,
          role: formattedRole,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        let msg = "Registration failed.";
        if (typeof data.detail === "string") {
          msg = data.detail;
        } else if (Array.isArray(data.detail)) {
          msg = data.detail.map((d) => `${d.loc?.[d.loc.length - 1] || "field"}: ${d.msg}`).join(", ");
        }
        throw new Error(msg);
      }

      // Automatically log in to receive JWT token upon registration
      const loginRes = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
        }),
      });

      const loginData = await loginRes.json();
      if (!loginRes.ok) {
        let loginMsg = "Login failed after registration.";
        if (typeof loginData.detail === "string") {
          loginMsg = loginData.detail;
        } else if (Array.isArray(loginData.detail)) {
          loginMsg = loginData.detail.map((d) => `${d.loc?.[d.loc.length - 1] || "field"}: ${d.msg}`).join(", ");
        }
        throw new Error(loginMsg);
      }

      localStorage.setItem("clipmind_user", JSON.stringify(data));
      localStorage.setItem("clipmind_token", loginData.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={register}>
        <Link href="/" className="back">← ClipMind AI</Link>
        <h1>Create account</h1>
        <p>Set up your ClipMind AI account.</p>
        {error && <div className="error">{error}</div>}
        <label>Full Name</label>
        <input name="name" value={form.name} onChange={update} placeholder="Your full name" required />
        <label>Email</label>
        <input name="email" type="email" value={form.email} onChange={update} placeholder="you@example.com" required />
        <label>Password (min 8 characters)</label>
        <input name="password" type="password" value={form.password} onChange={update} placeholder="Create a password" required />
        <label>Confirm Password</label>
        <input name="confirm" type="password" value={form.confirm} onChange={update} placeholder="Repeat password" required />
        <label>Role</label>
        <select name="role" value={form.role} onChange={update}>
          <option>Content Creator</option>
          <option>Learner</option>
          <option>Educator</option>
          <option>Administrator</option>
        </select>
        <button className="btn primary full" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
        <p className="switch">Already have an account? <Link href="/login">Login</Link></p>
      </form>
    </main>
  );
}