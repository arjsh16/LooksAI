import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'
const WS_BASE  = import.meta.env.VITE_WS_URL  ?? 'ws://localhost:8000/api'

export const api = axios.create({ baseURL: BASE_URL })

// Attach JWT on every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/LooksAI/login'
    }
    return Promise.reject(err)
  }
)

// ── Analysis ──────────────────────────────────────────────────────────────────

export async function uploadPhotos(front, left, right) {
  const form = new FormData()
  form.append('front', front)
  form.append('left', left)
  form.append('right', right)
  const res = await api.post('/analysis/upload', form)
  return res.data   // AnalysisSessionResponse
}

export async function getSession(sessionId) {
  const res = await api.get(`/analysis/${sessionId}`)
  return res.data
}

export async function listSessions() {
  const res = await api.get('/analysis/')
  return res.data
}

// ── WebSocket factory ─────────────────────────────────────────────────────────

export function buildWsUrl(sessionId) {
  const token = localStorage.getItem('token')
  return `${WS_BASE}/chat/stream/${sessionId}?token=${token}`
}
