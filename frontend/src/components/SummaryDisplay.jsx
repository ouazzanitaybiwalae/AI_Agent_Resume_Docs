import { useMemo } from 'react';

function SummaryDisplay({ summary, fileName, docType, instructions, onReset, onCopy }) {
  
  // Utiliser useMemo au lieu de useState + useEffect
  const financialData = useMemo(() => {
    try {
      const parsed = JSON.parse(summary);
      if (parsed.type === 'financial') {
        return parsed;
      }
    } catch {
      // Ce n'est pas du JSON, c'est du texte normal
    }
    return null;
  }, [summary]);

  const isFinancial = financialData !== null;

  const getDocTypeLabel = (type) => {
    const labels = {
      rapport_financier: "Rapport financier",
      article_scientifique: "Article scientifique",
      compte_rendu_reunion: "Compte-rendu",
      contrat_juridique: "Contrat juridique",
      transcription_audio: "Transcription",
      documentation_technique: "Documentation",
      general: "Général",
    };
    return labels[type] || "Auto-détection";
  };

  // Affichage pour tableau financier (style carte)
  if (isFinancial && financialData) {
    return (
      <div className="result-container financial">
        <div className="result-header">
          <div className="result-meta">
            <span className="result-badge">📊 Résumé extractif</span>
            <span className="result-badge secondary">Rapport financier</span>
            {instructions && <span className="result-badge accent">Instructions</span>}
          </div>
          <div className="result-actions">
            <button className="icon-btn" onClick={onCopy} title="Copier">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
            </button>
            <button className="icon-btn" onClick={onReset} title="Nouveau document">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9h-4m-7 9A9 9 0 0 1 3 12m9 9v-4" />
              </svg>
            </button>
          </div>
        </div>

        <div className="result-file-info">
          <span>📄</span>
          <span>{fileName}</span>
        </div>

        <h2 className="financial-title">{financialData.title}</h2>

        <div className="financial-grid">
          {Object.entries(financialData.data).map(([key, value]) => (
            <div className="financial-card" key={key}>
              <div className="financial-card-label">{key}</div>
              <div className="financial-card-value">{value}</div>
            </div>
          ))}
        </div>

        <div className="financial-source">{financialData.source}</div>

        <button className="new-doc-btn" onClick={onReset}>
          📄 Nouveau document
        </button>
      </div>
    );
  }

  // Affichage standard pour les autres types
  return (
    <div className="result-container">
      <div className="result-header">
        <div className="result-meta">
          <span className="result-badge">✅ Résumé extractif</span>
          {docType && docType !== "auto" && (
            <span className="result-badge secondary">{getDocTypeLabel(docType)}</span>
          )}
          {instructions && <span className="result-badge accent">✨ Instructions</span>}
        </div>
        <div className="result-actions">
          <button className="icon-btn" onClick={onCopy} title="Copier">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
          <button className="icon-btn" onClick={onReset} title="Nouveau document">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9h-4m-7 9A9 9 0 0 1 3 12m9 9v-4" />
            </svg>
          </button>
        </div>
      </div>

      <div className="result-file-info">
        <span>📄</span>
        <span>{fileName}</span>
      </div>

      <div className="result-content">
        <div className="result-text" dangerouslySetInnerHTML={{ __html: summary }} />
      </div>

      <button className="new-doc-btn" onClick={onReset}>
        📄 Nouveau document
      </button>
    </div>
  );
}

export default SummaryDisplay;