import React, { useEffect, useState } from "react";
import { api } from "../api";
import "./Analytics.css";
 
function formatDuration(totalSeconds) {
  const s = Math.max(0, Math.round(totalSeconds || 0));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${sec}s`;
  return `${sec}s`;
}
 
const STATUS_COLORS = {
  uploaded: "#a5b4fc",
  processing: "#f59e0b",
  completed: "#22c55e",
  failed: "#ef4444",
};
 
// ---------- Simple inline SVG donut chart (no chart library needed) ----------
function DonutChart({ data }) {
  const entries = Object.entries(data).filter(([, v]) => v > 0);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
 
  if (total === 0) {
    return <p className="empty-note">Abhi koi video upload nahi hua.</p>;
  }
 
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;
 
  return (
    <div className="donut-wrap">
      <svg viewBox="0 0 160 160" className="donut-svg">
        <circle cx="80" cy="80" r={radius} fill="none" stroke="#eee" strokeWidth="24" />
        {entries.map(([status, value]) => {
          const fraction = value / total;
          const dash = fraction * circumference;
          const circle = (
            <circle
              key={status}
              cx="80"
              cy="80"
              r={radius}
              fill="none"
              stroke={STATUS_COLORS[status] || "#ccc"}
              strokeWidth="24"
              strokeDasharray={`${dash} ${circumference - dash}`}
              strokeDashoffset={-offset}
              transform="rotate(-90 80 80)"
            />
          );
          offset += dash;
          return circle;
        })}
        <text x="80" y="85" textAnchor="middle" className="donut-center-text">
          {total}
        </text>
      </svg>
      <div className="donut-legend">
        {entries.map(([status, value]) => (
          <div key={status} className="legend-row">
            <span className="legend-dot" style={{ background: STATUS_COLORS[status] || "#ccc" }} />
            <span className="legend-label">{status}</span>
            <span className="legend-value">{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
 
// ---------- Simple inline SVG bar chart ----------
function BarChart({ items, valueKey, labelKey, color = "#4f46e5", formatValue }) {
  if (!items.length) {
    return <p className="empty-note">Data nahi hai.</p>;
  }
  const max = Math.max(1, ...items.map((i) => i[valueKey]));
 
  return (
    <div className="bar-chart">
      {items.map((item, i) => (
        <div key={i} className="bar-row">
          <span className="bar-label" title={item[labelKey]}>
            {item[labelKey]}
          </span>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{ width: `${(item[valueKey] / max) * 100}%`, background: color }}
            />
          </div>
          <span className="bar-value">
            {formatValue ? formatValue(item[valueKey]) : item[valueKey]}
          </span>
        </div>
      ))}
    </div>
  );
}
 
function Analytics() {
  const [overview, setOverview] = useState(null);
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
 
  useEffect(() => {
    Promise.all([api.getAnalyticsOverview(), api.getAnalyticsVideos()])
      .then(([overviewData, videosData]) => {
        setOverview(overviewData);
        setVideos(videosData.videos || []);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);
 
  if (loading) return <div className="analytics-page"><p>Loading analytics...</p></div>;
  if (error) return <div className="analytics-page"><div className="error">{error}</div></div>;
 
  const topByWordCount = [...videos]
    .filter((v) => v.word_count > 0)
    .sort((a, b) => b.word_count - a.word_count)
    .slice(0, 6)
    .map((v) => ({ ...v, short_name: v.filename.length > 22 ? v.filename.slice(0, 22) + "…" : v.filename }));
 
  const topByDuration = [...videos]
    .filter((v) => v.duration_seconds > 0)
    .sort((a, b) => b.duration_seconds - a.duration_seconds)
    .slice(0, 6)
    .map((v) => ({ ...v, short_name: v.filename.length > 22 ? v.filename.slice(0, 22) + "…" : v.filename }));
 
  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <p className="module-label">MILESTONE 3</p>
        <h1>Analytics</h1>
        <p>Aapke sabhi videos ka overview aur har video ki alag insights.</p>
      </div>
 
      {/* ---------- Overview stat cards ---------- */}
      <div className="stat-cards">
        <div className="stat-card">
          <span className="stat-value">{overview.total_videos}</span>
          <span className="stat-label">Total Videos</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{formatDuration(overview.total_duration_seconds)}</span>
          <span className="stat-label">Total Watch Time</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{formatDuration(overview.avg_duration_seconds)}</span>
          <span className="stat-label">Avg. Video Length</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{overview.transcripts_completed}</span>
          <span className="stat-label">Transcripts Completed</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{overview.total_words_transcribed.toLocaleString()}</span>
          <span className="stat-label">Words Transcribed</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{overview.total_topics_detected}</span>
          <span className="stat-label">Topics Detected</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{overview.total_key_moments_detected}</span>
          <span className="stat-label">Key Moments Detected</span>
        </div>
      </div>
 
      {/* ---------- Charts ---------- */}
      <div className="charts-grid">
        <div className="chart-card">
          <h2>Processing Status</h2>
          <DonutChart data={overview.status_breakdown} />
        </div>
 
        <div className="chart-card">
          <h2>Longest Videos</h2>
          <BarChart
            items={topByDuration}
            valueKey="duration_seconds"
            labelKey="short_name"
            color="#4f46e5"
            formatValue={formatDuration}
          />
        </div>
 
        <div className="chart-card">
          <h2>Most Talkative Videos (word count)</h2>
          <BarChart
            items={topByWordCount}
            valueKey="word_count"
            labelKey="short_name"
            color="#f59e0b"
          />
        </div>
      </div>
 
      {/* ---------- Per-video table ---------- */}
      <div className="video-table-card">
        <h2>Per-video Insights</h2>
        <div className="table-scroll">
          <table className="video-table">
            <thead>
              <tr>
                <th>Video</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Transcript</th>
                <th>Words</th>
                <th>Topics</th>
                <th>Key Moments</th>
              </tr>
            </thead>
            <tbody>
              {videos.map((v) => (
                <tr key={v.id}>
                  <td className="video-name-cell">{v.filename}</td>
                  <td>
                    <span className={`status-pill status-${v.status}`}>{v.status}</span>
                  </td>
                  <td>{formatDuration(v.duration_seconds)}</td>
                  <td>{v.transcript_status}</td>
                  <td>{v.word_count || "-"}</td>
                  <td>{v.topics_count}</td>
                  <td>{v.key_moments_count}</td>
                </tr>
              ))}
              {videos.length === 0 && (
                <tr>
                  <td colSpan="7" className="empty-note">Koi video upload nahi hua abhi tak.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
 
export default Analytics;
 







