function BtnGroup({ options, value, onChange }) {
  return (
    <div className="btn-group">
      {options.map((opt) => (
        <button
          key={opt.value}
          className={`btn-opt${value === opt.value ? ' active' : ''}`}
          onClick={() => onChange(opt.value)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}

function DocTypeSelect({ options, setOptions }) {
  const set = (key) => (val) => setOptions((prev) => ({ ...prev, [key]: val }))

  return (
    <div className="card">
      <p className="card-label">02 — Options de résumé</p>
      <div className="options-grid">

        <div className="option-group">
          <label>Style</label>
          <BtnGroup
            value={options.style}
            onChange={set('style')}
            options={[
              { value: 'abstractif', label: 'Abstractif' },
              { value: 'extractif',  label: 'Extractif' },
            ]}
          />
        </div>

        <div className="option-group">
          <label>Longueur</label>
          <BtnGroup
            value={options.length}
            onChange={set('length')}
            options={[
              { value: 'court', label: 'Court' },
              { value: 'moyen', label: 'Moyen' },
              { value: 'long',  label: 'Long'  },
            ]}
          />
        </div>

        <div className="option-group">
          <label>Découpage</label>
          <BtnGroup
            value={options.chunk}
            onChange={set('chunk')}
            options={[
              { value: 'paragraphs', label: 'Paragraphes' },
              { value: 'tokens',     label: 'Tokens'      },
            ]}
          />
        </div>

      </div>
    </div>
  )
}

export default DocTypeSelect
