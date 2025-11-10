import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Send, CheckCircle, AlertCircle, Star, User, Mail, MessageCircleMore } from 'lucide-react';
import { GridBeams } from '@/components/magicui/grid-beams';
import usageTracker from '@/lib/usageTracker';

// Web3Forms Configuration
// Get your free access key from https://web3forms.com
const WEB3FORMS_ACCESS_KEY = '19e0390e-1daf-431c-868d-d4d9e99e025f';

// Mock feedback storage service (in-memory only)
class FeedbackService {
  static feedbackData = [];

  static saveFeedback(feedback) {
    try {
      const newFeedback = {
        id: Date.now() + Math.random(),
        ...feedback,
        timestamp: new Date().toISOString(),
        status: 'submitted'
      };
      
      this.feedbackData.push(newFeedback);
      
      console.log('Feedback saved successfully:', newFeedback);
      return { success: true, data: newFeedback };
    } catch (error) {
      console.error('Error saving feedback:', error);
      return { success: false, error: 'Failed to save feedback' };
    }
  }

  static getAllFeedback() {
    return this.feedbackData;
  }

  static getFeedbackStats() {
    const feedback = this.getAllFeedback();
    const total = feedback.length;
    const categories = feedback.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + 1;
      return acc;
    }, {});

    return {
      total,
      categories,
      recent: feedback.slice(-5).reverse()
    };
  }
}

