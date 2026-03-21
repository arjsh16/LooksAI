import { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import Spinner from '../ui/Spinner'

export default function RegisterForm({ onSuccess }) {
  const { register } = useAuth()
  const [email, setEmail]       = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (password.length < 8) { setError('Password must be at least 8 characters.'); return }
    setLoading(true)
    try {
      await register(email, username, password)
      onSuccess?.()
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Try a different email or username.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="reg-email">Email</label>
        <input
          id="reg-email" type="email" required autoComplete="email"
          value={email} onChange={e => setEmail(e.target.value)}
          placeholder="you@example.com"
        />
      </div>
      <div className="form-group">
        <label htmlFor="reg-username">Username</label>
        <input
          id="reg-username" type="text" required autoComplete="username"
          value={username} onChange={e => setUsername(e.target.value)}
          placeholder="coolhandle"
        />
      </div>
      <div className="form-group">
        <label htmlFor="reg-password">Password</label>
        <input
          id="reg-password" type="password" required autoComplete="new-password"
          value={password} onChange={e => setPassword(e.target.value)}
          placeholder="Min 8 characters"
        />
      </div>
      {error && <p className="form-error">{error}</p>}
      <button className="btn btn-primary" type="submit" disabled={loading}>
        {loading ? <Spinner size={18} color="#fff" /> : 'Create account'}
      </button>
    </form>
  )
}
