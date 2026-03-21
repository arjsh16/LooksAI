import { useState, useRef, useCallback, useEffect } from 'react'
import { buildWsUrl } from '../services/api'

export const WS_STATES = { CONNECTING: 0, OPEN: 1, CLOSING: 2, CLOSED: 3 }

export function useWebSocket(sessionId) {
  const [messages, setMessages]   = useState([])
  const [wsState, setWsState]     = useState(WS_STATES.CLOSED)
  const [streaming, setStreaming]  = useState(false)
  const wsRef    = useRef(null)
  const bufRef   = useRef('')   // accumulates streaming tokens

  const addMessage = (msg) => setMessages(prev => [...prev, msg])

  const flushStream = useCallback(() => {
    if (!bufRef.current) return
    setMessages(prev => {
      const last = prev[prev.length - 1]
      if (last?.type === 'stream') {
        return [...prev.slice(0, -1), { ...last, content: bufRef.current }]
      }
      return [...prev, { type: 'stream', role: 'assistant', content: bufRef.current }]
    })
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WS_STATES.OPEN) return
    const ws = new WebSocket(buildWsUrl(sessionId))
    wsRef.current = ws
    setWsState(WS_STATES.CONNECTING)

    ws.onopen  = () => setWsState(WS_STATES.OPEN)
    ws.onclose = () => { setWsState(WS_STATES.CLOSED); setStreaming(false) }
    ws.onerror = () => { setWsState(WS_STATES.CLOSED); setStreaming(false) }

    ws.onmessage = (ev) => {
      let data
      try { data = JSON.parse(ev.data) } catch { return }

      switch (data.type) {
        case 'message':
          addMessage({ type: 'message', role: data.role, content: data.content,
                       stage: data.stage, options: data.options })
          break
        case 'stream_start':
          bufRef.current = ''
          setStreaming(true)
          break
        case 'stream_chunk':
          bufRef.current += data.content
          flushStream()
          break
        case 'stream_end':
          setStreaming(false)
          break
        case 'error':
          addMessage({ type: 'error', content: data.message })
          setStreaming(false)
          break
        default:
          break
      }
    }
  }, [sessionId, flushStream])

  const sendMessage = useCallback((text) => {
    if (wsRef.current?.readyState !== WS_STATES.OPEN) return
    addMessage({ type: 'message', role: 'user', content: text })
    wsRef.current.send(JSON.stringify({ message: text }))
  }, [])

  const disconnect = useCallback(() => {
    wsRef.current?.close()
  }, [])

  // Auto-disconnect on unmount
  useEffect(() => () => wsRef.current?.close(), [])

  return { messages, wsState, streaming, connect, sendMessage, disconnect }
}
