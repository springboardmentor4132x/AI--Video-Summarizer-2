import React, { useState } from 'react'
import { api } from '../api.js'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    if (!file) {
      setError('Please select a video file first.')
      return
    }
    setUploading(true)
    try {
      const result = await api.uploadVideo(file)
      setMessage(`${result.message} (Status: ${result.video.status})`)
      setFile(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="container">
      <h1>Upload Video</h1>
      <form onSubmit={handleSubmit}>
        <label>Select Video File</label>
        <input
          type="file"
          accept=".mp4,.mov,.avi,.mkv,.webm"
          onChange={(e) => setFile(e.target.files[0])}
        />
        {error && <div className="error">{error}</div>}
        {message && <div className="success">{message}</div>}
        <button type="submit" disabled={uploading}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
    </div>
  )
}
