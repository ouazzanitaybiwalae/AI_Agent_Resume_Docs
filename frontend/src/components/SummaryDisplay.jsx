import { useMemo } from 'react';

// ─── helpers ──────────────────────────────────────────────────────────────────

function getDocTypeLabel(type) {
  const labels = {
    rapport_financier:       "Rapport financier",
    article_scientifique:    "Article scientifique",
    compte_rendu_reunion:    "Compte-rendu",
    contrat_juridique:       "Contrat juridique",
    transcription_audio:     "Transcription",
    documentation_technique: "Documentation",
    general:                 "Général",
  };
  return labels[type] || "Auto-détection";
}

// ─── Sous-composant : tableau de bord financier standard ─────────────────────

function FinancialDashboard({ data }) {
  const { executive_summary = [], risks = [], dashboard = {} } = data;

  // Couleurs par section
  const sectionStyles = {
    revenus:      { border: '#3B82F6', bg: '#EFF6FF', badge: '#3B82F6' },
    rentabilite:  { border: '#10B981', bg: '#ECFDF5', badge: '#10B981' },
    bilan:        { border: '#8B5CF6', bg: '#F5F3FF', badge: '#8B5CF6' },
    financement:  { border: '#F59E0B', bg: '#FFFBEB', badge: '#F59E0B' },
  };

  return (
    <div style={{ fontFamily: "'Segoe UI', system-ui, sans-serif" }}>

      {/* ── Résumé exécutif ── */}
      {executive_summary.length > 0 && (
        <div style={{
          background: 'linear-gradient(135deg, #1e3a5f 0%, #1e4976 100%)',
          borderRadius: '12px',
          padding: '20px 24px',
          marginBottom: '24px',
          color: '#fff',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
            <span style={{ fontSize: '20px' }}>📋</span>
            <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase' }}>
              Résumé Exécutif
            </h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {executive_summary.map((line, i) => (
              <p
                key={i}
                style={{ margin: 0, fontSize: '14px', lineHeight: '1.6', opacity: 0.92 }}
                dangerouslySetInnerHTML={{ __html: `<span style="color:#60A5FA;margin-right:8px">▸</span>${line}` }}
              />
            ))}
          </div>
          {risks.length > 0 && (
            <div style={{
              marginTop: '14px',
              padding: '10px 14px',
              background: 'rgba(239,68,68,0.15)',
              borderLeft: '3px solid #EF4444',
              borderRadius: '4px',
            }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#FCA5A5' }}>⚠ Points de vigilance :</span>
              {risks.map((r, i) => (
                <p key={i} style={{ margin: '4px 0 0', fontSize: '13px', color: '#FECACA' }}>{r}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Tableau de bord 4 sections ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
        {Object.entries(dashboard).map(([key, section]) => {
          const style = sectionStyles[key] || { border: '#6B7280', bg: '#F9FAFB', badge: '#6B7280' };
          const filledKpis = section.kpis.filter(k => k.value && k.value !== '—');

          return (
            <div key={key} style={{
              background: style.bg,
              border: `1px solid ${style.border}30`,
              borderTop: `3px solid ${style.border}`,
              borderRadius: '10px',
              padding: '16px',
              boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
            }}>
              {/* En-tête section */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <span style={{ fontSize: '18px' }}>{section.icon}</span>
                <span style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  color: style.badge,
                }}>
                  {section.label}
                </span>
                <span style={{
                  marginLeft: 'auto',
                  fontSize: '11px',
                  background: `${style.border}18`,
                  color: style.badge,
                  padding: '2px 8px',
                  borderRadius: '99px',
                  fontWeight: 600,
                }}>
                  {filledKpis.length}/{section.kpis.length} KPIs
                </span>
              </div>

              {/* KPIs */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {section.kpis.map((kpi, i) => (
                  <div key={i} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 10px',
                    background: '#fff',
                    borderRadius: '6px',
                    border: '1px solid #E5E7EB',
                  }}>
                    <span style={{ fontSize: '13px', color: '#4B5563', fontWeight: 500 }}>
                      {kpi.label}
                    </span>
                    <span style={{
                      fontSize: '13px',
                      fontWeight: 700,
                      color: kpi.value ? style.badge : '#9CA3AF',
                      letterSpacing: kpi.value ? '0.01em' : 'normal',
                    }}>
                      {kpi.value || '—'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────

function SummaryDisplay({ summary, fileName, docType, instructions, onReset, onCopy }) {

  const financialData = useMemo(() => {
    try {
      const parsed = JSON.parse(summary);
      if (parsed.type === 'financial') return parsed;
    } catch {
      // Pas du JSON — résumé texte standard
    }
    return null;
  }, [summary]);

  const isFinancial = financialData !== null;

  // ── Affichage rapport financier ──────────────────────────────────────────
  if (isFinancial) {
    return (
      <div className="result-container financial">
        <div className="result-header">
          <div className="result-meta">
            <span className="result-badge">Résumé extractif</span>
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

        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px', color: '#1e3a5f' }}>
          {financialData.title}
        </h2>

        <FinancialDashboard data={financialData} />

        <p style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '16px', textAlign: 'right' }}>
          Source : {financialData.source}
        </p>

        <button className="new-doc-btn" onClick={onReset}>
          📄 Nouveau document
        </button>
      </div>
    );
  }

  // ── Affichage standard ───────────────────────────────────────────────────
  return (
    <div className="result-container">
      <div className="result-header">
        <div className="result-meta">
          <span className="result-badge">Résumé extractif</span>
          {docType && docType !== "auto" && (
            <span className="result-badge secondary">{getDocTypeLabel(docType)}</span>
          )}
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

      <div className="result-content">
        <div className="result-text" dangerouslySetInnerHTML={{ __html: summary }} />
      </div>

      <button className="new-doc-btn" onClick={onReset}>
        Nouveau document
      </button>
    </div>
  );
}

export default SummaryDisplay;