// Enhanced Feedback Form Card Component
function FeedbackFormCard() {
  const [isSuccess, setIsSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    category: 'suggestion',
    message: ''
  });

  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      errors.name = 'Name must be at least 2 characters';
    }
    
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    if (!formData.message.trim()) {
      errors.message = 'Message is required';
    } else if (formData.message.trim().length < 10) {
      errors.message = 'Message must be at least 10 characters';
    } else if (formData.message.trim().length > 1000) {
      errors.message = 'Message must be less than 1000 characters';
    }
    
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setError('');
    
    try {
      const response = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          access_key: WEB3FORMS_ACCESS_KEY,
          ...formData,
          subject: `ParentShield Feedback - ${formData.category}`,
          from_name: 'ParentShield.AI Feedback System',
          replyto: formData.email,
        }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Increment usage counter when feedback is successfully submitted
        usageTracker.incrementUsage('userFeedback');
        
        setIsSuccess(true);
        setFormData({
          name: '',
          email: '',
          category: 'suggestion',
          message: ''
        });
        
        // Reset success message after 5 seconds
        setTimeout(() => {
          setIsSuccess(false);
        }, 5000);
      } else {
        setError(result.message || 'Failed to send feedback. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Feedback submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-blue-600/90 to-cyan-700/90 backdrop-blur-xl rounded-2xl h-full p-6 flex flex-col text-white shadow-2xl border border-blue-400/30 hover:shadow-blue-500/20 transition-all duration-300">
      {isSuccess ? (
        <div className="flex flex-col items-center justify-center h-full animate-in fade-in duration-500">
          <div className="relative">
            <CheckCircle className="w-20 h-20 text-green-300 mb-4 animate-pulse" />
            <div className="absolute inset-0 w-20 h-20 bg-green-300/20 rounded-full animate-ping"></div>
          </div>
          <h3 className="text-3xl font-bold mb-3 bg-gradient-to-r from-green-300 to-emerald-300 bg-clip-text text-transparent">
            Thank You!
          </h3>
          <p className="text-blue-100 text-center leading-relaxed">
            Your feedback has been received and will help us improve ParentShield.AI
          </p>
          <div className="mt-4 flex items-center gap-2 text-sm text-blue-200">
            <CheckCircle size={16} />
            <span>Feedback ID: #{Date.now().toString().slice(-6)}</span>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <MessageSquare className="w-8 h-8 text-blue-200" />
              <div>
                <h3 className="text-xl font-bold">Share Your Feedback</h3>
                <p className="text-blue-200 text-sm">Help us make ParentShield.AI better</p>
              </div>
            </div>
            <span className="bg-blue-800/50 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium">
              Secure
            </span>
          </div>

          <div className="space-y-4 flex-1">
            {/* Name Input */}
            <div>
              <label className="block text-sm font-medium text-blue-100 mb-2">
                <User size={16} className="inline mr-2" />
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                disabled={isSubmitting}
                className={`w-full px-4 py-3 bg-blue-700/40 backdrop-blur-sm border rounded-xl text-white placeholder-blue-300 text-sm focus:outline-none focus:ring-2 transition-all ${
                  fieldErrors.name 
                    ? 'border-red-400 focus:ring-red-400' 
                    : 'border-blue-500/50 focus:ring-blue-400'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                placeholder="Enter your full name"
                maxLength={50}
              />
              {fieldErrors.name && (
                <p className="mt-1 text-xs text-red-300 flex items-center gap-1">
                  <AlertCircle size={12} />
                  {fieldErrors.name}
                </p>
              )}
            </div>

            {/* Email Input */}
            <div>
              <label className="block text-sm font-medium text-blue-100 mb-2">
                <Mail size={16} className="inline mr-2" />
                Email Address
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                disabled={isSubmitting}
                className={`w-full px-4 py-3 bg-blue-700/40 backdrop-blur-sm border rounded-xl text-white placeholder-blue-300 text-sm focus:outline-none focus:ring-2 transition-all ${
                  fieldErrors.email 
                    ? 'border-red-400 focus:ring-red-400' 
                    : 'border-blue-500/50 focus:ring-blue-400'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                placeholder="your.email@example.com"
              />
              {fieldErrors.email && (
                <p className="mt-1 text-xs text-red-300 flex items-center gap-1">
                  <AlertCircle size={12} />
                  {fieldErrors.email}
                </p>
              )}
            </div>

            {/* Category Select */}
            <div>
              <label className="block text-sm font-medium text-blue-100 mb-2">
                Category
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleChange}
                disabled={isSubmitting}
                className="w-full px-4 py-3 bg-blue-700/40 backdrop-blur-sm border border-blue-500/50 rounded-xl text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="suggestion">💡 Suggestion</option>
                <option value="bug">🐛 Bug Report</option>
                <option value="feature">✨ Feature Request</option>
                <option value="improvement">⚡ Improvement</option>
                <option value="complaint">⚠ Complaint</option>
                <option value="praise">👏 Praise</option>
                <option value="other">🤔 Other</option>
              </select>
            </div>

            {/* Message Textarea */}
            <div>
              <label className="block text-sm font-medium text-blue-100 mb-2">
                <MessageCircleMore size={16} className="inline mr-2" />
                Your Message
              </label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                disabled={isSubmitting}
                rows="4"
                className={`w-full px-4 py-3 bg-blue-700/40 backdrop-blur-sm border rounded-xl text-white placeholder-blue-300 text-sm focus:outline-none focus:ring-2 resize-none transition-all ${
                  fieldErrors.message 
                    ? 'border-red-400 focus:ring-red-400' 
                    : 'border-blue-500/50 focus:ring-blue-400'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                placeholder="Please share your detailed feedback, suggestions, or any issues you've encountered..."
                maxLength={1000}
              />
              <div className="flex justify-between items-center mt-1">
                {fieldErrors.message ? (
                  <p className="text-xs text-red-300 flex items-center gap-1">
                    <AlertCircle size={12} />
                    {fieldErrors.message}
                  </p>
                ) : (
                  <span></span>
                )}
                <span className="text-xs text-blue-300">
                  {formData.message.length}/1000
                </span>
              </div>
            </div>

            {error && (
              <div className="flex items-center p-3 bg-red-500/20 backdrop-blur-sm border border-red-400/50 rounded-xl">
                <AlertCircle className="w-5 h-5 text-red-300 mr-3 flex-shrink-0" />
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}
          </div>

          <button
            onClick={handleSubmit}
            disabled={isSubmitting || Object.keys(fieldErrors).some(key => fieldErrors[key])}
            className="w-full mt-6 bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-3 rounded-xl font-semibold hover:from-blue-600 hover:to-cyan-600 transition-all duration-300 transform hover:translate-y-[-2px] hover:shadow-xl flex items-center justify-center text-sm disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg"
          >
            {isSubmitting ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3"></div>
                Submitting Your Feedback...
              </>
            ) : (
              <>
                <Send className="w-5 h-5 mr-3" />
                Submit Feedback
              </>
            )}
          </button>
        </>
      )}
    </div>
  );
}

// Feedback Impact Card
function FeedbackImpactCard() {
  const [stats, setStats] = useState({ total: 0, categories: {}, recent: [] });

  useEffect(() => {
    const updateStats = () => {
      const currentStats = FeedbackService.getFeedbackStats();
      setStats(currentStats);
    };

    updateStats();
    const interval = setInterval(updateStats, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gradient-to-br from-indigo-600/90 to-purple-700/90 backdrop-blur-xl rounded-2xl h-full p-6 flex flex-col justify-between text-white shadow-2xl border border-indigo-400/30 hover:shadow-indigo-500/20 transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <Star className="w-8 h-8 text-indigo-200 fill-indigo-200" />
        <span className="bg-indigo-800/50 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium">
          Impact
        </span>
      </div>
      
      <div className="mb-4">
        <h3 className="text-xl font-bold mb-2">Why Your Feedback Matters</h3>
        <p className="text-indigo-200 text-sm mb-4">Every voice helps us build better protection</p>
      </div>

      <div className="space-y-3 mb-6">
        <div className="flex items-center text-sm">
          <span className="w-2 h-2 bg-indigo-300 rounded-full mr-3"></span>
          <span className="text-indigo-200">Improves AI detection accuracy</span>
        </div>
        <div className="flex items-center text-sm">
          <span className="w-2 h-2 bg-purple-300 rounded-full mr-3"></span>
          <span className="text-indigo-200">Guides new feature development</span>
        </div>
        <div className="flex items-center text-sm">
          <span className="w-2 h-2 bg-pink-300 rounded-full mr-3"></span>
          <span className="text-indigo-200">Enhances user experience</span>
        </div>
        <div className="flex items-center text-sm">
          <span className="w-2 h-2 bg-cyan-300 rounded-full mr-3"></span>
          <span className="text-indigo-200">Builds safer digital spaces</span>
        </div>
      </div>

      {/* Live Feedback Stats - Removed community feedback text */}
      <div className="bg-indigo-800/30 rounded-xl p-4 backdrop-blur-sm border border-indigo-500/20">
        <div className="flex justify-between items-center">
          <span className="text-sm text-indigo-200">Feedback Count</span>
          <span className="text-lg font-bold text-white">{stats.total}</span>
        </div>
      </div>
    </div>
  );
}

// Main Feedback Dashboard Component
export default function FeedbackDashboard() {
  // Track usage when feedback is actually submitted, not on mount
  // Remove the useEffect that was incrementing on mount

  return (
    <div className="min-h-screen relative bg-[#05081A] overflow-x-hidden">
      {/* GridBeams Background */}
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

      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="px-4 lg:px-8 py-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600/20 to-cyan-600/20 rounded-full border border-blue-500/30 backdrop-blur-sm mb-6">
                <span className="text-blue-300 text-sm font-medium flex items-center gap-2">
                  <MessageSquare size={16} />
                  ParentShield.AI Feedback Center
                </span>
              </div>
              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-white via-blue-200 to-cyan-400 bg-clip-text text-transparent mb-6 leading-tight">
                Help Us Protect
                <br />
                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
                  Every Family
                </span>
              </h1>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
                Your feedback drives our mission to create the safest digital environment for families across India. Every suggestion matters.
              </p>
            </div>

            {/* Main Dashboard Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-12">
              {/* Feedback Form - Takes up 8 columns on large screens */}
              <div className="lg:col-span-8">
                <FeedbackFormCard />
              </div>

              {/* Impact Card - Takes up 4 columns on large screens */}
              <div className="lg:col-span-4">
                <FeedbackImpactCard />
              </div>
            </div>

            {/* Support Section - Removed 24/7 availability text */}
            <div className="bg-gradient-to-br from-purple-600/90 to-pink-600/90 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-purple-400/30 hover:shadow-purple-500/20 transition-all duration-300 mb-8">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <MessageSquare className="w-10 h-10 text-purple-200" />
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-2">Need Direct Support?</h3>
                    <p className="text-purple-200 leading-relaxed">
                      For urgent issues, technical problems, or detailed inquiries, our support team is ready to help you create a safer digital environment.
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="bg-purple-800/50 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium">
                    Support Available
                  </span>
                </div>
              </div>
              
              <div className="grid sm:grid-cols-1 gap-4">
                <a
                  href="mailto:support@parentshield.ai"
                  className="flex items-center justify-center gap-3 bg-purple-700/80 backdrop-blur-sm px-6 py-4 rounded-xl text-white font-medium hover:bg-purple-800/80 transition-all duration-300 transform hover:translate-y-[-2px] hover:shadow-lg"
                >
                  <Send size={20} />
                  support@parentshield.ai
                </a>
              </div>
            </div>

            {/* Stats Grid - Removed */}
          </div>
        </div>

        {/* Footer - Removed security and community text */}
        <div className="border-t border-slate-700/50 py-8">
          <div className="max-w-4xl mx-auto px-4 text-center">
            <p className="text-slate-400 leading-relaxed mb-4">
              Your feedback is completely secure and confidential. We use it exclusively to improve ParentShield.AI 
              and create safer digital experiences for families across India.
            </p>
          </div>
        </div>
        
        {/* Back to Dashboard Button */}
        <div className="text-center mt-8">
          <Link 
            to="/dashboard"
            className="inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}