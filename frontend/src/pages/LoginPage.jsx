import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'

export default function LoginPage() {
  const [tab, setTab] = useState('login')
  const { user } = useAuth()
  const navigate  = useNavigate()

  if (user) { navigate('/analysis', { replace: true }); return null }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="brand-icon">✂️</span>
          <h1 className="brand-name">LooksAI</h1>
          <p className="brand-tagline">Your face. Your perfect cut.</p>
        </div>

        <div className="tab-bar">
          <button
            className={`tab ${tab === 'login' ? 'active' : ''}`}
            onClick={() => setTab('login')}
          >Sign in</button>
          <button
            className={`tab ${tab === 'register' ? 'active' : ''}`}
            onClick={() => setTab('register')}
          >Create account</button>
        </div>

        {tab === 'login'
          ? <LoginForm    onSuccess={() => navigate('/analysis')} />
          : <RegisterForm onSuccess={() => navigate('/analysis')} />
        }
      </div>
    </div>
  )
}
