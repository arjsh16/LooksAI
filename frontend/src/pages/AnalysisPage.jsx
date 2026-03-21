import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useAnalysis } from '../hooks/useAnalysis'
import PhotoUploader from '../components/analysis/PhotoUploader'
import AnalysisStatus from '../components/analysis/AnalysisStatus'

export default function AnalysisPage() {
  const { user, logout } = useAuth()
  const navigate          = useNavigate()
  const { session, uploading, polling, error, upload, reset } = useAnalysis()

  // Navigate to chat as soon as analysis finishes
  useEffect(() => {
    if (session?.status === 'completed') {
      const timer = setTimeout(() => navigate(`/chat/${session.id}`), 1200)
      return () => clearTimeout(timer)
    }
  }, [session, navigate])

  const isActive = uploading || polling

  return (
    <div className="page analysis-page">
      <header className="page-header">
        <div className="header-brand">
          <span className="brand-icon">✂️</span>
          <span className="brand-name">LooksAI</span>
        </div>
        <div className="header-right">
          <span className="header-user">{user?.username}</span>
          <button className="btn btn-ghost btn-sm" onClick={logout}>Sign out</button>
        </div>
      </header>

      <main className="page-main">
        <div className="section-header">
          <h2>Upload your photos</h2>
          <p className="section-sub">
            Three angles unlock the full AI analysis — face shape, skin condition,
            and targeted haircut recommendations.
          </p>
        </div>

        {!isActive && !session && (
          <PhotoUploader onUpload={upload} uploading={uploading} />
        )}

        <AnalysisStatus session={session} error={error} />

        {(error || session?.status === 'failed') && (
          <button className="btn btn-secondary" style={{ marginTop: '1rem' }} onClick={reset}>
            Try again
          </button>
        )}
      </main>
    </div>
  )
}
