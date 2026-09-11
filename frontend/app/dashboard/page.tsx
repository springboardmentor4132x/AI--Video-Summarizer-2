"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api, type VideoItem } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function DashboardPage() {
  const { user } = useAuth();
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.videos().then(setVideos).catch((err) => setError(err.message));
  }, []);

  const mine = videos.filter((v) => v.owner_id === user?.id);
  const processing = videos.filter((v) => v.status === "processing").length;
  const ready = videos.filter((v) => v.status === "ready").length;

  return (
    <AppShell>
      <p className="text-sm text-moss">Good to see you, {user?.full_name.split(" ")[0]}</p>
      <h1 className="font-display mt-2 text-4xl">Studio overview</h1>
      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <Stat label="Your videos" value={mine.length} />
        <Stat label="Processing" value={processing} />
        <Stat label="Ready" value={ready} />
      </div>
      <div className="mt-10 flex items-center justify-between">
        <h2 className="text-lg font-medium">Recent library</h2>
        <Link href="/videos" className="text-sm text-ember">View all</Link>
      </div>
      {error ? <p className="mt-3 text-red-300">{error}</p> : null}
      <div className="mt-4 grid gap-3">
        {videos.slice(0, 6).map((video) => (
          <Link key={video.id} href={`/videos/${video.id}`} className="card flex items-center justify-between p-4 hover:border-ember/40">
            <div>
              <p className="font-medium">{video.title}</p>
              <p className="text-xs text-sand/50">{video.owner_name} · {video.status}</p>
            </div>
            <span className="text-sand/40">→</span>
          </Link>
        ))}
        {videos.length === 0 ? <p className="text-sand/50">No videos yet. Upload one to start the pipeline.</p> : null}
      </div>
    </AppShell>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="card p-5">
      <p className="text-xs uppercase tracking-widest text-sand/50">{label}</p>
      <p className="font-display mt-2 text-4xl">{value}</p>
    </div>
  );
}
