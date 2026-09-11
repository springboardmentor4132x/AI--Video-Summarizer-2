"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { AppShell, StatusBadge } from "@/components/AppShell";
import { api, type AnalyticsDashboardData } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function DashboardPage() {
  const { user } = useAuth();
  const [days, setDays] = useState<number>(7);
  const [data, setData] = useState<AnalyticsDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadAnalytics = useCallback(async (selectedDays: number, isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError("");

    try {
      const result = await api.analytics(selectedDays);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load analytics dashboard data.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics(days);
  }, [days, loadAnalytics]);

  if (loading && !data) {
    return (
      <AppShell>
        <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-sand/60">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-ember border-t-transparent" />
          <p className="text-sm">Loading Analytical Dashboard metrics…</p>
        </div>
      </AppShell>
    );
  }

  const metrics = data?.metrics || {
    total_videos: 0,
    completed_videos: 0,
    transcripts_generated: 0,
    summaries_generated: 0,
    total_duration_sec: 0,
    total_duration_formatted: "0s",
    avg_duration_sec: 0,
    avg_duration_formatted: "0s",
    success_rate: 100,
    failed_processing: 0,
  };

  return (
    <AppShell>
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-moss">
            <span className="inline-block h-2 w-2 rounded-full bg-moss animate-pulse" />
            <span>LIVE ANALYTICS STUDIO</span>
          </div>
          <h1 className="font-display mt-1 text-3xl font-bold tracking-tight text-sand md:text-4xl">
            Analytics Dashboard
          </h1>
          <p className="mt-1 text-sm text-sand/60">
            Overview of your video processing activity, AI pipeline health & performance
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="cursor-pointer appearance-none rounded-xl border border-white/15 bg-black/60 px-4 py-2.5 pr-8 text-sm text-sand focus:border-ember focus:outline-none hover:border-white/30 transition-colors"
            >
              <option value={7}>7 Days ▼</option>
              <option value={30}>30 Days ▼</option>
              <option value={90}>90 Days ▼</option>
              <option value={0}>All Time ▼</option>
            </select>
          </div>

          <button
            onClick={() => loadAnalytics(days, true)}
            disabled={refreshing}
            className="btn-ghost flex items-center gap-2 rounded-xl border border-white/15 px-4 py-2.5 text-sm text-sand hover:border-white/30 hover:bg-white/5 active:scale-95 disabled:opacity-50 transition-all"
          >
            <span className={`text-base ${refreshing ? "animate-spin" : ""}`}>↻</span>
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {error ? (
        <div className="mt-4 rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-300">
          {error}
        </div>
      ) : null}

      {/* 8 Stat Cards Grid (2 Rows x 4 Columns) */}
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total Videos"
          value={metrics.total_videos}
          subtext="Uploaded to platform"
          icon="🎥"
          accent="from-blue-500/20 to-blue-500/5 text-blue-400 border-blue-500/20"
        />
        <StatCard
          label="Completed Videos"
          value={metrics.completed_videos}
          subtext="AI processing finished"
          icon="✅"
          accent="from-emerald-500/20 to-emerald-500/5 text-emerald-400 border-emerald-500/20"
        />
        <StatCard
          label="Transcripts Generated"
          value={metrics.transcripts_generated}
          subtext="Offline Whisper STT"
          icon="📝"
          accent="from-indigo-500/20 to-indigo-500/5 text-indigo-400 border-indigo-500/20"
        />
        <StatCard
          label="Summaries Generated"
          value={metrics.summaries_generated}
          subtext="Local DistilBART LLM"
          icon="✨"
          accent="from-purple-500/20 to-purple-500/5 text-purple-400 border-purple-500/20"
        />

        <StatCard
          label="Total Duration"
          value={metrics.total_duration_formatted}
          subtext="Total audio processed"
          icon="⏱️"
          accent="from-amber-500/20 to-amber-500/5 text-amber-400 border-amber-500/20"
        />
        <StatCard
          label="Avg Video Duration"
          value={metrics.avg_duration_formatted}
          subtext="Per uploaded file"
          icon="📊"
          accent="from-cyan-500/20 to-cyan-500/5 text-cyan-400 border-cyan-500/20"
        />
        <StatCard
          label="Success Rate"
          value={`${metrics.success_rate}%`}
          subtext="Pipeline completion"
          icon="📈"
          accent="from-moss/20 to-moss/5 text-moss border-moss/20"
        />
        <StatCard
          label="Failed Processing"
          value={metrics.failed_processing}
          subtext={metrics.failed_processing > 0 ? "Requires attention" : "Zero errors recorded"}
          icon="⚠️"
          accent={
            metrics.failed_processing > 0
              ? "from-rose-500/30 to-rose-500/10 text-rose-400 border-rose-500/30"
              : "from-white/10 to-white/5 text-sand/60 border-white/10"
          }
        />
      </div>

      {/* Charts Section 1: Line Chart & Donut Chart */}
      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        {/* Videos Processed Over Time (Line Chart) */}
        <div className="card p-6 lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-mono uppercase tracking-widest text-moss">Trends</p>
              <h2 className="mt-1 text-xl font-medium text-sand">Videos Processed Over Time</h2>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1.5 text-sand/70">
                <span className="h-2.5 w-2.5 rounded-full bg-blue-500" /> Uploaded
              </span>
              <span className="flex items-center gap-1.5 text-sand/70">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" /> Completed
              </span>
            </div>
          </div>

          <div className="mt-6">
            <LineChart overTime={data?.over_time || []} />
          </div>
        </div>

        {/* Processing Status (Donut Chart) */}
        <div className="card p-6">
          <p className="text-xs font-mono uppercase tracking-widest text-moss">Breakdown</p>
          <h2 className="mt-1 text-xl font-medium text-sand">Processing Status</h2>

          <div className="mt-4 flex flex-col items-center">
            <DonutChart
              statusData={data?.status_distribution || []}
              total={metrics.total_videos}
            />
          </div>
        </div>
      </div>

      {/* Charts Section 2: Video Duration Distribution (Bar Chart) */}
      <div className="card mt-6 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-mono uppercase tracking-widest text-moss">Distribution</p>
            <h2 className="mt-1 text-xl font-medium text-sand">Video Duration Distribution</h2>
          </div>
          <span className="text-xs text-sand/50">Categorized by estimated length</span>
        </div>

        <div className="mt-6">
          <BarChart distribution={data?.duration_distribution || []} />
        </div>
      </div>

      {/* Bottom Section: Key Insights & Recent Activity */}
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        {/* Key Insights */}
        <div className="card p-6">
          <div className="flex items-center gap-2">
            <span className="text-lg">💡</span>
            <div>
              <p className="text-xs font-mono uppercase tracking-widest text-moss">Analytics Summary</p>
              <h2 className="mt-0.5 text-xl font-medium text-sand">Key Insights</h2>
            </div>
          </div>

          <ul className="mt-5 space-y-3">
            {(data?.insights || []).map((insight, idx) => (
              <li
                key={idx}
                className="flex items-start gap-3 rounded-xl border border-white/5 bg-white/[0.02] p-3.5 text-sm leading-relaxed text-sand/80"
              >
                <span className="mt-0.5 text-moss">✦</span>
                <span>{insight}</span>
              </li>
            ))}
            {(data?.insights || []).length === 0 ? (
              <p className="text-sm text-sand/50">No insights available for this timeframe.</p>
            ) : null}
          </ul>
        </div>

        {/* Recent Activity */}
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-mono uppercase tracking-widest text-moss">Activity Feed</p>
              <h2 className="mt-0.5 text-xl font-medium text-sand">Recent Activity</h2>
            </div>
            <Link href="/videos" className="text-xs text-ember hover:underline">
              View All →
            </Link>
          </div>

          <div className="mt-5 space-y-3">
            {(data?.recent_activity || []).map((act) => (
              <Link
                key={act.id}
                href={`/videos/${act.id}`}
                className="flex items-center justify-between rounded-xl border border-white/5 bg-black/40 p-3 hover:border-ember/40 hover:bg-white/[0.03] transition-all"
              >
                <div className="min-w-0 flex-1 pr-3">
                  <p className="truncate text-sm font-medium text-sand">{act.title}</p>
                  <p className="mt-0.5 text-xs text-sand/50">
                    {act.owner_name} · {act.duration} · {act.uploaded_at}
                  </p>
                </div>
                <StatusBadge status={act.status} />
              </Link>
            ))}

            {(data?.recent_activity || []).length === 0 ? (
              <p className="text-sm text-sand/50">No recent activity detected.</p>
            ) : null}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

/* StatCard Helper Component */
function StatCard({
  label,
  value,
  subtext,
  icon,
  accent,
}: {
  label: string;
  value: string | number;
  subtext: string;
  icon: string;
  accent: string;
}) {
  return (
    <div className={`card relative overflow-hidden bg-gradient-to-b p-5 border ${accent}`}>
      <div className="flex items-start justify-between">
        <p className="text-xs uppercase tracking-wider text-sand/60">{label}</p>
        <span className="text-xl">{icon}</span>
      </div>
      <p className="font-display mt-3 text-3xl font-bold tracking-tight text-sand">{value}</p>
      <p className="mt-1.5 text-xs text-sand/40">{subtext}</p>
    </div>
  );
}

/* LineChart SVG Component */
function LineChart({
  overTime,
}: {
  overTime: { date: string; uploaded: number; completed: number; failed: number }[];
}) {
  if (!overTime || overTime.length === 0) {
    return <p className="py-12 text-center text-xs text-sand/40">No time-series data available.</p>;
  }

  const maxVal = Math.max(...overTime.map((d) => Math.max(d.uploaded, d.completed, 1)), 5);
  const width = 600;
  const height = 180;
  const padding = 30;
  const graphW = width - padding * 2;
  const graphH = height - padding * 2;

  const pointsUploaded = overTime.map((d, idx) => {
    const x = padding + (idx / Math.max(overTime.length - 1, 1)) * graphW;
    const y = height - padding - (d.uploaded / maxVal) * graphH;
    return `${x},${y}`;
  });

  const pointsCompleted = overTime.map((d, idx) => {
    const x = padding + (idx / Math.max(overTime.length - 1, 1)) * graphW;
    const y = height - padding - (d.completed / maxVal) * graphH;
    return `${x},${y}`;
  });

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full min-w-[480px]">
        {/* Horizontal Gridlines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const y = height - padding - ratio * graphH;
          const val = Math.round(ratio * maxVal);
          return (
            <g key={ratio}>
              <line
                x1={padding}
                y1={y}
                x2={width - padding}
                y2={y}
                stroke="currentColor"
                strokeOpacity={0.08}
                strokeDasharray="4 4"
              />
              <text x={padding - 8} y={y + 3} textAnchor="end" fill="currentColor" fillOpacity={0.3} fontSize="9">
                {val}
              </text>
            </g>
          );
        })}

        {/* Uploaded Area & Line */}
        <polyline fill="none" stroke="#3B82F6" strokeWidth="2.5" points={pointsUploaded.join(" ")} />
        {/* Completed Area & Line */}
        <polyline fill="none" stroke="#10B981" strokeWidth="2.5" points={pointsCompleted.join(" ")} />

        {/* Interactive Vertex Dots */}
        {overTime.map((d, idx) => {
          const x = padding + (idx / Math.max(overTime.length - 1, 1)) * graphW;
          const yUp = height - padding - (d.uploaded / maxVal) * graphH;
          const yComp = height - padding - (d.completed / maxVal) * graphH;
          return (
            <g key={idx}>
              <circle cx={x} cy={yUp} r="4" fill="#3B82F6" stroke="#000" strokeWidth="1.5" />
              <circle cx={x} cy={yComp} r="4" fill="#10B981" stroke="#000" strokeWidth="1.5" />
              {/* Date X Label */}
              <text
                x={x}
                y={height - 8}
                textAnchor="middle"
                fill="currentColor"
                fillOpacity={0.4}
                fontSize="9"
              >
                {d.date}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

/* DonutChart SVG Component */
function DonutChart({
  statusData,
  total,
}: {
  statusData: { name: string; value: number; color: string }[];
  total: number;
}) {
  const size = 160;
  const strokeWidth = 18;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  let cumulativeOffset = 0;
  const safeTotal = total > 0 ? total : 1;

  const slices = statusData.map((item) => {
    const pct = item.value / safeTotal;
    const strokeDasharray = `${pct * circumference} ${circumference}`;
    const strokeDashoffset = -cumulativeOffset;
    cumulativeOffset += pct * circumference;
    return { ...item, strokeDasharray, strokeDashoffset, pct: Math.round(pct * 100) };
  });

  return (
    <div className="flex flex-col items-center gap-5 w-full">
      <div className="relative flex items-center justify-center">
        <svg width={size} height={size} className="-rotate-90">
          {slices.map((slice, idx) => (
            <circle
              key={idx}
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="transparent"
              stroke={slice.color}
              strokeWidth={strokeWidth}
              strokeDasharray={slice.strokeDasharray}
              strokeDashoffset={slice.strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
          ))}
        </svg>

        {/* Center label */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-display text-2xl font-bold text-sand">{total}</span>
          <span className="text-[10px] uppercase tracking-wider text-sand/50">Videos</span>
        </div>
      </div>

      {/* Legend */}
      <div className="w-full space-y-2">
        {statusData.map((s, idx) => (
          <div key={idx} className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: s.color }} />
              <span className="text-sand/80">{s.name}</span>
            </div>
            <span className="font-mono text-sand/60">
              {s.value} ({total > 0 ? Math.round((s.value / total) * 100) : 0}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* BarChart SVG Component */
function BarChart({
  distribution,
}: {
  distribution: { range: string; count: number }[];
}) {
  const maxCount = Math.max(...distribution.map((d) => d.count), 1);

  return (
    <div className="grid grid-cols-5 gap-3 pt-4">
      {distribution.map((item, idx) => {
        const heightPct = Math.max((item.count / maxCount) * 100, 8);
        return (
          <div key={idx} className="flex flex-col items-center gap-2">
            {/* Bar container */}
            <div className="relative flex h-36 w-full items-end justify-center rounded-xl border border-white/5 bg-black/40 p-1.5">
              <div
                className="w-full rounded-lg bg-gradient-to-t from-moss/30 via-moss/60 to-moss transition-all duration-500 hover:brightness-125"
                style={{ height: `${heightPct}%` }}
              >
                <div className="pt-1 text-center font-mono text-[10px] font-bold text-white">
                  {item.count}
                </div>
              </div>
            </div>
            {/* X-label */}
            <span className="text-center font-mono text-xs text-sand/60">{item.range}</span>
          </div>
        );
      })}
    </div>
  );
}
