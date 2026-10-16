"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { api, type UserRole } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("learner");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const { access_token } = await api.register({ email, password, full_name: fullName, role });
      await login(access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <Link href="/" className="font-display text-3xl">ClipMind</Link>
      <h2 className="mt-8 text-2xl font-medium">Create your workspace</h2>
      <form onSubmit={onSubmit} className="card mt-6 space-y-4 p-6">
        <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Full name" required />
        <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />
        <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password (min 8)" required minLength={8} />
        <select className="input" value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
          <option value="learner">Learner</option>
          <option value="content_creator">Content creator</option>
          <option value="educator">Educator</option>
        </select>
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Creating…" : "Register"}</button>
      </form>
      <p className="mt-4 text-sm text-sand/60">
        Already have an account? <Link href="/login" className="text-ember">Sign in</Link>
      </p>
    </div>
  );
}
