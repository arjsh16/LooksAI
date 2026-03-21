import MarkdownRenderer from '../ui/MarkdownRenderer'
import Spinner from '../ui/Spinner'

export default function MessageBubble({ message, streaming }) {
  const isUser = message.role === 'user'
  const isError = message.type === 'error'

  return (
    <div className={`bubble-row ${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div className="bubble-avatar" aria-label="LooksAI">
          <span>✂️</span>
        </div>
      )}
      <div className={`bubble ${isError ? 'bubble-error' : ''}`}>
        {isUser
          ? <p>{message.content}</p>
          : <MarkdownRenderer content={message.content} />
        }
        {streaming && message.type === 'stream' && (
          <span className="cursor-blink">▍</span>
        )}
      </div>
    </div>
  )
}
