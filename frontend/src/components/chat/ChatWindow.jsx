import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import ChoiceButtons from './ChoiceButtons'
import Spinner from '../ui/Spinner'
import { WS_STATES } from '../../hooks/useWebSocket'

export default function ChatWindow({ messages, wsState, streaming, onChoice }) {
  const endRef = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const lastMsg      = messages[messages.length - 1]
  const pendingOpts  = !streaming && lastMsg?.options?.length ? lastMsg.options : []
  const isConnecting = wsState === WS_STATES.CONNECTING

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {isConnecting && (
          <div className="full-center" style={{ padding: '2rem' }}>
            <Spinner size={32} />
            <span style={{ marginLeft: '0.75rem', color: 'var(--text-muted)' }}>
              Connecting…
            </span>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            message={msg}
            streaming={streaming && i === messages.length - 1}
          />
        ))}

        {streaming && messages[messages.length - 1]?.type !== 'stream' && (
          <div className="bubble-row assistant">
            <div className="bubble-avatar"><span>✂️</span></div>
            <div className="bubble typing">
              <Spinner size={14} />
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {pendingOpts.length > 0 && (
        <ChoiceButtons
          options={pendingOpts}
          onChoice={onChoice}
          disabled={streaming}
        />
      )}
    </div>
  )
}
