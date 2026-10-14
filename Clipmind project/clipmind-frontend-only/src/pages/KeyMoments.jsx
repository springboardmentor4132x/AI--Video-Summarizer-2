/* import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

function KeyMoments() {
  const { videoId } = useParams();  // route: /keymoments/:videoId
  const videoRef = useRef(null);

  const [status, setStatus] = useState("NOT_STARTED");
  const [topics, setTopics] = useState([]);
  const [keyMoments, setKeyMoments] = useState([]);
  const [selectedMoment, setSelectedMoment] = useState(null);

  const fetchData = async () => {
    const data = await api.getKeyMoments(videoId);
    setStatus(data.status);
    setTopics(data.topics);
    setKeyMoments(data.key_moments);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 4000); // har 4 second mein status check karo jab tak processing hai
    return () => clearInterval(interval);
  }, [videoId]);

  const playAt = (seconds, moment) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
    setSelectedMoment(moment);
  };

  return (
    <div className="module-page">
      <div className="module-header">
        <p className="module-label">MODULE 3</p>
        <h1>Key Moments Detection</h1>
        <p>View important topics and key moments detected from your video.</p>
      </div>

      <div className="module-card">
        <h2>Video Player</h2>
        <video ref={videoRef} controls width="100%" style={{ borderRadius: "12px", marginTop: "15px" }}>
          <source src={`http://127.0.0.1:8000/uploads/${videoId}`} type="video/mp4" />
        </video>
      </div>

      {status !== "COMPLETED" && (
        <div className="module-card">
          <p>Status: {status === "PROCESSING" ? "Detecting key moments..." : status}</p>
        </div>
      )}

      {status === "COMPLETED" && (
        <>
          <div className="module-card">
            <h2>Topics</h2>
            <div className="moment-list">
              {topics.map((topic, index) => (
                <div key={index} className="moment-item" onClick={() => playAt(topic.start_time, topic)}>
                  <strong>{Math.floor(topic.start_time / 60)}:{String(topic.start_time % 60).padStart(2, "0")}</strong>
                  <span>{topic.title}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="module-card">
            <h2>Key Moments</h2>
            <div className="moment-list">
              {keyMoments.map((moment, index) => (
                <div
                  key={index}
                  className={`moment-item ${selectedMoment?.start_time === moment.start_time ? "selected" : ""}`}
                  onClick={() => playAt(moment.start_time, moment)}
                >
                  <div className="moment-star">⭐</div>
                  <span>{Math.floor(moment.start_time / 60)}:{String(moment.start_time % 60).padStart(2, "0")}</span>
                  <span>{moment.text.slice(0, 60)}...</span>
                  <div className="importance-score">Score: {moment.score}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default KeyMoments; */





/*
import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

function KeyMoments() {
  const { videoId } = useParams();  // route: /keymoments/:videoId
  const videoRef = useRef(null);

  const [videoFile, setVideoFile] = useState(null);
  const [status, setStatus] = useState("NOT_STARTED");
  const [topics, setTopics] = useState([]);
  const [keyMoments, setKeyMoments] = useState([]);
  const [selectedMoment, setSelectedMoment] = useState(null);
  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      // 1. Video ki details lao (asli filename ke liye, taaki player sahi file load kare)
      const videoInfo = await api.videoStatus(videoId);
      setVideoFile(videoInfo.video_file);

      // 2. Key moments data lao
      const data = await api.getKeyMoments(videoId);
      setStatus(data.status);
      setTopics(data.topics);
      setKeyMoments(data.key_moments);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 4000); // har 4 second mein status check karo jab tak processing hai
    return () => clearInterval(interval);
  }, [videoId]);

  const playAt = (seconds, moment) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
    setSelectedMoment(moment);
  };

  return (
    <div className="module-page">
      <div className="module-header">
        <p className="module-label">MODULE 3</p>
        <h1>Key Moments Detection</h1>
        <p>View important topics and key moments detected from your video.</p>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="module-card">
        <h2>Video Player</h2>
        {videoFile ? (
          <video ref={videoRef} controls width="100%" style={{ borderRadius: "12px", marginTop: "15px" }}>
            <source src={`http://127.0.0.1:8000/uploads/${videoFile}`} type="video/mp4" />
          </video>
        ) : (
          <p>Video load ho rahi hai...</p>
        )}
      </div>

      {status !== "COMPLETED" && (
        <div className="module-card">
          <p>Status: {status === "PROCESSING" ? "Detecting key moments..." : status}</p>
        </div>
      )}

      {status === "COMPLETED" && (
        <>
          <div className="module-card">
            <h2>Topics</h2>
            <div className="moment-list">
              {topics.map((topic, index) => (
                <div key={index} className="moment-item" onClick={() => playAt(topic.start_time, topic)}>
                  <strong>{Math.floor(topic.start_time / 60)}:{String(topic.start_time % 60).padStart(2, "0")}</strong>
                  <span>{topic.title}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="module-card">
            <h2>Key Moments</h2>
            <div className="moment-list">
              {keyMoments.map((moment, index) => (
                <div
                  key={index}
                  className={`moment-item ${selectedMoment?.start_time === moment.start_time ? "selected" : ""}`}
                  onClick={() => playAt(moment.start_time, moment)}
                >
                  <div className="moment-star">⭐</div>
                  <span>{Math.floor(moment.start_time / 60)}:{String(moment.start_time % 60).padStart(2, "0")}</span>
                  <span>{moment.text.slice(0, 60)}...</span>
                  <div className="importance-score">Score: {moment.score}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default KeyMoments; */









