"use client";

import { FormEvent, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function ProfilePage() {
  const { user, refresh } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [bio, setBio] = useState(user?.bio || "");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      await api.updateMe({ full_name: fullName, bio });
      await refresh();
      setMessage("Profile saved.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Could not save");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-4xl">Profile</h1>
      <form onSubmit={onSubmit} className="card mt-8 max-w-xl space-y-4 p-6">
        <p className="text-sm text-sand/50">{user?.email} · {user?.role}</p>
        <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Full name" />
        <textarea className="input min-h-28" value={bio} onChange={(e) => setBio(e.target.value)} placeholder="Bio" />
        {message ? <p className="text-sm text-moss">{message}</p> : null}
        <button className="btn-primary" disabled={busy}>{busy ? "Saving…" : "Save changes"}</button>
      </form>
    </AppShell>
  );
}
