
import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import "./Assistant.css";
 
function formatTime(seconds) {
  const s = Math.max(0, Math.floor(seconds || 0));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
 
// Browser ka built-in speech recognition (free, no paid API)
const SpeechRecognitionAPI =
  typeof window !== "undefined" && (window.SpeechRecognition || window.webkitSpeechRecognition);
 
const SUGGESTIONS = [
  "Is video ka summary kya hai?",
  "Sabse important key moments kaunse hain?",
  "Video kitni lambi hai?",
];
 
function Assistant() {
  const { videoId } = useParams(); // route: /assistant/:videoId
  const videoRef = useRef(null);
  const recognitionRef = useRef(null);
  const chatEndRef = useRef(null);
 
  const [videoFile, setVideoFile] = useState(null);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text:
        "Namaste! Main is video ka AI assistant hoon. Aap mujhse iska summary, transcript, ya key moments ke baare mein kuch bhi pooch sakte hain.",
    },
  ]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");
 
  useEffect(() => {
    api
      .videoStatus(videoId)
      .then((info) => setVideoFile(info.video_file))
      .catch((err) => setError(err.message));
  }, [videoId]);
 
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);
 
  // ---------- Voice input setup ----------
  useEffect(() => {
    if (!SpeechRecognitionAPI) return;
    const recognition = new SpeechRecognitionAPI();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
 
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuestion(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
 
    recognitionRef.current = recognition;
  }, []);
 
  const toggleListening = () => {
    if (!SpeechRecognitionAPI) {
      setError("Aapka browser voice input support nahi karta. Chrome try karein.");
      return;
    }
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      setError("");
      recognitionRef.current.start();
      setListening(true);
    }
  };
 
  const jumpTo = (seconds) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
  };
 
  const sendQuestion = async (text) => {
    const q = (text ?? question).trim();
    if (!q || loading) return;
 
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setQuestion("");
    setLoading(true);
    setError("");
 
    try {
      const result = await api.askAssistant(videoId, q);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: result.answer,
          matched_segments: result.matched_segments || [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Maaf kijiye, abhi jawab nahi de paaya. Dobara try karein." },
      ]);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
 
  const handleSubmit = (e) => {
    e.preventDefault();
    sendQuestion();
  };
 
  return (
    <div className="assistant-page">
      <div className="assistant-header">
        <div>
          <p className="module-label">AI ASSISTANT</p>
          <h1>Ask about this video 🤖</h1>
          <p>Transcript, summary aur key moments ke baare mein kuch bhi poochein.</p>
        </div>
      </div>
 
      <div className="assistant-layout">
        {/* ---------- Left: sticky video ---------- */}
        <div className="video-sidebar">
          <h2>Video</h2>
          {videoFile ? (
            <video ref={videoRef} controls className="km-video">
              <source src={`http://127.0.0.1:8000/uploads/${videoFile}`} type="video/mp4" />
            </video>
          ) : (
            <p>Video load ho rahi hai...</p>
          )}
        </div>
 
        {/* ---------- Right: chat ---------- */}
        <div className="chat-card">
          <div className="chat-topbar">
            <div className="bot-avatar">🤖</div>
            <div>
              <div className="bot-name">ClipMind Assistant</div>
              <div className="bot-status">
                <span className="status-dot" /> Online — transcript, summary aur key moments ke saath ready
              </div>
            </div>
          </div>
 
          <div className="chat-window">
            {messages.map((m, i) => (
              <div key={i} className={`chat-row ${m.role}`}>
                <div className="chat-avatar">{m.role === "assistant" ? "🤖" : "🧑"}</div>
                <div className={`chat-bubble ${m.role}`}>
                  <p>{m.text}</p>
                  {m.matched_segments && m.matched_segments.length > 0 && (
                    <div className="chat-segments">
                      {m.matched_segments.map((seg, j) => (
                        <button key={j} className="segment-chip" onClick={() => jumpTo(seg.start_time)}>
                          ▶ {formatTime(seg.start_time)}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-row assistant">
                <div className="chat-avatar">🤖</div>
                <div className="chat-bubble assistant">
                  <p className="typing">Assistant type kar raha hai...</p>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
 
          {error && <div className="error">{error}</div>}
 
          <div className="suggestions">
            {SUGGESTIONS.map((s, i) => (
              <button key={i} className="suggestion-chip" onClick={() => sendQuestion(s)} disabled={loading}>
                {s}
              </button>
            ))}
          </div>
 
          <form className="chat-input-row" onSubmit={handleSubmit}>
            <button
              type="button"
              className={`mic-button ${listening ? "listening" : ""}`}
              onClick={toggleListening}
              title={SpeechRecognitionAPI ? "Bol kar poochein" : "Voice input supported nahi hai"}
            >
              🎤
            </button>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Apna sawaal yahan likhein ya bolein..."
            />
            <button type="submit" className="send-button" disabled={loading || !question.trim()}>
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
 
export default Assistant;
