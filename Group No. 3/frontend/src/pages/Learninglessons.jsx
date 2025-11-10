import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '@/components/navbar';
import { GridBeams } from '@/components/magicui/grid-beams';
import { 
  Play, 
  Pause, 
  X, 
  CheckCircle, 
  Star, 
  Bookmark, 
  BookmarkPlus,
  Trash2,
  PlayCircle,
  Clock,
  GraduationCap,
  Target,
  Loader2
} from 'lucide-react';
import usageTracker from '@/lib/usageTracker';

const LessonsPage = () => {
  const [bookmarks, setBookmarks] = useState([]);
  const [readTips, setReadTips] = useState(new Set());
  const [modalTipId, setModalTipId] = useState(null);
  const [videoCompleted, setVideoCompleted] = useState(new Set());
  const [currentProgress, setCurrentProgress] = useState({});

  // Track usage when lesson is actually viewed
  const incrementUsage = () => {
    usageTracker.incrementUsage('securityLessons');
  };

  const toggleDetails = (tipId) => {
    if (modalTipId === tipId) {
      setModalTipId(null);
    } else {
      // Increment usage counter when user actually opens a lesson
      incrementUsage();
      setModalTipId(tipId);
      setReadTips(prev => new Set([...prev, tipId]));
    }
  };

  const toggleBookmark = (tipId, title) => {
    if (bookmarks.some(b => b.id === tipId)) {
      setBookmarks(prev => prev.filter(b => b.id !== tipId));
    } else {
      setBookmarks(prev => [...prev, { id: tipId, title }]);
    }
  };

  const removeBookmark = (tipId) => {
    setBookmarks(prev => prev.filter(b => b.id !== tipId));
  };

  const markAsCompleted = (tipId) => {
    setVideoCompleted(prev => new Set([...prev, tipId]));
    setCurrentProgress(prev => ({ ...prev, [tipId]: 100 }));
    // Increment usage counter when user completes a lesson
    incrementUsage();
  };

  const isBookmarked = (tipId) => bookmarks.some(b => b.id === tipId);
  const isExpanded = (tipId) => modalTipId === tipId;
  const isCompleted = (tipId) => videoCompleted.has(tipId);

  // Simplified Video Player Component
  const SimpleVideoPlayer = React.memo(({ videoSrc, tipId }) => {
    const videoRef = useRef(null);
    const [hasError, setHasError] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    
    const handleError = useCallback((e) => {
      setHasError(true);
      setIsLoading(false);
      console.error('Video failed to load:', videoSrc, e.target?.error);
    }, [videoSrc]);

    const handleLoadStart = useCallback(() => {
      setIsLoading(true);
      setHasError(false);
    }, []);

    const handleCanPlay = useCallback(() => {
      setIsLoading(false);
    }, []);

    // Reset states when video changes
    useEffect(() => {
      setHasError(false);
      setIsLoading(true);
    }, [videoSrc]);

    // Force play when component mounts (for autoplay)
    useEffect(() => {
      if (videoRef.current) {
        const playPromise = videoRef.current.play();
        if (playPromise !== undefined) {
          playPromise.catch(error => {
            console.log("Auto-play was prevented:", error);
          });
        }
      }
    }, [videoSrc]);

    // Retry function
    const retryVideo = useCallback(() => {
      setHasError(false);
      setIsLoading(true);
      if (videoRef.current) {
        videoRef.current.load();
      }
    }, []);

    if (hasError) {
      return (
        <div className="w-full h-80 bg-slate-800 rounded-xl flex flex-col items-center justify-center text-white">
          <div className="text-4xl mb-4">⚠</div>
          <h3 className="text-lg font-semibold mb-2">Video Unavailable</h3>
          <p className="text-sm text-slate-400 text-center max-w-md mb-4">
            The video could not be loaded. Please check your internet connection or try again.
          </p>
          <button
            onClick={retryVideo}
            className="px-6 py-3 bg-blue-600 rounded-lg text-sm hover:bg-blue-700 transition-colors flex items-center gap-2 font-medium"
          >
            <Play size={16} />
            Retry Loading
          </button>
        </div>
      );
    }

    return (
      <div className="relative bg-black rounded-xl overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 bg-black/80 flex items-center justify-center z-20 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="animate-spin h-8 w-8 text-white" />
              <p className="text-white text-sm">Loading video...</p>
            </div>
          </div>
        )}
        
        <video
          ref={videoRef}
          src={videoSrc}
          className="w-full h-auto max-h-96 object-contain rounded-xl"
          controls
          onError={handleError}
          onLoadStart={handleLoadStart}
          onCanPlay={handleCanPlay}
          preload="metadata"
          playsInline
          muted={false}
          style={{
            backgroundColor: '#000',
            display: 'block'
          }}
        >
          <source src={videoSrc} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      </div>
    );
  });

  // Memoized Learning Card Component 
  const LearningCard = React.memo(({ 
    title, 
    subtitle, 
    preview, 
    category, 
    difficulty, 
    duration, 
    icon, 
    tipId, 
    gradientColors,
    imageSrc,
    className = "" 
  }) => {
    return (
      <div 
        className={`group relative h-96 rounded-2xl overflow-hidden shadow-2xl transition-all duration-500 hover:scale-[1.02] border border-slate-600/30 ${className}`}
      >
        <div className="absolute inset-0">
          <div 
            className="w-full h-full bg-cover bg-center bg-no-repeat"
            style={{
              backgroundImage: imageSrc ? `url(${imageSrc})` : `linear-gradient(135deg, ${gradientColors.from} 0%, ${gradientColors.to} 100%)`
            }}
          />
        </div>

        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />

        <div className="absolute inset-0 p-6 flex flex-col justify-between z-10">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 bg-gradient-to-r ${gradientColors.badge} text-white text-xs font-bold rounded-full shadow-lg backdrop-blur-sm`}>
                {category}
              </span>
              {isCompleted(tipId) && (
                <span className="px-3 py-1 bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs font-bold rounded-full shadow-lg backdrop-blur-sm flex items-center gap-1">
                  <CheckCircle size={12} />
                  Completed
                </span>
              )}
            </div>
            
            <div className="flex items-center gap-1 bg-black/30 backdrop-blur-sm rounded-full px-3 py-1">
              <div className={`w-2 h-2 ${gradientColors.difficulty.active} rounded-full`}></div>
              <div className={`w-2 h-2 ${gradientColors.difficulty.active} rounded-full ${difficulty === 'Beginner' ? 'opacity-50' : ''}`}></div>
              <div className={`w-2 h-2 ${difficulty === 'Advanced' ? gradientColors.difficulty.active : 'bg-slate-600'} rounded-full`}></div>
              <span className={`ml-2 text-xs ${gradientColors.difficulty.text} font-medium`}>{difficulty}</span>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <div className={`w-14 h-14 bg-gradient-to-br ${gradientColors.icon} rounded-xl flex items-center justify-center text-2xl shadow-lg flex-shrink-0`}>
                {icon}
              </div>
              <div className="flex-1 min-w-0">
                <span className={`text-sm font-medium block ${gradientColors.subtitle}`}>{subtitle}</span>
                <h3 className="text-white text-xl font-bold leading-tight mb-2">{title}</h3>
                <p className="text-slate-200 text-sm leading-relaxed line-clamp-2">
                  {preview}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 text-sm text-slate-300">
              <span className="flex items-center gap-1 bg-black/30 backdrop-blur-sm px-2 py-1 rounded-full">
                <Clock size={12} />
                {duration}
              </span>
              <span className="flex items-center gap-1 bg-black/30 backdrop-blur-sm px-2 py-1 rounded-full">
                <GraduationCap size={12} />
                Learn & Practice
              </span>
              {currentProgress[tipId] > 0 && (
                <span className="flex items-center gap-1 bg-black/30 backdrop-blur-sm px-2 py-1 rounded-full">
                  <PlayCircle size={12} />
                  {Math.round(currentProgress[tipId] || 0)}%
                </span>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={() => toggleDetails(tipId)}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r ${gradientColors.button} text-white rounded-xl font-semibold hover:shadow-lg transition-all duration-300 transform hover:translate-y-[-1px] backdrop-blur-sm`}
              >
                <GraduationCap size={16} />
                {isExpanded(tipId) ? 'Close Lesson' : 'Start Learning'}
              </button>
              <button
                onClick={() => toggleBookmark(tipId, title)}
                className={`px-4 py-3 rounded-xl font-semibold transition-all duration-300 shadow-lg transform hover:translate-y-[-1px] backdrop-blur-sm ${
                  isBookmarked(tipId)
                    ? 'bg-gradient-to-r from-amber-500 to-orange-600 text-white shadow-amber-500/25'
                    : 'bg-black/30 border border-white/20 text-slate-300 hover:bg-black/40'
                }`}
              >
                {isBookmarked(tipId) ? <Star size={16} fill="currentColor" /> : <BookmarkPlus size={16} />}
              </button>
            </div>
          </div>
        </div>

        {currentProgress[tipId] > 0 && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/30">
            <div 
              className={`h-1 bg-gradient-to-r ${gradientColors.progress} transition-all duration-300`}
              style={{ width: `${currentProgress[tipId] || 0}%` }}
            />
          </div>
        )}

        <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${gradientColors.glow} opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`}></div>
      </div>
    );
  });

  // Learning Content Data with Cloudinary Video URLs
  const learningContent = {
    'fake-news': {
      title: 'Spot Fake News Like a Pro',
      subtitle: 'Critical Thinking Skills',
      videoSrc: 'https://res.cloudinary.com/dbl1ihpn0/video/upload/v1759565391/Video1_dpchnh.mp4',
      sections: [
        {
          title: 'Key Warning Signs',
          content: [
            'Check the source - Is it from a reputable news organization?',
            'Look for emotional language designed to provoke strong reactions',
            'Verify with multiple sources before sharing',
            'Check the date - Old news can be recycled as current',
            'Be skeptical of sensational headlines',
            'Look for author credentials and contact information'
          ]
        },
        {
          title: 'Teaching Your Children',
          content: [
            'Always ask "Who wrote this and why?"',
            'Use fact-checking websites like Snopes or PolitiFact',
            'Encourage them to pause before sharing',
            'Discuss current events together regularly'
          ]
        }
      ],
      practiceExercises: [
        'Identify 3 warning signs in a suspicious headline',
        'Practice fact-checking with your family',
        'Create a family media literacy checklist'
      ]
    },
    'whatsapp': {
      title: 'Avoiding Over-Sharing on WhatsApp',
      subtitle: 'Digital Safety',
      videoSrc: 'https://res.cloudinary.com/dbl1ihpn0/video/upload/v1759565382/Video2_ydi84d.mp4',
      sections: [
        {
          title: 'Privacy Settings to Check',
          content: [
            'Set "Last Seen" to "My Contacts" or "Nobody"',
            'Limit who can see your profile photo and status',
            'Turn off read receipts for privacy',
            'Review group privacy settings regularly',
            'Enable two-step verification',
            'Turn off location sharing by default'
          ]
        },
        {
          title: 'What NOT to Share',
          content: [
            'Home addresses, school names, or work locations',
            'Travel plans or when you\'re away from home',
            'Financial information or personal documents',
            'Photos with identifiable background details',
            'Children\'s full names, ages, or schedules'
          ]
        }
      ],
      practiceExercises: [
        'Review and update your WhatsApp privacy settings',
        'Teach family members about safe sharing practices',
        'Create a family digital safety agreement'
      ]
    },
    'screen-time': {
      title: 'Healthy Screen Time Habits',
      subtitle: 'Healthy Habits',
      videoSrc: 'https://res.cloudinary.com/dbl1ihpn0/video/upload/v1759565392/Video3_yvvieu.mp4',
      sections: [
        {
          title: 'Age-Appropriate Guidelines',
          content: [
            'Ages 2-5: Maximum 1 hour of high-quality content daily',
            'Ages 6+: Consistent limits that don\'t interfere with sleep/activities',
            'No screens during meals or before bedtime',
            'Create screen-free zones in bedrooms',
            'Encourage breaks every 30-60 minutes'
          ]
        },
        {
          title: 'Healthy Habits to Build',
          content: [
            'Model good screen behavior yourself',
            'Create a family media plan together',
            'Prioritize outdoor activities and face-to-face interaction',
            'Use parental controls and screen time apps',
            'Make bedrooms screen-free spaces',
            'Plan engaging offline activities'
          ]
        }
      ],
      practiceExercises: [
        'Create a family screen time schedule',
        'Set up screen-free family time',
        'Design alternative activities for kids'
      ]
    }
  };

  // Individual Tip Card Components
  const FakeNewsTipCard = () => (
    <LearningCard
      title="Spot Fake News Like a Pro"
      subtitle="Critical Thinking Skills"
      preview="Master the art of identifying misinformation and teach your children to navigate today's complex information landscape with confidence."
      category="Media Literacy"
      difficulty="Beginner"
      duration="10 min video"
      icon="🕵‍♂"
      tipId="fake-news"
      imageSrc="https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop"
      gradientColors={{
        from: '#7c3aed',
        to: '#3b82f6',
        badge: 'from-emerald-500 to-teal-600',
        icon: 'from-purple-600 to-indigo-700',
        button: 'from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700',
        subtitle: 'text-purple-300',
        progress: 'from-purple-500 to-indigo-600',
        difficulty: { active: 'bg-emerald-400', text: 'text-emerald-400' },
        glow: 'from-purple-600/10 to-indigo-600/10'
      }}
      className="hover:shadow-purple-500/20"
    />
  );

  const WhatsAppTipCard = () => (
    <LearningCard
      title="Avoiding Over-Sharing on WhatsApp"
      subtitle="Digital Safety"
      preview="Protect your family's privacy with advanced WhatsApp security features and learn what information should never be shared online."
      category="Privacy & Security"
      difficulty="Intermediate"
      duration="15 min video"
      icon="🛡"
      tipId="whatsapp"
      imageSrc="https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=1000&auto=format&fit=crop"
      gradientColors={{
        from: '#0891b2',
        to: '#1d4ed8',
        badge: 'from-cyan-500 to-blue-600',
        icon: 'from-cyan-600 to-blue-700',
        button: 'from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700',
        subtitle: 'text-cyan-300',
        progress: 'from-cyan-500 to-blue-600',
        difficulty: { active: 'bg-cyan-400', text: 'text-cyan-400' },
        glow: 'from-cyan-600/10 to-blue-600/10'
      }}
      className="hover:shadow-cyan-500/20"
    />
  );

  const ScreenTimeTipCard = () => (
    <LearningCard
      title="Healthy Screen Time Habits"
      subtitle="Healthy Habits"
      preview="Create sustainable screen time routines that promote healthy development while embracing technology's benefits for learning and connection."
      category="Wellness & Balance"
      difficulty="Beginner"
      duration="12 min video"
      icon="⚖"
      tipId="screen-time"
      imageSrc="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=1000&auto=format&fit=crop"
      gradientColors={{
        from: '#059669',
        to: '#16a34a',
        badge: 'from-emerald-500 to-green-600',
        icon: 'from-emerald-600 to-green-700',
        button: 'from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700',
        subtitle: 'text-emerald-300',
        progress: 'from-emerald-500 to-green-600',
        difficulty: { active: 'bg-emerald-400', text: 'text-emerald-400' },
        glow: 'from-emerald-600/10 to-green-600/10'
      }}
      className="hover:shadow-emerald-500/20"
    />
  );

  const selectedContent = learningContent[modalTipId];

  return (
    <div className="min-h-screen bg-[#05081A] relative overflow-x-hidden">
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
      
      <div className="relative z-10">
        <Navbar />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20 relative z-10">
        <div className="mt-20 mb-12">
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600/20 to-indigo-600/20 rounded-full border border-purple-500/30 backdrop-blur-sm mb-6">
              <span className="text-purple-300 text-sm font-medium flex items-center gap-2">
                <GraduationCap size={16} />
                Premium Digital Safety Course
              </span>
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent mb-6 leading-tight">
              Master Digital <br />
              <span className="bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">Parenting</span>
            </h1>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
              Interactive video lessons with practical exercises to guide your family through today's digital landscape
            </p>
          </div>

          <div className="grid grid-cols-4 gap-4 max-w-3xl mx-auto">
            <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl p-4 text-center border border-slate-700/50 hover:bg-slate-800/60 transition-all duration-300">
              <span className="block text-2xl font-bold text-white mb-1">3</span>
              <span className="text-xs text-purple-300 flex items-center justify-center gap-1">
                <PlayCircle size={12} />
                Video Lessons
              </span>
            </div>
            <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl p-4 text-center border border-slate-700/50 hover:bg-slate-800/60 transition-all duration-300">
              <span className="block text-2xl font-bold text-white mb-1">{bookmarks.length}</span>
              <span className="text-xs text-amber-300 flex items-center justify-center gap-1">
                <BookmarkPlus size={12} />
                Bookmarked
              </span>
            </div>
            <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl p-4 text-center border border-slate-700/50 hover:bg-slate-800/60 transition-all duration-300">
              <span className="block text-2xl font-bold text-white mb-1">{readTips.size}</span>
              <span className="text-xs text-emerald-300 flex items-center justify-center gap-1">
                <Play size={12} />
                Started
              </span>
            </div>
            <div className="bg-slate-800/40 backdrop-blur-xl rounded-2xl p-4 text-center border border-slate-700/50 hover:bg-slate-800/60 transition-all duration-300">
              <span className="block text-2xl font-bold text-white mb-1">{videoCompleted.size}</span>
              <span className="text-xs text-green-300 flex items-center justify-center gap-1">
                <CheckCircle size={12} />
                Completed
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8 mb-16">
          <FakeNewsTipCard />
          <WhatsAppTipCard />
          <ScreenTimeTipCard />
        </div>

        {bookmarks.length > 0 && (
          <div className="mt-16 pt-8 border-t border-slate-700/50">
            <div className="flex items-center gap-4 mb-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl flex items-center justify-center">
                  <Bookmark size={20} className="text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white">Your Learning Path</h2>
              </div>
              <span className="bg-gradient-to-r from-amber-500 to-orange-600 text-white px-4 py-2 rounded-xl text-sm font-bold shadow-lg">
                {bookmarks.length} Saved
              </span>
            </div>
            
            <div className="grid gap-4">
              {bookmarks.map((bookmark) => (
                <div
                  key={bookmark.id}
                  className="bg-slate-800/40 backdrop-blur-xl p-6 rounded-2xl border border-slate-700/50 hover:bg-slate-800/60 transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="text-white font-semibold mb-2">{bookmark.title}</h4>
                      <p className="text-slate-400 text-sm">Ready to continue your learning journey</p>
                    </div>
                    <button
                      onClick={() => removeBookmark(bookmark.id)}
                      className="ml-4 px-4 py-2 bg-red-600/20 border border-red-500/30 text-red-400 rounded-xl text-sm font-medium hover:bg-red-600/30 transition-colors flex items-center gap-2"
                    >
                      <Trash2 size={14} />
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Simplified Modal with just video and guidelines */}
        {modalTipId && selectedContent && (
          <div 
            className="fixed inset-0 flex items-center justify-center z-50 bg-black/60 backdrop-blur-md p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                toggleDetails(modalTipId);
              }
            }}
          >
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto border border-slate-600/50 backdrop-blur-xl">
              {/* Header with title and close button only */}
              <div className="sticky top-0 bg-gradient-to-r from-slate-900 to-slate-800 p-6 border-b border-slate-700/50 backdrop-blur-xl z-10">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-2xl font-bold text-white">{selectedContent.title}</h3>
                    <p className="text-slate-400 mt-1">{selectedContent.subtitle}</p>
                  </div>
                  <button
                    onClick={() => toggleDetails(modalTipId)}
                    className="w-10 h-10 bg-slate-700/50 rounded-xl flex items-center justify-center text-slate-300 hover:text-white hover:bg-slate-600/50 transition-colors"
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>
              
              {/* Simple video player section */}
              <div className="p-6 border-b border-slate-700/50">
                <SimpleVideoPlayer 
                  videoSrc={selectedContent.videoSrc}
                  tipId={modalTipId}
                />
              </div>

              {/* Guidelines sections */}
              <div className="p-6 space-y-8">
                {selectedContent.sections.map((section, index) => (
                  <div key={index}>
                    <h4 className="font-semibold text-white mb-4 text-lg">{section.title}</h4>
                    <div className="grid gap-3">
                      {section.content.map((item, itemIndex) => (
                        <div key={itemIndex} className="flex items-start text-slate-300 bg-slate-800/30 p-4 rounded-xl border border-slate-700/30">
                          <span className="text-emerald-400 font-bold mr-3 mt-0.5">
                            <CheckCircle size={16} />
                          </span>
                          <span className="text-sm leading-relaxed">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                <div>
                  <h4 className="font-semibold text-white mb-4 text-lg flex items-center gap-2">
                    <Target size={20} />
                    Practice Exercises
                  </h4>
                  <div className="grid gap-3">
                    {selectedContent.practiceExercises.map((exercise, index) => (
                      <div key={index} className="flex items-start text-slate-300 bg-gradient-to-r from-purple-900/20 to-indigo-900/20 p-4 rounded-xl border border-purple-500/30">
                        <span className="text-purple-400 font-bold mr-3 mt-0.5 flex items-center justify-center w-6 h-6 bg-purple-600/20 rounded-full text-xs">
                          {index + 1}
                        </span>
                        <span className="text-sm leading-relaxed">{exercise}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
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
      </div>
    </div>
  );
};

export default LessonsPage;