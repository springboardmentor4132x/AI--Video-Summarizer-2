import React, { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import "./SelfAssessment.css";
 
function formatTime(seconds) {
  const s = Math.max(0, Math.floor(seconds || 0));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}
 
function SelfAssessment() {
  const { videoId } = useParams(); // route: /quiz/:videoId
  const videoRef = useRef(null);
 
  const [videoFile, setVideoFile] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // { [questionId]: optionId }
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
 
  const loadQuiz = () => {
    setLoading(true);
    setError("");
    setAnswers({});
    api
      .getQuiz(videoId)
      .then((data) => setQuestions(data.questions || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };
 
  useEffect(() => {
    api.videoStatus(videoId).then((v) => setVideoFile(v.video_file)).catch(() => {});
    loadQuiz();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [videoId]);
 
  const jumpTo = (seconds) => {
    if (videoRef.current) {
      videoRef.current.currentTime = seconds;
      videoRef.current.play();
    }
  };
 
  const selectOption = (question, optionId) => {
    // Ek baar answer karne ke baad badal nahi sakte (real test jaisa)
    if (answers[question.id]) return;
    setAnswers((prev) => ({ ...prev, [question.id]: optionId }));
  };
 
  const answeredCount = Object.keys(answers).length;
  const allAnswered = questions.length > 0 && answeredCount === questions.length;
  const score = questions.filter((q) => answers[q.id] === q.correct_option_id).length;
 
  // ---------- Weak topics: jin topics mein galti hui, unhe list karo ----------
  const weakTopics = allAnswered
    ? questions.filter((q) => answers[q.id] !== q.correct_option_id)
    : [];
 
  return (
    <div className="quiz-page">
      <div className="quiz-header">
        <p className="module-label">SELF ASSESSMENT</p>
        <h1>Test yourself 📝</h1>
        <p>Video dekhte hue neeche diye gaye sawaal solve karein.</p>
      </div>
 
      {error && <div className="error">{error}</div>}
 
      <div className="quiz-layout">
        {/* ---------- Left: video ---------- */}
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
 
        {/* ---------- Right: quiz ---------- */}
        <div className="quiz-card">
          {loading && <p>Quiz taiyaar ho raha hai...</p>}
 
          {!loading && questions.length > 0 && (
            <>
              <div className="quiz-progress">
                {answeredCount} / {questions.length} answered
              </div>
 
              <div className="question-list">
                {questions.map((q, index) => {
                  const selected = answers[q.id];
                  const isAnswered = !!selected;
                  const isCorrect = selected === q.correct_option_id;
 
                  return (
                    <div key={q.id} className="question-block">
                      <p className="question-text">
                        <span className="question-number">Q{index + 1}.</span> {q.question}
                      </p>
 
                      <div className="options-list">
                        {q.options.map((opt) => {
                          let optionClass = "option-item";
                          if (isAnswered) {
                            if (opt.id === q.correct_option_id) optionClass += " correct";
                            else if (opt.id === selected) optionClass += " incorrect";
                          }
                          return (
                            <label key={opt.id} className={optionClass}>
                              <input
                                type="radio"
                                name={q.id}
                                checked={selected === opt.id}
                                disabled={isAnswered}
                                onChange={() => selectOption(q, opt.id)}
                              />
                              {opt.text}
                            </label>
                          );
                        })}
                      </div>
 
                      {isAnswered && (
                        <div className={`feedback ${isCorrect ? "correct" : "incorrect"}`}>
                          <strong>{isCorrect ? "✓ Sahi jawab!" : "✗ Galat jawab."}</strong>
                          <p>{q.explanation}</p>
                          <button className="jump-link" onClick={() => jumpTo(q.start_time)}>
                            ▶ Video mein dekhein ({formatTime(q.start_time)})
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
 
              {/* ---------- Final result ---------- */}
              {allAnswered && (
                <div className="result-card">
                  <h2>
                    Aapka score: {score} / {questions.length}
                  </h2>
 
                  {weakTopics.length > 0 ? (
                    <div className="weak-topics">
                      <h3>💡 Yeh topics dobara revise karein:</h3>
                      <ul>
                        {weakTopics.map((q) => (
                          <li key={q.id}>
                            <button className="jump-link" onClick={() => jumpTo(q.start_time)}>
                              ▶ {formatTime(q.start_time)}
                            </button>{" "}
                            {q.topic}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : (
                    <p>🎉 Sab sahi! Is video ka content aapko achhe se samajh aa gaya.</p>
                  )}
 
                  <button className="retry-button" onClick={loadQuiz}>
                    Naya Quiz Try Karein
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
 
export default SelfAssessment;
 







