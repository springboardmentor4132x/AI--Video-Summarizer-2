"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ name:"", email:"", password:"", confirm:"", role:"Learner" });
  const [error, setError] = useState("");

  function update(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function register(e) {
    e.preventDefault();
    if (!form.name || !form.email || !form.password) return setError("Please fill all required fields.");
    if (form.password !== form.confirm) return setError("Passwords do not match.");
    localStorage.setItem("clipmind_user", JSON.stringify({ email: form.email, name: form.name, role: form.role }));
    localStorage.setItem("clipmind_token", "demo-jwt-token");
    router.push("/dashboard");
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={register}>
        <Link href="/" className="back">← ClipMind AI</Link>
        <h1>Create account</h1>
        <p>Set up your ClipMind AI account.</p>
        {error && <div className="error">{error}</div>}
        <label>Full Name</label>
        <input name="name" value={form.name} onChange={update} placeholder="Your full name" />
        <label>Email</label>
        <input name="email" type="email" value={form.email} onChange={update} placeholder="you@example.com" />
        <label>Password</label>
        <input name="password" type="password" value={form.password} onChange={update} placeholder="Create a password" />
        <label>Confirm Password</label>
        <input name="confirm" type="password" value={form.confirm} onChange={update} placeholder="Repeat password" />
        <label>Role</label>
        <select name="role" value={form.role} onChange={update}>
          <option>Content Creator</option>
          <option>Learner</option>
          <option>Educator</option>
          <option>Administrator</option>
        </select>
        <button className="btn primary full">Register</button>
        <p className="switch">Already have an account? <Link href="/login">Login</Link></p>
      </form>
    </main>
  );
}