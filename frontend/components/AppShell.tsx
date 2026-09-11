"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth";
import type { UserRole } from "@/lib/api";

const NAV: { href: string; label: string; roles?: UserRole[] }[] = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/videos", label: "Library" },
  { href: "/videos/upload", label: "Upload", roles: ["content_creator", "educator", "administrator"] },
  { href: "/profile", label: "Profile" },
  { href: "/admin/users", label: "Users", roles: ["administrator"] },
];

function roleLabel(role: UserRole) {
  return {
    content_creator: "Creator",
    learner: "Learner",
    educator: "Educator",
    administrator: "Admin",
  }[role];
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sand/60">
        Loading ClipMind…
      </div>
    );
  }

  const links = NAV.filter((item) => !item.roles || item.roles.includes(user.role));

  return (
    <div className="mx-auto flex min-h-screen max-w-7xl gap-6 px-4 py-6 md:px-8">
      <aside className="card hidden h-fit w-64 shrink-0 p-5 md:block">
        <Link href="/dashboard" className="block">
          <p className="font-display text-2xl tracking-tight">ClipMind</p>
          <p className="mt-1 text-xs uppercase tracking-[0.2em] text-moss">AI video studio</p>
        </Link>
        <div className="mt-8 space-y-1">
          {links.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-xl px-3 py-2 text-sm ${
                  active ? "bg-ember/15 text-ember" : "text-sand/70 hover:bg-white/5 hover:text-sand"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
        <div className="mt-10 border-t border-white/10 pt-4">
          <p className="text-sm font-medium">{user.full_name}</p>
          <p className="text-xs text-sand/50">{roleLabel(user.role)}</p>
          <button className="btn-ghost mt-4 w-full" onClick={() => { logout(); router.push("/login"); }}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="min-w-0 flex-1">
        <div className="mb-4 flex items-center justify-between md:hidden">
          <Link href="/dashboard" className="font-display text-xl">ClipMind</Link>
          <button className="btn-ghost" onClick={() => { logout(); router.push("/login"); }}>Out</button>
        </div>
        {children}
      </main>
    </div>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    uploaded: "bg-sand/10 text-sand",
    processing: "bg-amber-400/15 text-amber-300",
    ready: "bg-moss/20 text-moss",
    failed: "bg-red-500/15 text-red-300",
    queued: "bg-white/10 text-sand/70",
    running: "bg-amber-400/15 text-amber-300",
    completed: "bg-moss/20 text-moss",
  };
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs capitalize ${map[status] || "bg-white/10"}`}>
      {status}
    </span>
  );
}
