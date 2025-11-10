import React, { useState, useRef, useEffect } from 'react';
import { GridBeams } from '@/components/magicui/grid-beams';
import Navbar from '@/components/navbar';
import { Link } from 'react-router-dom';
import usageTracker from '@/lib/usageTracker';

const MessageFraud = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const API_BASE_URL = 'http://localhost:5000/api';

  // Track usage when image is actually analyzed
  const incrementUsage = () => {
    usageTracker.incrementUsage('messageFraud');
  };

  const handleFile = async (file) => {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    // Increment usage counter when user actually uses the feature
    incrementUsage();

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('screenshot', file);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to analyze image. Please try again.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragActive(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#020412' }}>
      {/* Grid Beams Background */}
      <div className="fixed inset-0 z-0">
        <GridBeams
          gridSize={0}
          gridColor="rgba(255, 255, 255, 0.2)"
          rayCount={20}
          rayOpacity={0.55}
          raySpeed={1.5}
          rayLength="40vh"
          gridFadeStart={5}
          gridFadeEnd={90}
          className="h-full w-full"
        />
      </div>
      
      {/* Navbar */}
      <div className="relative z-10">
        <Navbar />
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="text-center py-12 px-4 sm:py-16 lg:py-20">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-4 text-white">
              Message Fraud
              <br />
              <span className="text-[#BDA7FF]">
                Detector
              </span>
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto leading-relaxed">
              Advanced AI-powered detection system to identify fraudulent messages from screenshots
            </p>
          </div>
        </header>

        {/* Main Content Container */}
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
          {/* Upload Section */}
          <div className="mb-12">
            <div
              className={`
                border-2 border-dashed rounded-2xl p-8 sm:p-12 lg:p-16 text-center cursor-pointer
                transition-all duration-300 ease-in-out backdrop-blur-md
                hover:backdrop-blur-lg hover:border-blue-400/60 hover:shadow-2xl hover:shadow-blue-500/10
                ${isDragActive 
                  ? 'bg-blue-500/10 border-blue-400/80 shadow-2xl shadow-blue-500/20 scale-[1.02]' 
                  : 'bg-white/5 border-white/20 hover:bg-white/10'
                }
              `}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={handleClick}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="hidden"
              />
              
              {/* Upload Icon */}
              <div className="mb-6">
                <div className="relative">
                  <svg
                    className="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 mx-auto text-blue-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                  <div className="absolute inset-0 bg-blue-400/20 rounded-full blur-xl"></div>
                </div>
              </div>
              
              {isDragActive ? (
                <div className="space-y-2">
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-blue-400">
                    Drop the screenshot here...
                  </p>
                  <p className="text-gray-300">Release to analyze</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-xl sm:text-2xl lg:text-3xl font-bold text-white">
                    Upload Screenshot to Analyze
                  </p>
                  <p className="text-gray-300 text-base sm:text-lg">
                    Drag & drop your message screenshot here
                  </p>
                  <div className="inline-flex items-center justify-center px-6 py-3 bg-[#BDA7FF] rounded-2xl transition-all duration-200">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Choose File
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-12">
              <div className="relative inline-block mb-6">
                <div className="animate-spin rounded-full h-12 w-12 sm:h-16 sm:w-16 border-4 border-blue-500/20 border-t-blue-500"></div>
                <div className="absolute inset-0 bg-blue-400/10 rounded-full blur-lg"></div>
              </div>
              <div className="space-y-2">
                <p className="text-xl sm:text-2xl font-bold text-white">Analyzing Screenshot...</p>
                <p className="text-gray-300">AI is processing your image for fraud detection</p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-500/20 backdrop-blur-md border border-red-500/30 text-white p-6 rounded-xl flex items-center gap-4 mb-8">
              <div className="flex-shrink-0">
                <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div>
                <h3 className="font-bold text-lg mb-1">Analysis Failed</h3>
                <p className="text-red-200">{error}</p>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl shadow-2xl p-6 sm:p-8">
              {/* Fraud Analysis Result */}
              <div className={`
                text-center p-8 sm:p-10 lg:p-12 rounded-xl mb-8 relative overflow-hidden
                ${result.fraud_analysis.is_fraud 
                  ? 'bg-gradient-to-r from-red-500/90 to-red-600/90 backdrop-blur-sm' 
                  : 'bg-gradient-to-r from-green-500/90 to-green-600/90 backdrop-blur-sm'
                }
              `}>
                <div className="absolute inset-0 bg-black/10"></div>
                <div className="relative z-10">
                  <div className="mb-6">
                    {result.fraud_analysis.is_fraud ? (
                      <div className="relative">
                        <svg className="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 mx-auto text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                        <div className="absolute inset-0 bg-red-400/30 rounded-full blur-2xl"></div>
                      </div>
                    ) : (
                      <div className="relative">
                        <svg className="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 mx-auto text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="absolute inset-0 bg-green-400/30 rounded-full blur-2xl"></div>
                      </div>
                    )}
                  </div>
                  
                  <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold mb-6 text-white">
                    {result.fraud_analysis.is_fraud 
                      ? '🚨 FRAUDULENT MESSAGE DETECTED' 
                      : '✅ MESSAGE APPEARS SAFE'
                    }
                  </h2>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-md mx-auto">
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-sm text-white/80 mb-1">Confidence Level</p>
                      <p className="text-2xl font-bold text-white">
                        {(result.fraud_analysis.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                      <p className="text-sm text-white/80 mb-1">Detection Method</p>
                      <p className="text-lg font-semibold text-white">
                        {result.fraud_analysis.method}
                      </p>
                    </div>
                  </div>

                  {result.fraud_analysis.matched_keywords && result.fraud_analysis.matched_keywords.length > 0 && (
                    <div className="mt-8">
                      <p className="text-lg font-bold mb-4 text-white">Suspicious Keywords Found:</p>
                      <div className="flex flex-wrap gap-2 justify-center max-w-2xl mx-auto">
                        {result.fraud_analysis.matched_keywords.map((keyword, index) => (
                          <span 
                            key={index}
                            className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-white border border-white/10"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Link Analysis Results */}
                  {result.fraud_analysis.link_analysis && result.fraud_analysis.link_analysis.overall && (
                    <div className="mt-8 bg-white/20 backdrop-blur-sm rounded-xl p-6 border border-white/30">
                      <h3 className="text-xl font-bold text-white mb-4">🔗 Link Analysis</h3>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
                        <div className="bg-white/10 rounded-lg p-3">
                          <p className="text-sm text-white/80 mb-1">Total Links</p>
                          <p className="text-2xl font-bold text-white">
                            {result.fraud_analysis.link_analysis.overall.total_links}
                          </p>
                        </div>
                        <div className="bg-white/10 rounded-lg p-3">
                          <p className="text-sm text-white/80 mb-1">Suspicious Links</p>
                          <p className={`text-2xl font-bold ${
                            result.fraud_analysis.link_analysis.overall.suspicious_links > 0 
                              ? 'text-red-400' 
                              : 'text-green-400'
                          }`}>
                            {result.fraud_analysis.link_analysis.overall.suspicious_links}
                          </p>
                        </div>
                        <div className="bg-white/10 rounded-lg p-3">
                          <p className="text-sm text-white/80 mb-1">Risk Level</p>
                          <p className={`text-xl font-bold ${
                            result.fraud_analysis.link_analysis.overall.risk_level === 'high' 
                              ? 'text-red-400' 
                              : result.fraud_analysis.link_analysis.overall.risk_level === 'medium' 
                                ? 'text-yellow-400' 
                                : 'text-green-400'
                          }`}>
                            {result.fraud_analysis.link_analysis.overall.risk_level.charAt(0).toUpperCase() + 
                             result.fraud_analysis.link_analysis.overall.risk_level.slice(1)}
                          </p>
                        </div>
                      </div>
                      
                      {result.fraud_analysis.link_analysis.links && result.fraud_analysis.link_analysis.links.length > 0 && (
                        <div className="mt-4">
                          <h4 className="text-lg font-semibold text-white mb-3">Analyzed Links:</h4>
                          <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
                            {result.fraud_analysis.link_analysis.links.map((link, index) => (
                              <div 
                                key={index} 
                                className={`p-3 rounded-lg border ${
                                  link.is_suspicious 
                                    ? 'bg-red-500/20 border-red-500/50' 
                                    : 'bg-green-500/20 border-green-500/50'
                                }`}
                              >
                                <div className="flex items-start">
                                  <span className={`mr-2 mt-1 text-lg ${
                                    link.is_suspicious ? 'text-red-400' : 'text-green-400'
                                  }`}>
                                    {link.is_suspicious ? '⚠️' : '✅'}
                                  </span>
                                  <div className="flex-1">
                                    <p className="text-white font-mono text-sm break-all">
                                      {link.url}
                                    </p>
                                    {link.issues && link.issues.length > 0 && (
                                      <div className="mt-2">
                                        <p className="text-xs text-white/80 mb-1">Issues:</p>
                                        <ul className="text-xs text-red-200 space-y-1">
                                          {link.issues.map((issue, i) => (
                                            <li key={i} className="flex items-start">
                                              <span className="mr-1">•</span>
                                              <span>{issue}</span>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}
                                  </div>
                                  <span className={`text-xs px-2 py-1 rounded ${
                                    link.is_suspicious 
                                      ? 'bg-red-500/30 text-red-200' 
                                      : 'bg-green-500/30 text-green-200'
                                  }`}>
                                    {(link.safety_score * 100).toFixed(0)}% safe
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Extracted Text */}
              <div className="border-t border-white/20 pt-8">
                <h3 className="text-xl sm:text-2xl font-bold text-white mb-6 flex items-center gap-3">
                  <span className="text-2xl">📝</span>
                  Extracted Text Analysis
                </h3>
                <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-xl p-6">
                  <div className="bg-black/30 border-l-4 border-blue-400 rounded-r-lg p-4">
                    <pre className="whitespace-pre-wrap text-gray-200 font-mono text-sm leading-relaxed max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-white/20 scrollbar-track-transparent">
                      {result.extracted_text || 'No text found in the image'}
                    </pre>
                  </div>
                </div>
              </div>

              {/* Additional Info */}
              {result.fraud_analysis.method === "Keyword Analysis" && (
                <div className="mt-8 p-6 bg-blue-500/20 backdrop-blur-sm border border-blue-400/30 rounded-xl">
                  <div className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h4 className="font-bold text-blue-400 mb-2">Detection Method Note</h4>
                      <p className="text-sm text-blue-200 leading-relaxed">
                        This analysis used keyword-based detection. For enhanced accuracy with machine learning models, 
                        ensure the ML model is properly trained and loaded by running <code className="bg-blue-400/20 text-blue-300 px-2 py-1 rounded font-mono text-xs">fraud_model.py</code> first.
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Back to Dashboard Button */}
          <div className="text-center mt-8">
            <Link 
              to="/dashboard"
              className="inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </main>
      </div>
    </div>
  );
};

export default MessageFraud;