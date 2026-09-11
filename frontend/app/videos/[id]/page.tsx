"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { AppShell, StatusBadge } from "@/components/AppShell";
import { api, mediaUrl, type AnalysisItem, type JobItem, type SummaryItem, type TranscriptItem, type VideoItem } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function VideoDetailPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [video, setVideo] = useState<VideoItem | null>(null);
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [transcript, setTranscript] = useState<TranscriptItem | null>(null);
  const [summary, setSummary] = useState<SummaryItem | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisItem>({ topics: [], key_moments: [] });
  const [editing, setEditing] = useState(false);
  const [transcriptText, setTranscriptText] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const playerRef = useRef<HTMLVideoElement>(null);

  const load = useCallback(async () => {
    const [v, j, t, s, a] = await Promise.all([api.video(params.id), api.jobs(params.id), api.transcript(params.id), api.summary(params.id), api.analysis(params.id)]);
    setVideo(v);
    setJobs(j);
    setTranscript(t);
    setTranscriptText(t.edited_text || t.full_text || "");
    setSummary(s);
    setAnalysis(a);
  }, [params.id]);

  useEffect(() => {
    load().catch((err) => setError(err.message));
  }, [load]);

  useEffect(() => {
    const active = jobs.some((j) => j.status === "queued" || j.status === "running") || video?.status === "processing" || transcript?.status === "processing" || summary?.status === "processing";
    if (!active) return;
    const timer = setInterval(() => {
      load().catch(() => undefined);
    }, 2500);
    return () => clearInterval(timer);
  }, [jobs, video?.status, load]);

  async function processNow() {
    setBusy(true);
    setError("");
    try {
      await api.processVideo(params.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start processing");
    } finally {
      setBusy(false);
    }
  }

  async function saveTranscript() {
    setBusy(true);
    try { setTranscript(await api.updateTranscript(params.id, transcriptText)); setEditing(false); }
    catch (err) { setError(err instanceof Error ? err.message : "Could not save transcript"); }
    finally { setBusy(false); }
  }

  async function generateSummary() {
    setBusy(true);
    try { await api.generateSummary(params.id); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "Could not start summary"); }
    finally { setBusy(false); }
  }

  async function rerunAnalysis() {
    setBusy(true);
    try { await api.rerunAnalysis(params.id); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "Could not start analysis"); }
    finally { setBusy(false); }
  }

  function seekTo(seconds: number) {
    if (playerRef.current) {
      playerRef.current.currentTime = seconds;
      void playerRef.current.play();
    }
  }

  function formatTime(seconds: number) {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${Math.floor(seconds % 60).toString().padStart(2, "0")}`;
  }

  if (!video) {
    return (
      <AppShell>
        <p className="text-sand/50">{error || "Loading video…"}</p>
      </AppShell>
    );
  }

  const canManage = user?.role === "administrator" || user?.id === video.owner_id;
  const latest = jobs[0];

  return (
    <AppShell>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-moss">{video.original_filename}</p>
          <h1 className="font-display mt-2 text-4xl">{video.title}</h1>
          <p className="mt-2 text-sand/60">{video.description || "No description"}</p>
        </div>
        <StatusBadge status={video.status} />
      </div>

      <div className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-black">
        <video ref={playerRef} className="aspect-video w-full" controls src={mediaUrl(video.id, "stream")} poster={video.has_thumbnail ? mediaUrl(video.id, "thumbnail") : undefined} />
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <Meta label="Duration" value={video.duration ? `${Math.round(video.duration)}s` : "Pending"} />
        <Meta label="Resolution" value={video.width ? `${video.width}×${video.height}` : "Pending"} />
        <Meta label="Size" value={video.file_size ? `${(video.file_size / (1024 * 1024)).toFixed(1)} MB` : "—"} />
      </div>

      {video.error_message ? <p className="mt-4 text-sm text-red-300">{video.error_message}</p> : null}
      {error ? <p className="mt-4 text-sm text-red-300">{error}</p> : null}

      {canManage ? (
        <div className="card mt-8 p-6">
          <h2 className="text-lg font-medium">FFmpeg pipeline</h2>
          <p className="mt-1 text-sm text-sand/60">
            Extracts audio and a thumbnail, then generates a timestamped transcript for analysis.
          </p>
          <button className="btn-primary mt-4" onClick={processNow} disabled={busy || video.status === "processing"}>
            {busy || video.status === "processing" ? "Processing…" : "Run processing"}
          </button>
          {latest ? (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm">
                <span>{latest.job_type}</span>
                <StatusBadge status={latest.status} />
              </div>
              <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/10">
                <div className="h-full bg-moss" style={{ width: `${latest.progress}%` }} />
              </div>
            </div>
          ) : null}
        </div>
      ) : null}

      <section className="card mt-6 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div><p className="text-xs uppercase tracking-widest text-moss">Transcript</p><h2 className="mt-1 text-xl">Generated transcript</h2></div>
          <StatusBadge status={transcript?.status || "not_started"} />
        </div>
        {transcript?.status === "processing" ? <p className="mt-5 text-sand/60">Transcription in progress…</p> : null}
        {transcript?.status === "failed" ? <p className="mt-5 text-red-300">{transcript.error_message || "Transcription failed. Run processing to try again."}</p> : null}
        {transcript?.status === "completed" ? <>
          {editing ? <textarea className="input mt-5 min-h-48" value={transcriptText} onChange={(event) => setTranscriptText(event.target.value)} /> : <p className="mt-5 whitespace-pre-wrap text-sm leading-7 text-sand/80">{transcriptText}</p>}
          {canManage ? <div className="mt-4 flex gap-3">{editing ? <button className="btn-primary" onClick={saveTranscript} disabled={busy}>Save transcript</button> : <button className="btn-ghost" onClick={() => setEditing(true)}>Edit transcript</button>}{editing ? <button className="btn-ghost" onClick={() => setEditing(false)}>Cancel</button> : null}</div> : null}
        </> : null}
      </section>

      <section className="card mt-6 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs uppercase tracking-widest text-moss">Summary</p><h2 className="mt-1 text-xl">AI summary</h2></div><StatusBadge status={summary?.status || "not_started"} /></div>
        {summary?.status === "processing" ? <p className="mt-5 text-sand/60">Generating summary…</p> : null}
        {summary?.status === "failed" ? <p className="mt-5 text-red-300">{summary.error_message || "Summary generation failed. Please try again."}</p> : null}
        {summary?.status === "completed" ? <div className="mt-5 grid gap-5 md:grid-cols-2"><div><h3 className="font-medium text-ember">Short summary</h3><p className="mt-2 text-sm leading-7 text-sand/80">{summary.short_text}</p></div><div><h3 className="font-medium text-ember">Detailed summary</h3><p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-sand/80">{summary.detailed_text}</p></div></div> : null}
        {canManage ? <button className="btn-primary mt-5" onClick={generateSummary} disabled={busy || summary?.status === "processing" || transcript?.status !== "completed"}>{summary?.status === "completed" ? "Regenerate summary" : "Generate summary"}</button> : null}
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <div className="flex items-center justify-between gap-3"><div><p className="text-xs uppercase tracking-widest text-moss">Topics</p><h2 className="mt-1 text-xl">Detected topics</h2></div><span className="text-xs text-sand/50">{analysis.topics.length}</span></div>
          {analysis.topics.length ? <ul className="mt-5 space-y-2">{analysis.topics.map((topic) => <li key={topic.id}><button className="flex w-full items-start gap-3 border-b border-white/10 py-3 text-left hover:text-ember" onClick={() => seekTo(topic.start_sec)}><span className="font-mono text-xs text-moss">{formatTime(topic.start_sec)}</span><span className="text-sm">{topic.title}</span></button></li>)}</ul> : <p className="mt-5 text-sm text-sand/50">Analysis will appear after transcription.</p>}
        </div>
        <div className="card p-6">
          <div className="flex items-center justify-between gap-3"><div><p className="text-xs uppercase tracking-widest text-moss">Key moments</p><h2 className="mt-1 text-xl">Useful highlights</h2></div>{canManage && transcript?.status === "completed" ? <button className="btn-ghost text-xs" onClick={rerunAnalysis} disabled={busy}>Rerun</button> : null}</div>
          {analysis.key_moments.length ? <ul className="mt-5 space-y-2">{analysis.key_moments.map((moment) => <li key={moment.id}><button className="w-full border-b border-white/10 py-3 text-left hover:text-ember" onClick={() => seekTo(moment.start_sec)}><div className="flex items-center justify-between gap-3"><span className="font-mono text-xs text-moss">{formatTime(moment.start_sec)}</span><span className="text-xs text-sand/50">{moment.score?.toFixed(2)}</span></div><p className="mt-1 line-clamp-2 text-sm text-sand/80">{moment.transcript_text || moment.title}</p></button></li>)}</ul> : <p className="mt-5 text-sm text-sand/50">No highlights detected yet.</p>}
        </div>
      </section>
    </AppShell>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="card p-4">
      <p className="text-xs uppercase tracking-widest text-sand/40">{label}</p>
      <p className="mt-1 text-lg">{value}</p>
    </div>
  );
}
