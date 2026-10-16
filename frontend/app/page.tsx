"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function HomePage() {
  const { user, loading } = useAuth();

  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6">
      <p className="text-xs uppercase tracking-[0.35em] text-moss">ClipMind AI</p>
      <h1 className="font-display mt-4 max-w-3xl text-5xl leading-tight text-sand md:text-7xl">
        Watch less. Understand more.
      </h1>
      <p className="mt-6 max-w-xl text-lg text-sand/70">
        Upload long-form video. ClipMind extracts audio, prepares transcripts, summaries, and
        key moments so students, creators, and educators can skip to what matters.
      </p>
      <div className="mt-10 flex flex-wrap gap-3">
        {loading ? null : user ? (
          <Link href="/dashboard" className="btn-primary">
            Open dashboard
          </Link>
        ) : (
          <>
            <Link href="/register" className="btn-primary">
              Create account
            </Link>
            <Link href="/login" className="btn-ghost">
              Sign in
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
