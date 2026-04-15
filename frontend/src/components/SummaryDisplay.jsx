import { useState } from 'react'

function SummaryDisplay({ result, onReset }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(result.final_summary).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const s = result.stats || {}

  return (
    <div className="card result-card">

      <div className="result-header">
        <div className="result-badges">
          <span className="badge badge-green">{result.style}</span>
          <span className="badge badge-blue">{result.target_length}</span>
          <span className="badge badge-gray">{result.nb_chunks} chunks</span>
        </div>
        <button className="btn-copy" onClick={handleCopy}>
          {copied ? '✓ Copié !' : 'Copier'}
        </button>
      </div>

      <p className="result-text">{result.final_summary}</p>

      <div className="result-stats">
        <div className="stat">
          <span className="stat-value">{(s.input_tokens || 0).toLocaleString()}</span>
          <span className="stat-label">tokens en entrée</span>
        </div>
        <div className="stat">
          <span className="stat-value">{(s.output_tokens || 0).toLocaleString()}</span>
          <span className="stat-label">tokens en sortie</span>
        </div>
        <div className="stat">
          <span className="stat-value">
            {s.compression_ratio != null
              ? (s.compression_ratio * 100).toFixed(1) + '%'
              : '—'}
          </span>
          <span className="stat-label">compression</span>
        </div>
      </div>

      <button className="btn-new" onClick={onReset}>
        ← Résumer un autre document
      </button>
    </div>
  )
}

export default SummaryDisplay

