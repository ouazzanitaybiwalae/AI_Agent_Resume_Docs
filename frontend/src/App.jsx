import { useState } from 'react'
import Header from './components/Header'
import UploadForm from './components/UploadForm'
import DocTypeSelect from './components/DocTypeSelect'
import Loader from './components/Loader'
import SummaryDisplay from './components/SummaryDisplay'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null)
  const [options, setOptions] = useState({
    style: 'abstractif',
    length: 'moyen',
    chunk: 'paragraphs',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('style', options.style)
    formData.append('target_length', options.length)
    formData.append('chunk_method', options.chunk)

    try {
      const res = await fetch(`${API_URL}/summarize`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Erreur inconnue.' }))
        throw new Error(err.detail || `Erreur ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
    } catch (e) {
      setError(e.message.includes('fetch')
        ? `Impossible de joindre l'API sur ${API_URL}. Vérifiez que le serveur tourne.`
        : e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <Header />

      <main className="main">
        {!result ? (
          <>
            <UploadForm file={file} setFile={setFile} />

            <DocTypeSelect options={options} setOptions={setOptions} />

            {error && (
              <div className="error-box">{error}</div>
            )}

            <button
              className="btn-submit"
              onClick={handleSubmit}
              disabled={!file || loading}
            >
              {loading ? 'Traitement en cours…' : 'Résumer le document'}
            </button>

            {loading && <Loader />}
          </>
        ) : (
          <SummaryDisplay result={result} onReset={handleReset} />
        )}
      </main>
    </div>
  )
}

export default App
