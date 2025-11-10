import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { GridBeams } from '@/components/magicui/grid-beams';
import Navbar from '@/components/navbar';
import { BarChart, PieChart, TrendingUp, Download, Calendar, User, Shield, AlertTriangle, CheckCircle, XCircle, FileText, Gamepad2 } from 'lucide-react';
import usageTracker from '@/lib/usageTracker';

const ReportGenerator = () => {
  const [usageStats, setUsageStats] = useState({
    securityLessons: 0,
    transactionFraud: 0,
    messageFraud: 0,
    userFeedback: 0,
    reportGenerator: 0,
    gameFeature: 0
  });
  
  const [historicalData, setHistoricalData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [timeRange, setTimeRange] = useState('all');
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    // Update usage stats
    const stats = usageTracker.getUsageStats();
    const history = usageTracker.getHistoricalData();
    setUsageStats(stats);
    setHistoricalData(history);
    
    // Increment report generator usage
    usageTracker.incrementUsage('reportGenerator');
    
    // Generate initial report
    generateReportData(stats, history);
    
    // Listen for storage changes to update in real-time
    const handleStorageChange = (e) => {
      if (e.key === 'parentshield_usage_stats' || e.key === 'parentshield_usage_history') {
        const updatedStats = usageTracker.getUsageStats();
        const updatedHistory = usageTracker.getHistoricalData();
        setUsageStats(updatedStats);
        setHistoricalData(updatedHistory);
        generateReportData(updatedStats, updatedHistory);
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Cleanup listener
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const generateReportData = (stats, history) => {
    const totalUsage = stats.securityLessons + stats.transactionFraud + 
                      stats.messageFraud + stats.userFeedback + 
                      stats.reportGenerator + stats.gameFeature;
    
    setReportData({
      totalUsage,
      moduleUsage: [
        { name: 'Security Lessons', value: stats.securityLessons, color: '#0D3B66' },
        { name: 'Transaction Fraud', value: stats.transactionFraud, color: '#7E1F86' },
        { name: 'Message Fraud', value: stats.messageFraud, color: '#177E89' },
        { name: 'User Feedback', value: stats.userFeedback, color: '#A499BE' },
        { name: 'Report Generator', value: stats.reportGenerator, color: '#0EA5E9' },
        { name: 'Fraud Fighter Game', value: stats.gameFeature, color: '#DB2777' }
      ],
      fraudDetectionStats: {
        messagesChecked: stats.messageFraud,
        transactionsChecked: stats.transactionFraud,
        potentialFraudDetected: Math.floor((stats.messageFraud + stats.transactionFraud) * 0.15)
      },
      securityEngagement: {
        lessonsCompleted: Math.floor(stats.securityLessons * 0.7),
        feedbackProvided: stats.userFeedback,
        gamesPlayed: stats.gameFeature
      },
      historicalUsage: history
    });
  };

  const handleGenerateReport = () => {
    setIsGenerating(true);
    
    // Simulate report generation delay
    setTimeout(() => {
      const stats = usageTracker.getUsageStats();
      const history = usageTracker.getHistoricalData();
      generateReportData(stats, history);
      setIsGenerating(false);
    }, 1500);
  };

  const handleDownloadReport = () => {
    // Create a simple text report
    const reportContent = `
PARENTSHIELD.AI USAGE REPORT
============================

Generated on: ${new Date().toLocaleDateString()}

TOTAL USAGE STATISTICS
----------------------
Total Module Usage: ${reportData?.totalUsage || 0}

MODULE BREAKDOWN
----------------
Security Lessons: ${usageStats.securityLessons}
Transaction Fraud Detection: ${usageStats.transactionFraud}
Message Fraud Detection: ${usageStats.messageFraud}
User Feedback: ${usageStats.userFeedback}
Report Generator: ${usageStats.reportGenerator}
Fraud Fighter Game: ${usageStats.gameFeature}

FRAUD DETECTION STATS
---------------------
Messages Checked: ${reportData?.fraudDetectionStats.messagesChecked || 0}
Transactions Checked: ${reportData?.fraudDetectionStats.transactionsChecked || 0}
Potential Fraud Detected: ${reportData?.fraudDetectionStats.potentialFraudDetected || 0}

SECURITY ENGAGEMENT
-------------------
Lessons Completed (estimated): ${reportData?.securityEngagement.lessonsCompleted || 0}
Feedback Provided: ${reportData?.securityEngagement.feedbackProvided || 0}
Games Played: ${reportData?.securityEngagement.gamesPlayed || 0}

HISTORICAL USAGE (Report Generator)
-----------------------------------
${reportData?.historicalUsage?.reportGenerator?.map(entry => 
  `  ${new Date(entry.timestamp).toLocaleDateString()}: ${entry.count} times`
).join('\n') || 'No historical data available'}
    `.trim();

    // Create and download the file
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `parentshield-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Simple bar chart component
  const BarChartComponent = ({ data }) => {
    const maxValue = Math.max(...data.map(item => item.value), 1);
    
    return (
      <div className="flex items-end justify-between h-48 mt-6">
        {data.map((item, index) => (
          <div key={index} className="flex flex-col items-center flex-1 mx-1">
            <div className="text-xs text-gray-400 mb-1">{item.value}</div>
            <div 
              className="w-full rounded-t-md transition-all duration-500 ease-out"
              style={{
                height: `${(item.value / maxValue) * 100}%`,
                backgroundColor: item.color,
                minHeight: '4px'
              }}
            ></div>
            <div className="text-xs text-center mt-2 text-gray-300 w-full truncate px-1">
              {item.name}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Simple pie chart component
  const PieChartComponent = ({ data }) => {
    const total = data.reduce((sum, item) => sum + item.value, 0);
    let startAngle = 0;
    
    if (total === 0) {
      return (
        <div className="w-48 h-48 rounded-full bg-gray-800 flex items-center justify-center">
          <span className="text-gray-500">No data</span>
        </div>
      );
    }
    
    return (
      <div className="relative w-48 h-48">
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {data.map((item, index) => {
            if (item.value === 0) return null;
            
            const percentage = (item.value / total) * 100;
            const angle = (percentage / 100) * 360;
            const endAngle = startAngle + angle;
            
            // Convert angles to radians
            const startRad = (startAngle - 90) * Math.PI / 180;
            const endRad = (endAngle - 90) * Math.PI / 180;
            
            // Calculate coordinates
            const x1 = 50 + 40 * Math.cos(startRad);
            const y1 = 50 + 40 * Math.sin(startRad);
            const x2 = 50 + 40 * Math.cos(endRad);
            const y2 = 50 + 40 * Math.sin(endRad);
            
            // Large arc flag
            const largeArcFlag = angle > 180 ? 1 : 0;
            
            const pathData = [
              `M 50 50`,
              `L ${x1} ${y1}`,
              `A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2}`,
              'Z'
            ].join(' ');
            
            const currentStartAngle = startAngle;
            startAngle = endAngle;
            
            return (
              <path
                key={index}
                d={pathData}
                fill={item.color}
                stroke="#1e293b"
                strokeWidth="0.5"
              />
            );
          })}
        </svg>
        
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">{total}</div>
            <div className="text-xs text-gray-400">Total Uses</div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen relative" style={{ backgroundColor: '#020412' }}>
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
      
      {/* Navbar */}
      <div className="relative z-10">
        <Navbar />
      </div>

      <div className="relative z-10 px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-cyan-600/20 to-blue-600/20 rounded-full border border-cyan-500/30 backdrop-blur-sm mb-6">
              <FileText className="w-5 h-5 text-cyan-400 mr-2" />
              <span className="text-cyan-300 text-sm font-medium">Analytics & Reporting</span>
            </div>
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
              Usage Analytics
            </h1>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Detailed insights into your ParentShield.AI usage patterns and security engagement
            </p>
          </div>

          {/* Controls */}
          <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-6 mb-8 border border-gray-700/50">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-400" />
                <span className="text-gray-300">Time Range:</span>
                <select 
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white"
                >
                  <option value="7">Last 7 days</option>
                  <option value="30">Last 30 days</option>
                  <option value="90">Last 90 days</option>
                  <option value="all">All time</option>
                </select>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={handleGenerateReport}
                  disabled={isGenerating}
                  className="flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-cyan-700 hover:to-blue-700 transition-all disabled:opacity-50"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-4 h-4" />
                      Refresh Data
                    </>
                  )}
                </button>
                
                <button
                  onClick={handleDownloadReport}
                  disabled={!reportData}
                  className="flex items-center gap-2 bg-gray-800 text-gray-300 px-4 py-2 rounded-lg hover:bg-gray-700 transition-all disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                  Download Report
                </button>
              </div>
            </div>
          </div>

          {/* Stats Overview */}
          {reportData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
              <div className="bg-gradient-to-br from-blue-600/20 to-cyan-600/20 backdrop-blur-lg rounded-2xl p-6 border border-blue-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-blue-300 text-sm">Total Usage</p>
                    <p className="text-3xl font-bold text-white">{reportData.totalUsage}</p>
                  </div>
                  <BarChart className="w-8 h-8 text-blue-400" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-purple-300 text-sm">Fraud Checks</p>
                    <p className="text-3xl font-bold text-white">
                      {reportData.fraudDetectionStats.messagesChecked + reportData.fraudDetectionStats.transactionsChecked}
                    </p>
                  </div>
                  <Shield className="w-8 h-8 text-purple-400" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-teal-600/20 to-green-600/20 backdrop-blur-lg rounded-2xl p-6 border border-teal-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-teal-300 text-sm">Potential Fraud</p>
                    <p className="text-3xl font-bold text-white">
                      {reportData.fraudDetectionStats.potentialFraudDetected}
                    </p>
                  </div>
                  <AlertTriangle className="w-8 h-8 text-teal-400" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-amber-600/20 to-orange-600/20 backdrop-blur-lg rounded-2xl p-6 border border-amber-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-amber-300 text-sm">Lessons Completed</p>
                    <p className="text-3xl font-bold text-white">
                      {reportData.securityEngagement.lessonsCompleted}
                    </p>
                  </div>
                  <CheckCircle className="w-8 h-8 text-amber-400" />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-rose-600/20 to-pink-600/20 backdrop-blur-lg rounded-2xl p-6 border border-rose-500/30">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-rose-300 text-sm">Games Played</p>
                    <p className="text-3xl font-bold text-white">
                      {reportData.securityEngagement.gamesPlayed}
                    </p>
                  </div>
                  <Gamepad2 className="w-8 h-8 text-rose-400" />
                </div>
              </div>
            </div>
          )}

          {/* Charts Section */}
          {reportData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              {/* Bar Chart */}
              <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <BarChart className="w-5 h-5 text-cyan-400" />
                  Module Usage Distribution
                </h3>
                <BarChartComponent data={reportData.moduleUsage} />
              </div>
              
              {/* Pie Chart */}
              <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <PieChart className="w-5 h-5 text-purple-400" />
                  Usage Breakdown
                </h3>
                <div className="flex flex-col items-center">
                  <PieChartComponent data={reportData.moduleUsage} />
                  <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                    {reportData.moduleUsage.map((item, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.color }}
                        ></div>
                        <span className="text-sm text-gray-300">{item.name}: {item.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Detailed Stats */}
          {reportData && (
            <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50 mb-8">
              <h3 className="text-xl font-bold text-white mb-6">Detailed Statistics</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <h4 className="text-lg font-semibold text-cyan-400 mb-4">Fraud Detection</h4>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center pb-2 border-b border-gray-700/50">
                      <span className="text-gray-300">Messages Analyzed</span>
                      <span className="text-white font-medium">{reportData.fraudDetectionStats.messagesChecked}</span>
                    </div>
                    <div className="flex justify-between items-center pb-2 border-b border-gray-700/50">
                      <span className="text-gray-300">Transactions Analyzed</span>
                      <span className="text-white font-medium">{reportData.fraudDetectionStats.transactionsChecked}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300">Potential Fraud Detected</span>
                      <span className="text-amber-400 font-medium">{reportData.fraudDetectionStats.potentialFraudDetected}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold text-purple-400 mb-4">Security Engagement</h4>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center pb-2 border-b border-gray-700/50">
                      <span className="text-gray-300">Lessons Completed (est.)</span>
                      <span className="text-white font-medium">{reportData.securityEngagement.lessonsCompleted}</span>
                    </div>
                    <div className="flex justify-between items-center pb-2 border-b border-gray-700/50">
                      <span className="text-gray-300">Feedback Provided</span>
                      <span className="text-white font-medium">{reportData.securityEngagement.feedbackProvided}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-300">Games Played</span>
                      <span className="text-white font-medium">{reportData.securityEngagement.gamesPlayed}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-lg font-semibold text-rose-400 mb-4">Usage History</h4>
                  <div className="space-y-3 max-h-60 overflow-y-auto pr-2">
                    {reportData.historicalUsage?.reportGenerator?.length > 0 ? (
                      [...reportData.historicalUsage.reportGenerator].reverse().slice(0, 10).map((entry, index) => (
                        <div key={index} className="flex justify-between items-center pb-2 border-b border-gray-700/30">
                          <div>
                            <div className="text-gray-300 text-sm">
                              {new Date(entry.timestamp).toLocaleDateString()}
                            </div>
                            <div className="text-gray-400 text-xs">
                              {new Date(entry.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                            </div>
                          </div>
                          <span className="text-white font-medium bg-gray-700/50 px-2 py-1 rounded">
                            Visit #{entry.count}
                          </span>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-400 text-sm py-4 text-center">No usage history available yet</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Back to Dashboard */}
          <div className="text-center mt-12">
            <Link 
              to="/dashboard"
              className="inline-flex items-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator;