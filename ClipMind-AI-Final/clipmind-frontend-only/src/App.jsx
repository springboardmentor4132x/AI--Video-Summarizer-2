/*import React from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './api.js'
import Dashboard from './pages/Dashboard.jsx'
import History from './pages/History.jsx'
import KeyMoments from './pages/KeyMoments.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Summary from './pages/Summary.jsx'
import Transcript from './pages/Transcript.jsx'
import Upload from './pages/Upload.jsx'
function ProtectedRoute({ children }) {
  if (!api.isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return children
}

function Navbar() {
  const navigate = useNavigate()
  if (!api.isLoggedIn()) return null

  const handleLogout = () => {
    api.logout()
    navigate('/login')
  }

  return (
    <div className="navbar">
      <strong>ClipMind AI</strong>
      <div>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/history">History</Link>
        <Link to="/transcript">Transcript</Link>
        <Link to="/summary">Summary</Link>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to={api.isLoggedIn() ? "/dashboard" : "/login"} replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/transcript" element={<ProtectedRoute><Transcript /></ProtectedRoute>} />
        <Route path="/summary" element={<ProtectedRoute><Summary /></ProtectedRoute>} />
        <Route path="/keymoments/:videoId" element={<ProtectedRoute><KeyMoments /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}*/








/*import React from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './api.js'
import Dashboard from './pages/Dashboard.jsx'
import History from './pages/History.jsx'
import KeyMoments from './pages/KeyMoments.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Summary from './pages/Summary.jsx'
import Transcript from './pages/Transcript.jsx'
import Upload from './pages/Upload.jsx'
function ProtectedRoute({ children }) {
  if (!api.isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return children
}

function Navbar() {
  const navigate = useNavigate()
  if (!api.isLoggedIn()) return null

  const handleLogout = () => {
    api.logout()
    navigate('/login')
  }

  return (
    <div className="navbar">
      <strong>ClipMind AI</strong>
      <div>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/history">History</Link>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to={api.isLoggedIn() ? "/dashboard" : "/login"} replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/transcript/:videoId" element={<ProtectedRoute><Transcript /></ProtectedRoute>} />
        <Route path="/summary/:videoId" element={<ProtectedRoute><Summary /></ProtectedRoute>} />
        <Route path="/keymoments/:videoId" element={<ProtectedRoute><KeyMoments /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}*/













/*import React from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './api.js'
import Assistant from './pages/Assistant.jsx'
import Dashboard from './pages/Dashboard.jsx'
import History from './pages/History.jsx'
import KeyMoments from './pages/KeyMoments.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Summary from './pages/Summary.jsx'
import Transcript from './pages/Transcript.jsx'
import Upload from './pages/Upload.jsx'
function ProtectedRoute({ children }) {
  if (!api.isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return children
}
 
function Navbar() {
  const navigate = useNavigate()
  if (!api.isLoggedIn()) return null
 
  const handleLogout = () => {
    api.logout()
    navigate('/login')
  }
 
  return (
    <div className="navbar">
      <strong>ClipMind AI</strong>
      <div>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/history">History</Link>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  )
}
 
export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to={api.isLoggedIn() ? "/dashboard" : "/login"} replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/transcript/:videoId" element={<ProtectedRoute><Transcript /></ProtectedRoute>} />
        <Route path="/summary/:videoId" element={<ProtectedRoute><Summary /></ProtectedRoute>} />
        <Route path="/keymoments/:videoId" element={<ProtectedRoute><KeyMoments /></ProtectedRoute>} />
        <Route path="/assistant/:videoId" element={<ProtectedRoute><Assistant /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}*/













/*import React from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './api.js'
import Analytics from './pages/Analytics.jsx'
import Assistant from './pages/Assistant.jsx'
import Dashboard from './pages/Dashboard.jsx'
import History from './pages/History.jsx'
import KeyMoments from './pages/KeyMoments.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Summary from './pages/Summary.jsx'
import Transcript from './pages/Transcript.jsx'
import Upload from './pages/Upload.jsx'
function ProtectedRoute({ children }) {
  if (!api.isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return children
}
 
function Navbar() {
  const navigate = useNavigate()
  if (!api.isLoggedIn()) return null
 
  const handleLogout = () => {
    api.logout()
    navigate('/login')
  }
 
  return (
    <div className="navbar">
      <strong>ClipMind AI</strong>
      <div>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/history">History</Link>
        <Link to="/analytics">Analytics</Link>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  )
}
 
export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to={api.isLoggedIn() ? "/dashboard" : "/login"} replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/transcript/:videoId" element={<ProtectedRoute><Transcript /></ProtectedRoute>} />
        <Route path="/summary/:videoId" element={<ProtectedRoute><Summary /></ProtectedRoute>} />
        <Route path="/keymoments/:videoId" element={<ProtectedRoute><KeyMoments /></ProtectedRoute>} />
        <Route path="/assistant/:videoId" element={<ProtectedRoute><Assistant /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}*/







import React from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './api.js'
import Analytics from './pages/Analytics.jsx'
import Assistant from './pages/Assistant.jsx'
import Dashboard from './pages/Dashboard.jsx'
import History from './pages/History.jsx'
import KeyMoments from './pages/KeyMoments.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import SelfAssessment from './pages/SelfAssessment.jsx'
import SelfAssessmentList from './pages/SelfAssessmentList.jsx'
import Summary from './pages/Summary.jsx'
import Transcript from './pages/Transcript.jsx'
import Upload from './pages/Upload.jsx'
function ProtectedRoute({ children }) {
  if (!api.isLoggedIn()) {
    return <Navigate to="/login" replace />
  }
  return children
}
 
function Navbar() {
  const navigate = useNavigate()
  if (!api.isLoggedIn()) return null
 
  const handleLogout = () => {
    api.logout()
    navigate('/login')
  }
 
  return (
    <div className="navbar">
      <strong>ClipMind AI</strong>
      <div>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/history">History</Link>
        <Link to="/self-assessment">Self Assessment</Link>
        <Link to="/analytics">Analytics</Link>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  )
}
 
export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to={api.isLoggedIn() ? "/dashboard" : "/login"} replace />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/transcript/:videoId" element={<ProtectedRoute><Transcript /></ProtectedRoute>} />
        <Route path="/summary/:videoId" element={<ProtectedRoute><Summary /></ProtectedRoute>} />
        <Route path="/keymoments/:videoId" element={<ProtectedRoute><KeyMoments /></ProtectedRoute>} />
        <Route path="/assistant/:videoId" element={<ProtectedRoute><Assistant /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
        <Route path="/quiz/:videoId" element={<ProtectedRoute><SelfAssessment /></ProtectedRoute>} />
        <Route path="/self-assessment" element={<ProtectedRoute><SelfAssessmentList /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
 







