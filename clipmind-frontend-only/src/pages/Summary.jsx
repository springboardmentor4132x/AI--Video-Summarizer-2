import React, { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import "./Summary.css";

function Summary() {
  const { videoId } = useParams();
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const status = summary?.status || (loading ? "loading" : "not_started");
  const statusLabel = {
    not_started: "Not Started",
    processing: "Processing",
    completed: "Completed",
    failed: "Failed",
  }[status] || status;

  const loadSummary = useCallback(() => {
    if (!videoId) return;
    api
      .getSummary(videoId)
      .then((data) => {
        setSummary(data);
        setError("");
      })
      .catch((err) => {
        if (err.message.toLowerCase().includes("no summary") || err.message.toLowerCase().includes("no transcript")) {
          setSummary(null);
        } else {
          setError(err.message);
        }
      })
      .finally(() => setLoading(false));
  }, [videoId]);

  useEffect(() => {
    loadSummary();
    const interval = setInterval(() => {
      if (summary?.status === "processing" || !summary) {
        loadSummary();
      }
    }, 4000);
    return () => clearInterval(interval);
  }, [loadSummary, summary?.status]);

  const handleGenerate = () => {
    setError("");
    setLoading(true);
    api
      .generateSummary(videoId)
      .then((res) => setSummary(res.summary))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  if (!videoId) {
    return (
      <div className="summary-page">
        <h1>AI Summary</h1>
        <p>
          Koi video select nahi hui hai. Pehle{" "}
          <Link to="/history">History</Link> page se ek video chuno.
        </p>
      </div>
    );
  }

  return (
    <div className="summary-page">
      <div className="summary-header">
        <div>
          <h1>AI Summary</h1>
          <p>Understand the important points from your video</p>
        </div>
        <div className={`summary-status ${statusLabel.toLowerCase()}`}>
          {status === "completed" && "✓ "}
          {statusLabel}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {(status === "not_started" || status === "failed") && (
        <button className="regenerate-button" onClick={handleGenerate} disabled={loading}>
          {status === "failed" ? "Try Again" : "Generate Summary"}
        </button>
      )}

      {status === "processing" && (
        <div className="summary-processing">
          <div className="loader"></div>
          <div>
            <h3>Generating summary...</h3>
            <p>AI is analyzing your transcript. Please wait, is page ko khula rehne do.</p>
          </div>
        </div>
      )}

      {status === "failed" && summary?.error_message && (
        <div className="summary-failed">
          <h3>Summary generation failed</h3>
          <p>{summary.error_message}</p>
        </div>
      )}

      {status === "completed" && (
        <>
          <div className="summary-card short-summary">
            <div className="summary-card-title">
              <div>
                <h2>Short Summary</h2>
                <p>Quick overview of the video</p>
              </div>
            </div>
            <p className="summary-text">{summary.short_summary}</p>
          </div>

          <div className="summary-card">
            <div className="summary-card-title">
              <div>
                <h2>Detailed Summary</h2>
                <p>Main concepts discussed in the video</p>
              </div>
              <button className="regenerate-button" onClick={handleGenerate} disabled={loading}>
                Regenerate
              </button>
            </div>
            <div className="detailed-summary">
              <p>{summary.detailed_summary}</p>
            </div>
          </div>

          <div className="summary-footer">
            ✓ Summary generated successfully
            <span>Last generated: {new Date(summary.updated_at).toLocaleString()}</span>
          </div>
        </>
      )}
    </div>
  );
}

export default Summary;