import { useRef } from 'react'

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' o'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' Ko'
  return (bytes / (1024 * 1024)).toFixed(1) + ' Mo'
}

function UploadForm({ file, setFile }) {
  const inputRef = useRef(null)

  const handleDrop = (e) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) setFile(f)
  }

  const handleChange = (e) => {
    if (e.target.files[0]) setFile(e.target.files[0])
  }

  return (
    <div className="card">
      <p className="card-label">01 — Document</p>

      <div
        className="drop-zone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          style={{ display: 'none' }}
          onChange={handleChange}
        />
        <div className="drop-icon">
          <svg viewBox="0 0 24 24" fill="none" strokeWidth="1.5"
            strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
        <p className="drop-text">
          <strong>Glissez un fichier</strong> ou cliquez pour parcourir
        </p>
        <p className="drop-formats">PDF · DOCX · TXT · MD</p>
      </div>

      {file && (
        <div className="file-selected">
          <svg viewBox="0 0 24 24" fill="none" strokeWidth="1.5"
            strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          <span className="file-name">{file.name}</span>
          <span className="file-size">{formatSize(file.size)}</span>
          <button className="file-remove" onClick={(e) => { e.stopPropagation(); setFile(null) }}>✕</button>
        </div>
      )}
    </div>
  )
}

export default UploadForm
