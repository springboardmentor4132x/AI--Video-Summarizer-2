/*import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'

export default function History() {
  const [videos, setVideos] = useState([])
  const [error, setError] = useState('')

  const loadHistory = () => {
    api.history().then(setVideos).catch((err) => setError(err.message))
  }

  useEffect(() => {
    loadHistory()
    // Har 5 second mein refresh karo taaki "processing" status update dikhe
    const interval = setInterval(loadHistory, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="wide-container">
      <h1>Upload History</h1>
      {error && <div className="error">{error}</div>}
      {videos.length === 0 ? (
        <p>No videos uploaded yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Status</th>
              <th>Duration</th>
              <th>Uploaded At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {videos.map((v) => (
              <tr key={v.id}>
                <td>{v.filename}</td>
                <td>
                  <span className={`status-badge status-${v.status}`}>{v.status}</span>
                </td>
                <td>{v.duration_seconds ? `${v.duration_seconds}s` : '-'}</td>
                <td>{new Date(v.uploaded_at).toLocaleString()}</td>
                <td>
                  <Link to={`/transcript/${v.id}`}>Transcript</Link>
                  {' | '}
                  <Link to={`/summary/${v.id}`}>Summary</Link>
                  {' | '}
                  <Link to={`/keymoments/${v.id}`}>Key Moments</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}*/


















import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
 
export default function History() {
  const [videos, setVideos] = useState([])
  const [error, setError] = useState('')
 
  const loadHistory = () => {
    api.history().then(setVideos).catch((err) => setError(err.message))
  }
 
  useEffect(() => {
    loadHistory()
    // Har 5 second mein refresh karo taaki "processing" status update dikhe
    const interval = setInterval(loadHistory, 5000)
    return () => clearInterval(interval)
  }, [])
 
  return (
    <div className="wide-container">
      <h1>Upload History</h1>
      {error && <div className="error">{error}</div>}
      {videos.length === 0 ? (
        <p>No videos uploaded yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Status</th>
              <th>Duration</th>
              <th>Uploaded At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {videos.map((v) => (
              <tr key={v.id}>
                <td>{v.filename}</td>
                <td>
                  <span className={`status-badge status-${v.status}`}>{v.status}</span>
                </td>
                <td>{v.duration_seconds ? `${v.duration_seconds}s` : '-'}</td>
                <td>{new Date(v.uploaded_at).toLocaleString()}</td>
                <td>
                  <Link to={`/transcript/${v.id}`}>Transcript</Link>
                  {' | '}
                  <Link to={`/summary/${v.id}`}>Summary</Link>
                  {' | '}
                  <Link to={`/keymoments/${v.id}`}>Key Moments</Link>
                  {' | '}
                  <Link to={`/assistant/${v.id}`}>Ask AI 🤖</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
