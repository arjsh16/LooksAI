import Spinner from '../ui/Spinner'

const STAGE_LABELS = {
  pending:    { icon: '⏳', text: 'Queued for analysis…' },
  processing: { icon: null, text: 'Running AI pipeline…' },
  completed:  { icon: '✅', text: 'Analysis complete!' },
  failed:     { icon: '❌', text: 'Analysis failed.' },
}

const STEPS = [
  'Extracting 468 face landmarks (MediaPipe)',
  'Classifying face shape',
  'Analysing skin — EfficientNet + heuristics',
  'Detecting facial features',
]

export default function AnalysisStatus({ session, error }) {
  if (!session && !error) return null

  const status = session?.status ?? 'failed'
  const { icon, text } = STAGE_LABELS[status] ?? STAGE_LABELS.failed

  return (
    <div className={`analysis-status status-${status}`}>
      <div className="status-header">
        {status === 'processing' && <Spinner size={22} />}
        {icon && <span className="status-icon">{icon}</span>}
        <span className="status-text">{error || text}</span>
      </div>

      {status === 'processing' && (
        <ul className="pipeline-steps">
          {STEPS.map(s => (
            <li key={s} className="step">
              <span className="step-dot" />
              {s}
            </li>
          ))}
        </ul>
      )}

      {status === 'completed' && session && (
        <div className="analysis-summary">
          <div className="summary-chip">Face shape: <strong>{session.face_shape}</strong></div>
          {session.skin_analysis && (
            <>
              <div className="summary-chip">Skin: <strong>{session.skin_analysis.skin_type}</strong></div>
              <div className="summary-chip">Acne: <strong>{session.skin_analysis.acne_severity}</strong></div>
              <div className="summary-chip">Dark circles: <strong>{session.skin_analysis.dark_circles}</strong></div>
            </>
          )}
          {session.facial_features && (
            <>
              <div className="summary-chip">Jawline: <strong>{session.facial_features.jawline}</strong></div>
              <div className="summary-chip">Forehead: <strong>{session.facial_features.forehead}</strong></div>
              <div className="summary-chip">Cheekbones: <strong>{session.facial_features.cheekbones}</strong></div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
