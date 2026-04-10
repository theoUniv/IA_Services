import { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, Zap, BrainCircuit, Activity, X, Trophy, Swords, User, Image as ImageIcon } from 'lucide-react';
import './index.css';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://72.60.37.180:3500';

function App() {
  const [appMode, setAppMode] = useState('vision'); // 'vision' or 'match'

  // --- VISION STATE ---
  const [method, setMethod] = useState('vision'); // 'vision' or 'llm'
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  // --- MATCH STATE ---
  const [joueur1, setJoueur1] = useState('');
  const [joueur2, setJoueur2] = useState('');
  const [surface, setSurface] = useState('Hard');
  const [matchResult, setMatchResult] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchError, setMatchError] = useState(null);

  // --- VISION HANDLERS ---
  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const handleDragLeave = () => { setIsDragging(false); };
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
    setFile(fileObj); setError(null); setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(fileObj);
  };

  const resetSelection = (e) => {
    e.stopPropagation();
    setFile(null); setPreview(null); setResult(null); setError(null);
    if(fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmitVision = async () => {
    if (!file) return;
    setLoading(true); setError(null); setResult(null);
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

  // --- MATCH HANDLERS ---
  const handleSubmitMatch = async () => {
    if (!joueur1 || !joueur2) {
      setMatchError("Veuillez entrer les deux joueurs.");
      return;
    }
    setMatchLoading(true); setMatchError(null); setMatchResult(null);

    try {
      const response = await axios.post(`${API_URL}/predict/match`, {
        joueur_1: joueur1,
        joueur_2: joueur2,
        surface: surface
      });
      setMatchResult(response.data);
    } catch (err) {
      if (err.response) {
        setMatchError(err.response.data.detail || "Erreur lors de la prédiction du match");
      } else {
        setMatchError("Impossible de contacter le serveur (Backend)");
      }
    } finally {
      setMatchLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Tennis Vision & API</h1>
        <p>Intelligence Artificielle au service du Tennis</p>
      </header>

      {/* Main Mode Selector */}
      <div className="mode-selector-main">
        <button 
          className={`main-tab ${appMode === 'vision' ? 'active' : ''}`}
          onClick={() => setAppMode('vision')}
        >
          <ImageIcon size={20} /> Vision (Image)
        </button>
        <button 
          className={`main-tab ${appMode === 'match' ? 'active' : ''}`}
          onClick={() => setAppMode('match')}
        >
          <Swords size={20} /> Prédiction Match ATP
        </button>
      </div>

      <div className="glass-panel">
        
        {appMode === 'vision' && (
          <div className="vision-mode fade-in">
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
                type="file" ref={fileInputRef} onChange={handleFileChange} 
                accept="image/*" style={{ display: 'none' }} 
              />
              
              {!file ? (
                <>
                  <UploadCloud className="dropzone-icon" />
                  <p className="drop-text">Glissez une photo de tennis, ou <span style={{color: "var(--accent)"}}>cliquez pour choisir</span></p>
                </>
              ) : (
                <div className="file-preview">
                  <button onClick={resetSelection} className="close-btn"><X size={20} /></button>
                  <img src={preview} alt="Aperçu" />
                </div>
              )}
            </div>

            <button className="submit-btn" onClick={handleSubmitVision} disabled={!file || loading}>
              {loading ? <><Activity className="spinner" size={20} /> Analyse en cours...</> : <><Zap size={20} /> Prédire le coup</>}
            </button>

            {error && <div className="error-msg">{error}</div>}

            {result && (
              <div className="result-container">
                <div className="result-header">Résultat de l'analyse</div>
                <div className="result-class">{result.classe.replace('_', ' ')}</div>
                
                <div className="result-header" style={{marginTop: '1rem'}}>Niveau de confiance</div>
                <div className="result-confidence">
                  <div className="confidence-bar-bg">
                    <div className="confidence-bar-fill" style={{ width: `${Math.min(100, Math.max(0, result.confiance * 100))}%` }}></div>
                  </div>
                  <div className="confidence-text">{(result.confiance * 100).toFixed(1)}%</div>
                </div>
              </div>
            )}
          </div>
        )}

        {appMode === 'match' && (
          <div className="match-mode fade-in">
            <h2 style={{ marginBottom: "1.5rem", textAlign: "center" }}>Qui va gagner ?</h2>
            <div className="match-inputs" style={{ display: "flex",flexDirection:"column", gap: "1rem" }}>
              
              <div style={{ display: "flex", gap: "1rem" }}>
                <div style={{ flex: 1 }}>
                  <label className="result-header">Joueur 1 (ex: Federer R.)</label>
                  <div className="input-group">
                    <User size={18} style={{color: "var(--text-muted)", marginRight: "10px"}} />
                    <input type="text" placeholder="Federer R." value={joueur1} onChange={(e) => setJoueur1(e.target.value)} />
                  </div>
                </div>
                <div style={{ flex: 1 }}>
                  <label className="result-header">Joueur 2 (ex: Nadal R.)</label>
                  <div className="input-group">
                    <User size={18} style={{color: "var(--text-muted)", marginRight: "10px"}} />
                    <input type="text" placeholder="Nadal R." value={joueur2} onChange={(e) => setJoueur2(e.target.value)} />
                  </div>
                </div>
              </div>

              <div>
                <label className="result-header">Surface</label>
                <select className="surface-select" value={surface} onChange={(e) => setSurface(e.target.value)}>
                  <option value="Hard">Dur (Hard)</option>
                  <option value="Clay">Terre battue (Clay)</option>
                  <option value="Grass">Gazon (Grass)</option>
                  <option value="Carpet">Synthétique (Carpet)</option>
                </select>
              </div>
            </div>

            <button className="submit-btn" onClick={handleSubmitMatch} disabled={matchLoading}>
              {matchLoading ? <><Activity className="spinner" size={20} /> Calcul en cours...</> : <><Swords size={20} /> Lancer la Simulation</>}
            </button>

            {matchError && <div className="error-msg">{matchError}</div>}

            {matchResult && (
              <div className="result-container" style={{ textAlign: "center" }}>
                <Trophy size={48} color="var(--accent)" style={{ margin: "0 auto", marginBottom: "1rem" }} />
                <div className="result-header">Gagnant Prédit</div>
                <div className="result-class" style={{ fontSize: "2.5rem" }}>{matchResult.gagnant_predit}</div>
                
                <div style={{ display: "flex", justifyContent: "space-between", marginTop: "2rem", background: "rgba(0,0,0,0.3)", padding: "1rem", borderRadius: "8px" }}>
                  <div style={{ textAlign: "left" }}>
                    <div style={{ fontWeight: 600, fontSize: "1.2rem", color: matchResult.gagnant_predit === matchResult.joueur_1 ? "var(--accent)" : "white" }}>
                      {matchResult.joueur_1}
                    </div>
                    <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Probabilité : {(matchResult.probabilite_j1 * 100).toFixed(1)}%</div>
                    <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Rang actuel : {matchResult.rank_1_actuel}</div>
                  </div>
                  <h3 style={{ margin: "auto", color: "var(--text-muted)" }}>VS</h3>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontWeight: 600, fontSize: "1.2rem", color: matchResult.gagnant_predit === matchResult.joueur_2 ? "var(--accent)" : "white" }}>
                      {matchResult.joueur_2}
                    </div>
                    <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Probabilité : {(matchResult.probabilite_j2 * 100).toFixed(1)}%</div>
                    <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>Rang actuel : {matchResult.rank_2_actuel}</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

export default App;
