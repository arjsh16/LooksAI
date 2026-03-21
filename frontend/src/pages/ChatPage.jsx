import { useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useWebSocket, WS_STATES } from '../hooks/useWebSocket'
import ChatWindow from '../components/chat/ChatWindow'
import Spinner from '../components/ui/Spinner'

export default function ChatPage() {
  const { sessionId }    = useParams()
  const { user, logout } = useAuth()
  const navigate          = useNavigate()
  const { messages, wsState, streaming, connect, sendMessage, disconnect } =
    useWebSocket(Number(sessionId))

  // Connect to WebSocket as soon as the page mounts
  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  const handleChoice = (option) => sendMessage(option)

  const wsLabel = {
    [WS_STATES.CONNECTING]: 'Connecting…',
    [WS_STATES.OPEN]:       'Live',
    [WS_STATES.CLOSING]:    'Closing…',
    [WS_STATES.CLOSED]:     'Disconnected',
  }[wsState] ?? ''

  return (
    <div className="page chat-page">
      <header className="page-header">
        <div className="header-brand">
          <span className="brand-icon">✂️</span>
          <span className="brand-name">LooksAI</span>
        </div>
        <div className="header-center">
          <span className={`ws-badge ws-${wsState === WS_STATES.OPEN ? 'open' : 'closed'}`}>
            {wsState === WS_STATES.OPEN && <span className="ws-dot" />}
            {wsLabel}
          </span>
        </div>
        <div className="header-right">
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/analysis')}>
            ← New analysis
          </button>
          <button className="btn btn-ghost btn-sm" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      <main className="chat-main">
        {wsState === WS_STATES.CLOSED && messages.length === 0 && (
          <div className="full-center">
            <Spinner size={40} />
            <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>
              Waiting for connection…
            </p>
          </div>
        )}

        <ChatWindow
          messages={messages}
          wsState={wsState}
          streaming={streaming}
          onChoice={handleChoice}
        />
      </main>
    </div>
  )
}
