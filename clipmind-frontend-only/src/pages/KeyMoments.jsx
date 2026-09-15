import React, { useRef, useState } from "react";

const keyMoments = [
  {
    id: 1,
    topic: "Introduction",
    start: 0,
    end: 60,
    transcript: "Introduction to the video and the main concepts discussed.",
    importance: 0.95,
  },
  {
    id: 2,
    topic: "Main Concept",
    start: 90,
    end: 180,
    transcript: "The important concept discussed in this section.",
    importance: 0.89,
  },
  {
    id: 3,
    topic: "Important Example",
    start: 240,
    end: 330,
    transcript: "An important example explaining the concept.",
    importance: 0.84,
  },
  {
    id: 4,
    topic: "Conclusion",
    start: 420,
    end: 500,
    transcript: "Summary and conclusion of the discussed topic.",
    importance: 0.78,
  },
];

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);

  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(
    2,
    "0"
  )}`;
}

export default function KeyMoments() {
  const videoRef = useRef(null);
  const [selectedMoment, setSelectedMoment] = useState(null);

  const handleTimestampClick = (moment) => {
    if (videoRef.current) {
      videoRef.current.currentTime = moment.start;
      videoRef.current.play();
    }

    setSelectedMoment(moment.id);
  };

  return (
    <div className="key-moments-page">
      <h1>Key Moments</h1>

      <p className="page-description">
        Important topics and moments detected from the video.
      </p>

      {/* Video Player */}
      <div className="video-section">
        <video
          ref={videoRef}
          controls
          width="100%"
          className="video-player"
        >
          {/* Backend se actual video URL aayega */}
          <source src="" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>

      {/* Key Moments */}
      <div className="moments-section">
        <h2>Important Moments</h2>

        {keyMoments.map((moment) => (
          <div
            key={moment.id}
            className={`moment-card ${
              selectedMoment === moment.id ? "selected" : ""
            }`}
          >
            <div className="moment-header">
              <h3>{moment.topic}</h3>

              <button
                className="timestamp-button"
                onClick={() => handleTimestampClick(moment)}
              >
                ▶ {formatTime(moment.start)}
              </button>
            </div>

            <p>{moment.transcript}</p>

            <div className="moment-footer">
              <span>
                {formatTime(moment.start)} - {formatTime(moment.end)}
              </span>

              <span>
                Importance: {(moment.importance * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}