/*import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";

function KeyMoments() {
  const { videoId } = useParams();  // route: /keymoments/:videoId
  const videoRef = useRef(null);

  const [videoFile, setVideoFile] = useState(null);
  const [status, setStatus] = useState("NOT_STARTED");
  const [topics, setTopics] = useState([]);
  const [keyMoments, setKeyMoments] = useState([]);
  const [selectedMoment, setSelectedMoment] = useState(null);
  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      // 1. Video ki details lao (asli filename ke liye, taaki player sahi file load kare)
      const videoInfo = await api.videoStatus(videoId);
      setVideoFile(videoInfo.video_file);

      // 2. Key moments data lao
      const data = await api.getKeyMoments(videoId);
      setStatus(data.status);
      setTopics(data.topics);
      setKeyMoments(data.key_moments);
    } catch (err) {
      setError(err.message);
    }
  };

  // NAYA FUNCTION: pehle generation trigger karo, warna status hamesha NOT_STARTED rahega
  const startGeneration = async () => {
    try {
      await api.generateKeyMoments(videoId); // yeh missing call thi
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    startGeneration(); // generation start karo
    const interval = setInterval(() => {
      fetchData(); // fir har 4 second status poll karte raho
    }, 4000);
    return () => clearInterval(interval);
  }, [videoId]);

  const playAt = (seconds, moment) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
    setSelectedMoment(moment);
  };

  return (
    <div className="module-page">
      <div className="module-header">
        <p className="module-label">MODULE 3</p>
        <h1>Key Moments Detection</h1>
        <p>View important topics and key moments detected from your video.</p>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="module-card">
        <h2>Video Player</h2>
        {videoFile ? (
          <video ref={videoRef} controls width="100%" style={{ borderRadius: "12px", marginTop: "15px" }}>
            <source src={`http://127.0.0.1:8000/uploads/${videoFile}`} type="video/mp4" />
          </video>
        ) : (
          <p>Video load ho rahi hai...</p>
        )}
      </div>

      {status !== "COMPLETED" && (
        <div className="module-card">
          <p>Status: {status === "PROCESSING" ? "Detecting key moments..." : status}</p>
        </div>
      )}

      {status === "COMPLETED" && (
        <>
          <div className="module-card">
            <h2>Topics</h2>
            <div className="moment-list">
              {topics.map((topic, index) => (
                <div key={index} className="moment-item" onClick={() => playAt(topic.start_time, topic)}>
                  <strong>{Math.floor(topic.start_time / 60)}:{String(topic.start_time % 60).padStart(2, "0")}</strong>
                  <span>{topic.title}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="module-card">
            <h2>Key Moments</h2>
            <div className="moment-list">
              {keyMoments.map((moment, index) => (
                <div
                  key={index}
                  className={`moment-item ${selectedMoment?.start_time === moment.start_time ? "selected" : ""}`}
                  onClick={() => playAt(moment.start_time, moment)}
                >
                  <div className="moment-star">⭐</div>
                  <span>{Math.floor(moment.start_time / 60)}:{String(moment.start_time % 60).padStart(2, "0")}</span>
                  <span>{moment.text.slice(0, 60)}...</span>
                  <div className="importance-score">Score: {moment.score}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default KeyMoments;   */











import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import "./KeyMoments.css";
 
// Kisi topic ke andar agar koi high-importance key moment aata hai,
// to us topic ko "important" maan kar highlight karte hain.
function isImportantTopic(topic, keyMoments) {
  return keyMoments.some(
    (m) => m.start_time >= topic.start_time && m.start_time <= topic.end_time
  );
}
 
