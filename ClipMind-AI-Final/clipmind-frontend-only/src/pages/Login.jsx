import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api.js'

export default function Login() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const data = await api.login(form)
      api.saveToken(data.access_token)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <label>Email</label>
        <input type="email" name="email" value={form.email} onChange={handleChange} required />

        <label>Password</label>
        <input type="password" name="password" value={form.password} onChange={handleChange} required />

        {error && <div className="error">{error}</div>}

        <button type="submit">Login</button>
      </form>
      <div className="link-text">
        Don't have an account? <Link to="/register">Register</Link>
      </div>
    </div>
  )
}
