import { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, Zap, BrainCircuit, Activity, X } from 'lucide-react';
import './index.css';

// Utilisez le port dynamique pour Docker Compose
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3500';

function App() {
  const [method, setMethod] = useState('vision'); // 'vision' or 'llm'
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      handleFileSelection(droppedFile);
    } else {
      setError("Seulement des images sont acceptées");
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) handleFileSelection(selectedFile);
  };

  const handleFileSelection = (fileObj) => {
    setFile(fileObj);
    setError(null);
    setResult(null);
    
    // Create preview URL
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(fileObj);
  };

  const resetSelection = (e) => {
    e.stopPropagation();
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if(fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('fichier', file);

    const endpoint = method === 'vision' ? `${API_URL}/predict/vision` : `${API_URL}/predict/llm`;

    try {
      const response = await axios.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (err) {
      if (err.response) {
        setError(err.response.data.detail || "Erreur de prédiction");
      } else {
        setError("Impossible de contacter le serveur (Backend)");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Tennis Vision App</h1>
        <p>Analyse d'image par Intelligence Artificielle</p>
      </header>

      <div className="glass-panel">
        <div className="method-selector">
          <button 
            className={`method-btn ${method === 'vision' ? 'active' : ''}`}
            onClick={() => { setMethod('vision'); setResult(null); }}
          >
            <Zap size={20} /> Deep Learning Keras
          </button>
          <button 
            className={`method-btn ${method === 'llm' ? 'active' : ''}`}
            onClick={() => { setMethod('llm'); setResult(null); }}
          >
            <BrainCircuit size={20} /> OpenRouter LLM
          </button>
        </div>

        <div 
          className={`dropzone ${isDragging ? 'active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !file && fileInputRef.current?.click()}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept="image/*" 
            style={{ display: 'none' }} 
          />
          
          {!file ? (
            <>
              <UploadCloud className="dropzone-icon" />
              <p className="drop-text">Glissez une photo de tennis, ou <span style={{color: "var(--accent)"}}>cliquez pour choisir</span></p>
            </>
          ) : (
            <div className="file-preview">
              <button 
                onClick={resetSelection} 
                style={{
                  position: 'absolute', top: 15, right: 15, 
                  background: 'rgba(0,0,0,0.5)', color: 'white', 
                  border: 'none', borderRadius: '50%', padding: 5,
                  cursor: 'pointer', zIndex: 10
                }}
              >
                <X size={20} />
              </button>
              <img src={preview} alt="Aperçu" />
            </div>
          )}
        </div>

        <button 
          className="submit-btn" 
          onClick={handleSubmit} 
          disabled={!file || loading}
        >
          {loading ? (
            <><Activity className="spinner" size={20} /> Analyse en cours...</>
          ) : (
            <><Zap size={20} /> Prédire le coup</>
          )}
        </button>

        {error && (
          <div className="error-msg">
            {error}
          </div>
        )}

        {result && (
          <div className="result-container">
            <div className="result-header">Résultat de l'analyse</div>
            <div className="result-class">{result.classe.replace('_', ' ')}</div>
            
            <div className="result-header" style={{marginTop: '1rem'}}>Niveau de confiance</div>
            <div className="result-confidence">
              <div className="confidence-bar-bg">
                <div 
                  className="confidence-bar-fill" 
                  style={{ width: `${Math.min(100, Math.max(0, result.confiance * 100))}%` }}
                ></div>
              </div>
              <div className="confidence-text">
                {(result.confiance * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
