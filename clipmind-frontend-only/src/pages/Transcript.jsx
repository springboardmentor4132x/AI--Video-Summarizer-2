import React, { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api.js";
import "./Transcript.css";

function Transcript() {
  const { videoId } = useParams();
  const [transcript, setTranscript] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const status = transcript?.status || (loading ? "loading" : "not_started");
  const statusLabel = {
    not_started: "Not Started",
    processing: "Processing",
    completed: "Completed",
    failed: "Failed",
  }[status] || status;

  const loadTranscript = useCallback(() => {
    if (!videoId) return;
    api
      .getTranscript(videoId)
      .then((data) => {
        setTranscript(data);
        setError("");
      })
      .catch((err) => {
        if (err.message.toLowerCase().includes("no transcript")) {
          setTranscript(null);
        } else {
          setError(err.message);
        }
      })
      .finally(() => setLoading(false));
  }, [videoId]);

  useEffect(() => {
    loadTranscript();
    const interval = setInterval(() => {
      if (transcript?.status === "processing" || !transcript) {
        loadTranscript();
      }
    }, 4000);
    return () => clearInterval(interval);
  }, [loadTranscript, transcript?.status]);

  const handleGenerate = () => {
    setError("");
    setLoading(true);
    api
      .generateTranscript(videoId)
      .then((res) => setTranscript(res.transcript))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  if (!videoId) {
    return (
      <div className="transcript-page">
        <h1>Transcript</h1>
        <p>
          Koi video select nahi hui hai. Pehle{" "}
          <Link to="/history">History</Link> page se ek video chuno.
        </p>
      </div>
    );
  }

  return (
    <div className="transcript-page">
      <div className="transcript-header">
        <div>
          <h1>Transcript</h1>
          <p>View the generated transcript of your video</p>
        </div>
        <div className={`status-badge ${statusLabel.toLowerCase()}`}>
          {status === "completed" && "✓ "}
          {statusLabel}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {(status === "not_started" || status === "loading") && !loading && (
        <div className="processing-box">
          <div>
            <strong>Transcript abhi generate nahi hua hai.</strong>
            <p>Neeche button dabakar transcript generation shuru karo.</p>
          </div>
        </div>
      )}

      {(status === "not_started" || status === "failed") && (
        <button className="summary-button" onClick={handleGenerate} disabled={loading}>
          {status === "failed" ? "Try Again" : "Generate Transcript"}
        </button>
      )}

      {status === "processing" && (
        <div className="processing-box">
          <div className="loader"></div>
          <div>
            <strong>Generating transcript...</strong>
            <p>Whisper aapki video process kar raha hai. Thoda time lagega, is page ko khula rehne do.</p>
          </div>
        </div>
      )}

      {status === "failed" && transcript?.error_message && (
        <div className="failed-box">
          <strong>Transcript generation failed</strong>
          <p>{transcript.error_message}</p>
        </div>
      )}

      {status === "completed" && (
        <div className="transcript-card">
          <div className="card-header">
            <div>
              <h2>Generated Transcript</h2>
              <p>Transcript generated from the video audio</p>
            </div>
            <Link className="summary-button" to={`/summary/${videoId}`}>
              Generate Summary
            </Link>
          </div>

          <div className="transcript-content">{transcript.transcript_text}</div>

          <div className="transcript-footer">
            <span>✓ Transcript completed</span>
            <span>Last updated: {new Date(transcript.updated_at).toLocaleString()}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default Transcript;