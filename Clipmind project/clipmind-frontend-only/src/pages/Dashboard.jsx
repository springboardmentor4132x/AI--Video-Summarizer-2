import React, { useEffect, useState } from 'react'
import { api } from '../api.js'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.dashboard().then(setData).catch((err) => setError(err.message))
  }, [])

  if (error) return <div className="wide-container error">{error}</div>
  if (!data) return <div className="wide-container">Loading...</div>

  return (
    <div className="wide-container">
      <h1>Welcome, {data.name}</h1>
      <p><strong>Role:</strong> {data.role}</p>
      <p><strong>Total Uploads:</strong> {data.total_uploads}</p>
      {data.message && <p>{data.message}</p>}
      {data.admin_stats && (
        <div>
          <h2>Admin Stats</h2>
          <p>Total Users: {data.admin_stats.total_users}</p>
          <p>Total Videos: {data.admin_stats.total_videos}</p>
        </div>
      )}
    </div>
  )
}
