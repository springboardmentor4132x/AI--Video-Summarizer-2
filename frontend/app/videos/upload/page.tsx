"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { uploadVideo } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const CAN_UPLOAD = new Set(["content_creator", "educator", "administrator"]);

export default function UploadPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user && !CAN_UPLOAD.has(user.role)) {
    return (
      <AppShell>
        <h1 className="font-display text-4xl">Upload locked</h1>
        <p className="mt-3 text-sand/60">Learners can watch and bookmark, but cannot upload. Switch to a creator or educator account.</p>
      </AppShell>
    );
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const video = await uploadVideo(file, title, description, setProgress);
      router.push(`/videos/${video.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-4xl">Upload a lecture or clip</h1>
      <p className="mt-2 max-w-xl text-sand/60">MP4, MOV, WebM, MKV, AVI. Max 500 MB. After upload, run FFmpeg processing to extract audio and a thumbnail.</p>
      <form onSubmit={onSubmit} className="card mt-8 max-w-xl space-y-4 p-6">
        <input
          className="input file:mr-4 file:rounded-full file:border-0 file:bg-ember file:px-4 file:py-2 file:text-ink-950"
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          required
        />
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title (optional)" />
        <textarea className="input min-h-28" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
        {busy ? (
          <div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
              <div className="h-full bg-ember" style={{ width: `${progress}%` }} />
            </div>
            <p className="mt-2 text-xs text-sand/50">{progress}%</p>
          </div>
        ) : null}
        {error ? <p className="text-sm text-red-300">{error}</p> : null}
        <button className="btn-primary" disabled={busy || !file}>{busy ? "Uploading…" : "Upload video"}</button>
      </form>
    </AppShell>
  );
}
