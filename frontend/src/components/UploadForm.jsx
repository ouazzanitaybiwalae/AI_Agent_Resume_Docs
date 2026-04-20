import { useRef, useState } from 'react'

const DOC_TYPES = [
  { value: "auto", label: "Auto-détection" },
  { value: "rapport_financier", label: "Rapport financier" },
  { value: "article_scientifique", label: "Article scientifique" },
  { value: "compte_rendu_reunion", label: "Compte-rendu" },
  { value: "contrat_juridique", label: "Contrat juridique" },
  { value: "transcription_audio", label: "Transcription" },
  { value: "documentation_technique", label: "Documentation" },
  { value: "general", label: "Général" },
];

const EXAMPLE_PROMPTS = [
  "Résumé en 5 puces maximum",
  "Pour un public non-expert",
  "Extrais uniquement les dates et responsabilités",
  "Quels sont les risques mentionnés ?",
  "Compare les positions des auteurs",
  "Résumé hiérarchique en 3 parties",
];

function UploadForm({ file, setFile, instructions, setInstructions, docType, setDocType }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f && (f.type === "text/plain" || f.type === "application/pdf" || f.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document")) {
      setFile(f)
    }
  }

  const handleChange = (e) => {
    if (e.target.files[0]) setFile(e.target.files[0])
  }

  const handleExampleClick = (example) => {
    setInstructions(example)
  }

  return (
    <div className="upload-container">
      {/* Zone de dépôt */}
      <div
        className={`dropzone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          style={{ display: 'none' }}
          onChange={handleChange}
        />
        
        {!file ? (
          <>
            <div className="dropzone-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <p className="dropzone-title">Déposez votre fichier ici</p>
            <p className="dropzone-subtitle">PDF, DOCX ou TXT — Jusqu'à 50 Mo</p>
          </>
        ) : (
          <div className="file-preview">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <div className="file-info">
              <span className="file-name">{file.name}</span>
              <span className="file-size">{(file.size / 1024).toFixed(0)} Ko</span>
            </div>
            <button 
              className="file-remove"
              onClick={(e) => { e.stopPropagation(); setFile(null) }}
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Type de document */}
      <div className="section">
        <label className="section-label">Type de document</label>
        <div className="doc-type-selector">
          {DOC_TYPES.map((type) => (
            <button
              key={type.value}
              className={`doc-type-option ${docType === type.value ? 'active' : ''}`}
              onClick={() => setDocType(type.value)}
            >
              {type.label}
            </button>
          ))}
        </div>
      </div>

      {/* Instructions */}
      <div className="section">
        <label className="section-label">Instructions (optionnel)</label>
        <textarea
          className="instructions-input"
          rows="3"
          placeholder="Exemple : Résume ce document en 5 puces maximum..."
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
        />
        <div className="prompts-grid">
          {EXAMPLE_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              className="prompt-tag"
              onClick={() => handleExampleClick(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default UploadForm