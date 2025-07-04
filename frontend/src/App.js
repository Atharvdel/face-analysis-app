import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const bracket = "(";
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analysis, setAnalysis] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [animateHeader, setAnimateHeader] = useState(false);
  const [animateSteps, setAnimateSteps] = useState(false);
  
  // Refs for scrolling
  const uploadSectionRef = useRef(null);
  const previewSectionRef = useRef(null);
  const analysisSectionRef = useRef(null);

  // Get API URL from environment variable or fallback to localhost
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Trigger animations on load
  useEffect(() => {
    setAnimateHeader(true);
    setTimeout(() => setAnimateSteps(true), 400);
  }, []);

  // Scroll functions
  const scrollToUpload = () => {
    uploadSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToPreview = () => {
    previewSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToAnalysis = () => {
    analysisSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadSuccess(true);
      
      // Create a preview of the image
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
        // Auto-scroll to preview section
        setTimeout(scrollToPreview, 300);
      };
      reader.readAsDataURL(file);
      
      // Clear any previous error or analysis
      setError('');
      setAnalysis('');
    }
  };

  const handleSubmit = async () => {
  if (!selectedFile) {
    setError('Please select an image first');
    return;
  }
  
  setLoading(true);
  setError('');
  
  try {
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    // Use API_URL variable instead of hardcoded URL
    const response = await fetch(`${API_URL}/api/analyze-image`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Failed to analyze image');
    }
    
    const data = await response.json();
    setAnalysis(data.analysis);
    // Auto-scroll to analysis section
    setTimeout(scrollToAnalysis, 300);
  } catch (err) {
    setError(err.message || 'An error occurred during analysis');
  } finally {
    setLoading(false);
  }
};


  // Format analysis text with better styling
  const formatAnalysis = (text) => {
    if (!text) return null;
    return <ReactMarkdown className="markdown-content">{text}</ReactMarkdown>;
  };

  return (
    <div className="App">
      <header className={`App-header ${animateHeader ? 'fadeIn' : ''}`} style={{opacity: animateHeader ? 1 : 0, transition: 'opacity 0.8s ease-out'}}>
        <h1>StyliQ AI</h1>
        <p>StyliQ AI analyzes your face shape and delivers personalized hairstyle and accessory recommendations tailored to your unique features—transforming selfies into professional style advice at your fingertips.</p>
        <button onClick={scrollToUpload} className="try-now-btn">Under Maintainance :{bracket}</button>
      </header>
      
      <div 
        className="process-steps" 
        style={{
          opacity: animateSteps ? 1 : 0, 
          transform: animateSteps ? 'translateY(0)' : 'translateY(20px)',
          transition: 'opacity 0.6s ease-out, transform 0.6s ease-out'
        }}
      >
        <div className="step">
          <div className="step-number">1</div>
          <div className="step-text">Upload Image</div>
        </div>
        <div className="step-connector"></div>
        <div className="step">
          <div className="step-number">2</div>
          <div className="step-text">Face Analysis</div>
        </div>
        <div className="step-connector"></div>
        <div className="step">
          <div className="step-number">3</div>
          <div className="step-text">Get Feedback</div>
        </div>
      </div>
      
      <main className="App-main">
        <div className="upload-section" ref={uploadSectionRef}>
  <form>
    <div className="file-input-container">
      <div className="upload-icon">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <input 
        type="file" 
        onChange={handleFileChange} 
        accept="image/*"
        id="file-upload"
      />
      <label htmlFor="file-upload" className="file-upload-btn">
        {uploadSuccess ? 'Change Image' : 'Choose Image'}
      </label>
      {selectedFile && (
        <span className="file-name">
          {selectedFile.name}
        </span>
      )}
    </div>
  </form>
  
  {error && <div className="error-message">{error}</div>}
</div>

        
        <div className="results-container">
          <div className="preview-container" ref={previewSectionRef}>
  <h2>Image Preview</h2>
  <div className="preview-content">
    {preview ? (
      <>
        <img src={preview} alt="Preview" className="image-preview" />
        <button 
          onClick={handleSubmit}
          className="analyze-btn"
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Analyze Image'}
        </button>
      </>
    ) : (
      <div className="upload-placeholder">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p>Upload an image to see preview</p>
      </div>
    )}
  </div>
</div>

          
          <div className="analysis-container" ref={analysisSectionRef}>
            <h2>Analysis Results</h2>
            <div className="analysis-content">
              {loading ? (
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <p>Analyzing your image with AI...</p>
                </div>
              ) : analysis ? (
                <div className="analysis-text">
                  {formatAnalysis(analysis)}
                </div>
              ) : (
                <div className="upload-placeholder">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
                  </svg>
                  <p>Analysis results will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
