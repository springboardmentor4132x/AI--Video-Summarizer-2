"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { api, type User } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function AdminUsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user?.role !== "administrator") return;
    api.users().then(setUsers).catch((err) => setError(err.message));
  }, [user]);

  if (user && user.role !== "administrator") {
    return (
      <AppShell>
        <h1 className="font-display text-4xl">Admin only</h1>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <h1 className="font-display text-4xl">Users</h1>
      <p className="mt-2 text-sand/60">Role management and audit depth expand in later milestones.</p>
      {error ? <p className="mt-4 text-red-300">{error}</p> : null}
      <div className="card mt-8 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-sand/50">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Email</th>
              <th className="px-4 py-3 font-medium">Role</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map((row) => (
              <tr key={row.id} className="border-t border-white/10">
                <td className="px-4 py-3">{row.full_name}</td>
                <td className="px-4 py-3 text-sand/70">{row.email}</td>
                <td className="px-4 py-3 capitalize">{row.role.replace("_", " ")}</td>
                <td className="px-4 py-3">{row.is_active ? "Active" : "Disabled"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppShell>
  );
}
