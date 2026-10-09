import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import './SelfAssessmentList.css'
 
export default function SelfAssessmentList() {
  const [videos, setVideos] = useState([])
  const [error, setError] = useState('')
 
  useEffect(() => {
    api.history().then(setVideos).catch((err) => setError(err.message))
  }, [])
 
  return (
    <div className="sa-list-page">
      <div className="sa-list-header">
        <p className="module-label">SELF ASSESSMENT</p>
        <h1>Test yourself 📝</h1>
        <p>Kisi bhi video ko choose karein aur uska quiz shuru karein.</p>
      </div>
 
      {error && <div className="error">{error}</div>}
 
      {videos.length === 0 ? (
        <p className="empty-note">Abhi koi video upload nahi hua. Pehle Upload page se video daalein.</p>
      ) : (
        <div className="sa-video-grid">
          {videos.map((v) => (
            <div key={v.id} className="sa-video-card">
              <div className="sa-video-name">{v.filename}</div>
              <div className={`sa-status-pill status-${v.status}`}>{v.status}</div>
              <Link to={`/quiz/${v.id}`} className="sa-start-button">
                Start Test →
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
 







