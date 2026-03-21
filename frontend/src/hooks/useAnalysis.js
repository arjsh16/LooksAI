import { useState, useCallback, useRef } from 'react'
import { uploadPhotos, getSession } from '../services/api'

const POLL_INTERVAL = 2000   // ms
const POLL_TIMEOUT  = 120000 // 2 min

export function useAnalysis() {
  const [session, setSession]   = useState(null)
  const [uploading, setUploading] = useState(false)
  const [polling, setPolling]   = useState(false)
  const [error, setError]       = useState(null)
  const timerRef = useRef(null)
  const startRef = useRef(null)

  const stopPolling = () => {
    clearInterval(timerRef.current)
    setPolling(false)
  }

  const startPolling = useCallback((sessionId) => {
    setPolling(true)
    startRef.current = Date.now()
    timerRef.current = setInterval(async () => {
      try {
        if (Date.now() - startRef.current > POLL_TIMEOUT) {
          stopPolling()
          setError('Analysis timed out. Please try again.')
          return
        }
        const data = await getSession(sessionId)
        setSession(data)
        if (data.status === 'completed' || data.status === 'failed') {
          stopPolling()
          if (data.status === 'failed') {
            setError(data.error_message || 'Analysis failed.')
          }
        }
      } catch (err) {
        stopPolling()
        setError(err.response?.data?.detail || 'Failed to fetch session status.')
      }
    }, POLL_INTERVAL)
  }, [])

  const upload = useCallback(async (front, left, right) => {
    setError(null)
    setSession(null)
    setUploading(true)
    try {
      const data = await uploadPhotos(front, left, right)
      setSession(data)
      startPolling(data.id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }, [startPolling])

  const reset = useCallback(() => {
    stopPolling()
    setSession(null)
    setError(null)
    setUploading(false)
  }, [])

  return { session, uploading, polling, error, upload, reset }
}
