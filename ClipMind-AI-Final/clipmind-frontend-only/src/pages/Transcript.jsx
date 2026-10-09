
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import "./Transcript.css";
 
// Translation feature abhi verify nahi hua (backend/internet setup pe depend karta hai).
// Jab tak test_translate.py se confirm na ho jaye ki translation kaam kar raha hai,
// isse false hi rakhein taaki demo mein koi risk na ho.
const SHOW_LANGUAGE_PANEL = false;
 
function Transcript() {
  const { videoId } = useParams(); // route: /transcript/:videoId
 
  const [status, setStatus] = useState("NOT_STARTED");
  const [fullText, setFullText] = useState("");
  const [videoName, setVideoName] = useState("");
  const [uploadedAt, setUploadedAt] = useState("");
  const [error, setError] = useState("");
 
  // ---------- Language selector state ----------
  const [languages, setLanguages] = useState([{ code: "en", name: "English" }]);
  const [selectedLang, setSelectedLang] = useState("en");
  const [translatedCache, setTranslatedCache] = useState({}); // { hi: "...", mr: "..." }
  const [translating, setTranslating] = useState(false);
  const [translateError, setTranslateError] = useState("");
 
  const fetchVideoInfo = async () => {
    try {
      const video = await api.videoStatus(videoId);
      setVideoName(video.filename);
      setUploadedAt(video.uploaded_at);
    } catch (err) {
      setError(err.message);
    }
  };
 
  const fetchTranscript = async () => {
    try {
      const data = await api.getTranscript(videoId);
      setStatus(data.status);
      setFullText(data.full_text || "");
      return data.status;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };
 
  const startGeneration = async () => {
    try {
      await api.generateTranscript(videoId);
      fetchTranscript();
    } catch (err) {
      setError(err.message);
    }
  };
 
  const fetchLanguages = async () => {
    try {
      const data = await api.getTranscriptLanguages(videoId);
      if (data.languages && data.languages.length) {
        setLanguages([{ code: "en", name: "English" }, ...data.languages]);
      }
    } catch (err) {
      // Language list na mile to bhi English transcript to dikhta hi rahega
    }
  };
 
  useEffect(() => {
    fetchVideoInfo();
    fetchLanguages();
 
    // Pehle current status check karo, agar kabhi generate hi nahi hua to start karo
    fetchTranscript().then((currentStatus) => {
      if (currentStatus === "NOT_STARTED") {
        startGeneration();
      }
    });
 
    // Har 4 second mein status poll karte raho (jab tak processing/failed/completed na ho)
    const interval = setInterval(fetchTranscript, 4000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoId]);
 
  // Naya video open hone par language selection English par reset karo
  useEffect(() => {
    setSelectedLang("en");
    setTranslatedCache({});
  }, [videoId]);
 
  const handleSelectLanguage = async (code) => {
    setSelectedLang(code);
    setTranslateError("");
 
    if (code === "en" || translatedCache[code]) return; // already have it, no need to call API again
 
    setTranslating(true);
    try {
      const data = await api.translateTranscript(videoId, code);
      setTranslatedCache((prev) => ({ ...prev, [code]: data.translated_text }));
    } catch (err) {
      setTranslateError(err.message);
      setSelectedLang("en"); // fail hone par wapas English par
    } finally {
      setTranslating(false);
    }
  };
 
  const displayStatus =
    status === "COMPLETED" ? "Completed" :
    status === "PROCESSING" ? "Processing" :
    status === "FAILED" ? "Failed" : "Processing";
 
  const shownText = selectedLang === "en" ? fullText : translatedCache[selectedLang];
 
  return (
    <div className="transcript-page">
 
      {/* Header */}
      <div className="transcript-header">
        <div>
          <h1>Transcript</h1>
          <p>View the generated transcript of your video</p>
        </div>
 
        <div className={`status-badge ${displayStatus.toLowerCase()}`}>
          {displayStatus === "Completed" && "✓ "}
          {displayStatus}
        </div>
      </div>
 
      {error && <div className="error">{error}</div>}
 
      {/* Video Information */}
      <div className="video-details">
        <div>
          <span>Video Name</span>
          <p>{videoName || "Loading..."}</p>
        </div>
 
        <div>
          <span>Uploaded</span>
          <p>{uploadedAt ? new Date(uploadedAt).toLocaleString() : "-"}</p>
        </div>
      </div>
 
      {/* Processing / Not started message */}
      {(status === "PROCESSING" || status === "NOT_STARTED") && (
        <div className="processing-box">
          <div className="loader"></div>
          <div>
            <strong>Generating transcript...</strong>
            <p>
              Aapke video ki audio se Whisper (local ML model) transcript
              nikaal raha hai. Video jitna lamba hoga utna time lagega.
            </p>
          </div>
        </div>
      )}
 
      {/* Failed message */}
      {status === "FAILED" && (
        <div className="failed-box">
          <strong>Transcript generation failed</strong>
          <p>
            Kuch galat ho gaya (shayad video mein audio nahi hai, ya ffmpeg/whisper
            error aaya). Dobara try karo.
          </p>
 
          <button onClick={startGeneration}>
            Try Again
          </button>
        </div>
      )}
 
      {/* Transcript + language panel */}
      {/* Translation feature abhi verify nahi hua (internet/library issue), isliye
          demo ke liye safely hide kar diya hai. SHOW_LANGUAGE_PANEL ko true karke
          wapas on kar sakte ho jab translation test ho jaye. */}
      {status === "COMPLETED" && (
        <div className={SHOW_LANGUAGE_PANEL ? "transcript-body" : ""}>
          <div className="transcript-card">
 
            <div className="card-header">
              <div>
                <h2>Generated Transcript</h2>
                <p>
                  {selectedLang === "en"
                    ? "Transcript generated from the video audio"
                    : `Translated view (${languages.find((l) => l.code === selectedLang)?.name || selectedLang})`}
                </p>
              </div>
 
              <button
                className="summary-button"
                onClick={() => {
                  window.location.href = `/summary/${videoId}`;
                }}
              >
                View Summary
              </button>
            </div>
 
            {translateError && <div className="error">{translateError}</div>}
 
            <div className="transcript-content">
              {translating
                ? "Translate ho raha hai..."
                : shownText || "Transcript khaali hai — video mein koi bolne wali audio detect nahi hui."}
            </div>
 
            <div className="transcript-footer">
              <span>✓ Transcript completed</span>
            </div>
 
          </div>
 
          {/* ---------- Right side: language selector ---------- */}
          {SHOW_LANGUAGE_PANEL && (
            <div className="language-panel">
              <h3>View in language</h3>
              <p className="language-panel-note">
                Transcript hamesha English mein generate hota hai — yahan sirf
                dekhne ke liye translate hota hai.
              </p>
              <div className="language-list">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    className={`language-item ${selectedLang === lang.code ? "active" : ""}`}
                    onClick={() => handleSelectLanguage(lang.code)}
                    disabled={translating}
                  >
                    {lang.name}
                    {lang.code === "en" && <span className="original-tag">Original</span>}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
 
    </div>
  );
}
 
export default Transcript;
