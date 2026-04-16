import { useState } from "react";
import Header from "./components/Header";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setError("Veuillez sélectionner un fichier");
      return;
    }

    setLoading(true);
    setError("");
    setSummary("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/summarize", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setSummary(data.summary);
    // eslint-disable-next-line no-unused-vars
    } catch (err) {
      setError("Erreur lors du résumé");
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <Header />

      <main className="main">
        <div className="card">
          <div className="card-label">UPLOAD</div>

          <div className="drop-zone">
            <input
              type="file"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <div className="drop-text">
              <strong>Choisir un document</strong>
            </div>
            <div className="drop-formats">
              PDF, DOCX, TXT
            </div>
          </div>

          {file && (
            <div className="file-selected">
              <span className="file-name">{file.name}</span>
              <button
                className="file-remove"
                onClick={() => setFile(null)}
              >
                ✕
              </button>
            </div>
          )}
        </div>

        <button
          className="btn-submit"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "Analyse..." : "Résumer"}
        </button>

        {error && <div className="error-box">{error}</div>}

        {loading && (
          <div className="loader">
            <div className="loader-ring"></div>
            <div className="loader-step">Traitement du document...</div>
          </div>
        )}

        {summary && (
          <div className="card result-card">
            <div className="result-header">
              <div className="result-badges">
                <span className="badge badge-green">Résumé</span>
              </div>
            </div>

            <div className="result-text">{summary}</div>

            <button
              className="btn-new"
              onClick={() => {
                setSummary("");
                setFile(null);
              }}
            >
              Nouveau document
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;