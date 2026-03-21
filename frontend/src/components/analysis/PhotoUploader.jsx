import { useState, useRef } from 'react'
import Spinner from '../ui/Spinner'

const ANGLES = [
  { key: 'front', label: 'Front view',         hint: 'Face the camera directly' },
  { key: 'left',  label: 'Left profile',        hint: 'Turn your head left 90°' },
  { key: 'right', label: 'Right profile',       hint: 'Turn your head right 90°' },
]

function PhotoSlot({ angle, file, onFile }) {
  const inputRef = useRef(null)
  const preview = file ? URL.createObjectURL(file) : null

  return (
    <div
      className={`photo-slot ${file ? 'filled' : ''}`}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && inputRef.current?.click()}
      aria-label={`Upload ${angle.label}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        style={{ display: 'none' }}
        onChange={e => e.target.files[0] && onFile(e.target.files[0])}
      />
      {preview ? (
        <img src={preview} alt={angle.label} className="photo-preview" />
      ) : (
        <div className="photo-placeholder">
          <span className="photo-icon">📷</span>
          <span className="photo-label">{angle.label}</span>
          <span className="photo-hint">{angle.hint}</span>
        </div>
      )}
      {file && <div className="photo-check">✓</div>}
    </div>
  )
}

export default function PhotoUploader({ onUpload, uploading }) {
  const [files, setFiles] = useState({ front: null, left: null, right: null })

  const setFile = (key, file) => setFiles(prev => ({ ...prev, [key]: file }))
  const allReady = files.front && files.left && files.right

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!allReady || uploading) return
    onUpload(files.front, files.left, files.right)
  }

  return (
    <div className="uploader">
      <p className="uploader-instruction">
        Upload three clear photos — front, left profile, and right profile.
        Good lighting and a neutral background give the best results.
      </p>
      <div className="photo-grid">
        {ANGLES.map(a => (
          <PhotoSlot
            key={a.key}
            angle={a}
            file={files[a.key]}
            onFile={f => setFile(a.key, f)}
          />
        ))}
      </div>
      <button
        className="btn btn-primary btn-wide"
        disabled={!allReady || uploading}
        onClick={handleSubmit}
      >
        {uploading
          ? <><Spinner size={18} color="#fff" /> &nbsp;Uploading…</>
          : 'Analyse my face'}
      </button>
    </div>
  )
}