function formatTime(seconds) {
  const s = Math.max(0, Math.floor(seconds || 0));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
 
function KeyMoments() {
  const { videoId } = useParams(); // route: /keymoments/:videoId
  const videoRef = useRef(null);
 
  const [videoFile, setVideoFile] = useState(null);
  const [status, setStatus] = useState("NOT_STARTED");
  const [topics, setTopics] = useState([]);
  const [keyMoments, setKeyMoments] = useState([]);
  const [selectedMoment, setSelectedMoment] = useState(null);
  const [error, setError] = useState("");
 
  const fetchData = async () => {
    try {
      // 1. Video ki details lao (asli filename ke liye, taaki player sahi file load kare)
      const videoInfo = await api.videoStatus(videoId);
      setVideoFile(videoInfo.video_file);
 
      // 2. Key moments data lao
      const data = await api.getKeyMoments(videoId);
      setStatus(data.status);
      setTopics(data.topics || []);
      setKeyMoments(data.key_moments || []);
    } catch (err) {
      setError(err.message);
    }
  };
 
  // Pehle generation trigger karo, warna status hamesha NOT_STARTED rahega
  const startGeneration = async () => {
    try {
      await api.generateKeyMoments(videoId);
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };
 
  useEffect(() => {
    startGeneration();
    const interval = setInterval(() => {
      fetchData();
    }, 4000); // har 4 second status poll karte raho
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoId]);
 
  const playAt = (seconds, moment) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
    setSelectedMoment(moment);
  };
 
  return (
    <div className="keymoments-page">
      <div className="keymoments-header">
        <div>
          <p className="module-label">MODULE 3</p>
          <h1>Key Moments Detection</h1>
          <p>Important topics aur moments jo video mein detect hue hain.</p>
        </div>
        <span
          className={`status-badge ${
            status === "COMPLETED" ? "completed" : status === "FAILED" ? "failed" : "processing"
          }`}
        >
          {status === "COMPLETED" ? "Ready" : status === "PROCESSING" ? "Processing..." : status}
        </span>
      </div>
 
      {error && <div className="error">{error}</div>}
 
      <div className="keymoments-layout">
        {/* ---------- Left: Sticky video player ---------- */}
        <div className="video-sidebar">
          <h2>Video</h2>
          {videoFile ? (
            <video ref={videoRef} controls className="km-video">
              <source src={`http://127.0.0.1:8000/uploads/${videoFile}`} type="video/mp4" />
            </video>
          ) : (
            <p>Video load ho rahi hai...</p>
          )}
          {selectedMoment && (
            <div className="now-playing">
              <span className="now-playing-label">Playing:</span>
              <p>{selectedMoment.title || selectedMoment.text}</p>
            </div>
          )}
        </div>
 
        {/* ---------- Right: Scrollable topics + key moments ---------- */}
        <div className="content-area">
          {status !== "COMPLETED" && (
            <div className="keymoments-card">
              {status === "PROCESSING" && <p>Detecting key moments...</p>}
              {status === "FAILED" && (
                <>
                  <p>
                    <strong>Key moments generate nahi ho paye.</strong> Aksar iski wajah yeh hoti hai ki
                    is video ka <strong>transcript abhi complete nahi hua hai</strong>.
                  </p>
                  <p>
                    Pehle <a href={`/transcript/${videoId}`}>Transcript page</a> par jaakar transcript ko
                    "Completed" hone ka wait karein, fir yahan wapas aakar dobara try karein.
                  </p>
                </>
              )}
              {status === "NOT_STARTED" && <p>Shuru ho raha hai...</p>}
            </div>
          )}
 
          {status === "COMPLETED" && (
            <>
              <div className="keymoments-card">
                <h2>Topics</h2>
                <div className="moment-list">
                  {topics.map((topic, index) => {
                    const important = isImportantTopic(topic, keyMoments);
                    return (
                      <div
                        key={index}
                        className={`moment-item ${important ? "important" : ""} ${
                          selectedMoment?.start_time === topic.start_time ? "selected" : ""
                        }`}
                        onClick={() => playAt(topic.start_time, topic)}
                      >
                        <span className="moment-time">{formatTime(topic.start_time)}</span>
                        <span className="moment-text">{topic.title}</span>
                        {important && <span className="important-badge">⭐ Important</span>}
                      </div>
                    );
                  })}
                  {topics.length === 0 && <p className="empty-note">Koi topic nahi mila.</p>}
                </div>
              </div>
 
              <div className="keymoments-card">
                <h2>Key Moments</h2>
                <div className="moment-list">
                  {keyMoments.map((moment, index) => (
                    <div
                      key={index}
                      className={`moment-item important ${
                        selectedMoment?.start_time === moment.start_time ? "selected" : ""
                      }`}
                      onClick={() => playAt(moment.start_time, moment)}
                    >
                      <span className="moment-star">⭐</span>
                      <span className="moment-time">{formatTime(moment.start_time)}</span>
                      <span className="moment-text">{moment.text.slice(0, 90)}...</span>
                      <span className="importance-score">{Math.round(moment.score * 100)}%</span>
                    </div>
                  ))}
                  {keyMoments.length === 0 && <p className="empty-note">Koi key moment nahi mila.</p>}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
 
export default KeyMoments;
