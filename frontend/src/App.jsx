import { useState } from "react";
import Header from "./components/Header";
import UploadForm from "./components/UploadForm";
import SummaryDisplay from "./components/SummaryDisplay";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [instructions, setInstructions] = useState("");
  const [docType, setDocType] = useState("auto");
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");

  const handleSummarize = async () => {
    if (!file) {
      setError("Veuillez sélectionner un fichier");
      return;
    }

    setLoading(true);
    setError("");
    setSummary("");

    const formData = new FormData();
    formData.append("file", file);
    
    if (docType !== "auto") {
      formData.append("doc_type", docType);
    }
    
    if (instructions.trim()) {
      formData.append("instructions", instructions);
    }

    try {
      const res = await fetch("http://localhost:8000/summarize", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setSummary(data.summary);
        setFileName(data.filename);
      }
    } catch {
      setError("Erreur de connexion au serveur");
    }

    setLoading(false);
  };

  const handleReset = () => {
    setSummary("");
    setFile(null);
    setInstructions("");
    setDocType("auto");
    setError("");
    setFileName("");
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
  };

  return (
    <div className="app">
      <Header />
      
      <main className="main">
        {!summary ? (
          <div className="upload-section">
            <UploadForm 
              file={file}
              setFile={setFile}
              instructions={instructions}
              setInstructions={setInstructions}
              docType={docType}
              setDocType={setDocType}
            />
            
            <button
              className="submit-btn"
              onClick={handleSummarize}
              disabled={loading || !file}
            >
              {loading ? (
                <>
                  <span className="loader-dot"></span>
                  <span>Analyse en cours...</span>
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9h-4m-7 9A9 9 0 0 1 3 12m9 9v-4" />
                  </svg>
                  <span>Résumer</span>
                </>
              )}
            </button>
            
            {error && <div className="error-message">{error}</div>}
          </div>
        ) : (
          <SummaryDisplay 
            summary={summary}
            fileName={fileName}
            docType={docType}
            instructions={instructions}
            onReset={handleReset}
            onCopy={handleCopy}
          />
        )}
      </main>
    </div>
  );
}

export default App;