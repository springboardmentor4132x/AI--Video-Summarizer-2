import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import "./Summary.css";

function Summary() {
  const { videoId } = useParams(); // route: /summary/:videoId

  const [status, setStatus] = useState("NOT_STARTED");
  const [shortSummary, setShortSummary] = useState("");
  const [topics, setTopics] = useState([]);
  const [videoName, setVideoName] = useState("");
  const [uploadedAt, setUploadedAt] = useState("");
  const [error, setError] = useState("");

  const fetchVideoInfo = async () => {
    try {
      const video = await api.videoStatus(videoId);
      setVideoName(video.filename);
      setUploadedAt(video.uploaded_at);
    } catch (err) {
      setError(err.message);
    }
  };

  const fetchSummary = async () => {
    try {
      const data = await api.getSummary(videoId); // backend: transcript status ke basis par hi COMPLETED/NOT_STARTED/PROCESSING/FAILED deta hai
      setStatus(data.status);
      setShortSummary(data.short_summary || "");
      setTopics(data.topics || []);
      return data.status;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  const startGeneration = async () => {
    // Summary khud generate nahi hoti, pehle transcript complete hona zaroori hai
    try {
      await api.generateTranscript(videoId);
      fetchSummary();
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchVideoInfo();

    fetchSummary().then((currentStatus) => {
      if (currentStatus === "NOT_STARTED") {
        startGeneration();
      }
    });

    const interval = setInterval(fetchSummary, 4000);
    return () => clearInterval(interval);
  }, [videoId]);

  const displayStatus =
    status === "COMPLETED" ? "Completed" :
    status === "PROCESSING" ? "Processing" :
    status === "FAILED" ? "Failed" : "Processing";

  return (
    <div className="summary-page">

      {/* Header */}
      <div className="summary-header">
        <div>
          <h1>AI Summary</h1>
          <p>Understand the important points from your video</p>
        </div>

        <div className={`summary-status ${displayStatus.toLowerCase()}`}>
          {displayStatus === "Completed" && "✓ "}
          {displayStatus}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      {/* Video Information */}
      <div className="summary-video-info">
        <span>Video</span>
        <h2>{videoName || "Loading..."}</h2>

        <div className="video-meta">
          <span>{uploadedAt ? new Date(uploadedAt).toLocaleString() : "-"}</span>
        </div>
      </div>

      {/* Processing */}
      {(status === "PROCESSING" || status === "NOT_STARTED") && (
        <div className="summary-processing">
          <div className="loader"></div>

          <div>
            <h3>Generating summary...</h3>
            <p>
              Pehle transcript ready ho raha hai, uske baad summary usi se
              nikali jaayegi. Please wait.
            </p>
          </div>
        </div>
      )}

      {/* Failed */}
      {status === "FAILED" && (
        <div className="summary-failed">
          <h3>Summary generation failed</h3>

          <p>
            Transcript generate nahi ho paaya, isliye summary bhi nahi ban
            saki.
          </p>

          <button onClick={startGeneration}>
            Try Again
          </button>
        </div>
      )}

      {/* Completed */}
      {status === "COMPLETED" && (
        <>
          {/* Short Summary */}
          <div className="summary-card short-summary">

            <div className="summary-card-title">
              <div>
                <h2>Short Summary</h2>
                <p>Quick overview of the video</p>
              </div>
            </div>

            <p className="summary-text">
              {shortSummary || "Summary ke liye kaafi transcript text nahi mila."}
            </p>

          </div>

          {/* Detailed Summary (topic-wise chunks) */}
          <div className="summary-card">

            <div className="summary-card-title">
              <div>
                <h2>Detailed Summary</h2>
                <p>Main concepts discussed in the video</p>
              </div>

              <button
                className="regenerate-button"
                onClick={startGeneration}
              >
                Regenerate
              </button>
            </div>

            <div className="detailed-summary">
              {topics.length === 0 && <p>Koi topics nahi mile.</p>}
              {topics.map((topic, index) => (
                <div className="summary-topic" key={index}>
                  <h3>
                    {index + 1}. {Math.floor(topic.start_time / 60)}:
                    {String(Math.floor(topic.start_time % 60)).padStart(2, "0")}
                  </h3>
                  <p>{topic.text}</p>
                </div>
              ))}
            </div>

          </div>

          {/* Footer */}
          <div className="summary-footer">
            ✓ Summary generated successfully
          </div>
        </>
      )}

    </div>
  );
}

export default Summary;