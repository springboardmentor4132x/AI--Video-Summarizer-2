import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api.js'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '', email: '', password: '', confirm_password: '', role: 'learner',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    try {
      await api.register(form)
      setSuccess('Registration successful! Redirecting to login...')
      setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="container">
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <label>Full Name</label>
        <input name="name" value={form.name} onChange={handleChange} required />

        <label>Email</label>
        <input type="email" name="email" value={form.email} onChange={handleChange} required />

        <label>Password</label>
        <input type="password" name="password" value={form.password} onChange={handleChange} required />

        <label>Confirm Password</label>
        <input type="password" name="confirm_password" value={form.confirm_password} onChange={handleChange} required />

        <label>Role</label>
        <select name="role" value={form.role} onChange={handleChange}>
          <option value="content_creator">Content Creator</option>
          <option value="learner">Learner</option>
          <option value="educator">Educator</option>
          <option value="administrator">Administrator</option>
        </select>

        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}

        <button type="submit">Register</button>
      </form>
      <div className="link-text">
        Already have an account? <Link to="/login">Login</Link>
      </div>
    </div>
  )
}
