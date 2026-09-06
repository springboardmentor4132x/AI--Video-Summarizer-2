"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell, StatusBadge } from "@/components/AppShell";
import { api, mediaUrl, type VideoItem } from "@/lib/api";

function formatDuration(sec: number | null) {
  if (!sec) return "—";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function VideosPage() {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.videos().then(setVideos).catch((err) => setError(err.message));
  }, []);

  return (
    <AppShell>
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-4xl">Library</h1>
          <p className="mt-2 text-sand/60">Upload history and processing status.</p>
        </div>
        <Link href="/videos/upload" className="btn-primary">Upload</Link>
      </div>
      {error ? <p className="mt-4 text-red-300">{error}</p> : null}
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {videos.map((video) => (
          <Link key={video.id} href={`/videos/${video.id}`} className="card overflow-hidden hover:border-ember/40">
            <div className="aspect-video bg-ink-950">
              {video.has_thumbnail ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={mediaUrl(video.id, "thumbnail")} alt="" className="h-full w-full object-cover" />
              ) : (
                <div className="flex h-full items-center justify-center text-sand/30">No thumbnail yet</div>
              )}
            </div>
            <div className="space-y-2 p-4">
              <div className="flex items-start justify-between gap-2">
                <p className="font-medium leading-snug">{video.title}</p>
                <StatusBadge status={video.status} />
              </div>
              <p className="text-xs text-sand/50">
                {video.owner_name} · {formatDuration(video.duration)}
              </p>
            </div>
          </Link>
        ))}
      </div>
      {videos.length === 0 ? <p className="mt-8 text-sand/50">The shelf is empty.</p> : null}
    </AppShell>
  );
}
