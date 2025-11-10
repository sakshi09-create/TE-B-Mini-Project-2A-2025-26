import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { GridBeams } from '@/components/magicui/grid-beams';
import Navbar from '@/components/navbar';
import { Shield, AlertTriangle, CheckCircle, XCircle, RotateCcw, Trophy, Star, Zap, Phone, User, MessageCircle, Gamepad2, Volume2, VolumeX } from 'lucide-react';
import usageTracker from '@/lib/usageTracker';

const GameFeature = () => {
  // Track usage when game actually starts
  const incrementUsage = () => {
    usageTracker.incrementUsage('gameFeature');
  };

  // Game states
  const [gameState, setGameState] = useState('menu'); // menu, playing, results
  const [currentLevel, setCurrentLevel] = useState(1);
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [timeLeft, setTimeLeft] = useState(30);
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [gameMode, setGameMode] = useState('fraud'); // fraud, social, impersonation
  
  // Voice/Speech states
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const speechSynthesisRef = useRef(null);
  
  // Game questions
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);

  // Initialize game questions
  useEffect(() => {
    const fraudQuestions = [
      {
        id: 1,
        text: "You receive a message saying: 'Your bank account will be closed in 24 hours. Click here to verify your details immediately.' What should you do?",
        options: [
          { id: 'a', text: 'Click the link and enter your details to save your account', isFraud: true },
          { id: 'b', text: 'Call your bank directly using their official phone number', isFraud: false },
          { id: 'c', text: 'Reply to the message with your account number', isFraud: true },
          { id: 'd', text: 'Forward the message to friends for advice', isFraud: true }
        ],
        explanation: "Legitimate banks will never ask for sensitive information through messages. Always contact them directly through official channels.",
        correctAnswer: 'b'
      },
      {
        id: 2,
        text: "An email claims you've won a $5000 lottery you never entered. What's the best response?",
        options: [
          { id: 'a', text: 'Provide your bank details to claim the prize', isFraud: true },
          { id: 'b', text: 'Delete the email and report it as spam', isFraud: false },
          { id: 'c', text: 'Click the link to verify your win', isFraud: true },
          { id: 'd', text: 'Share it on social media for others to see', isFraud: true }
        ],
        explanation: "Lottery scams are common. You cannot win a lottery you never entered. Delete and report such messages.",
        correctAnswer: 'b'
      },
      {
        id: 3,
        text: "A text message says: 'Your OTP is required to complete your transaction. Reply with the code sent to your phone.' What should you do?",
        options: [
          { id: 'a', text: 'Reply with the OTP code immediately', isFraud: true },
          { id: 'b', text: 'Call your bank to verify if a transaction is pending', isFraud: false },
          { id: 'c', text: 'Forward the OTP to a friend for safekeeping', isFraud: true },
          { id: 'd', text: 'Ignore the message but check your bank app', isFraud: false }
        ],
        explanation: "Banks never ask for OTPs through messages. If unsure, verify through official channels but never share your OTP.",
        correctAnswer: 'b'
      },
      {
        id: 4,
        text: "You receive a call from someone claiming to be from tech support, saying your computer is infected. They ask for remote access. What's the safest action?",
        options: [
          { id: 'a', text: 'Allow them remote access to fix the issue', isFraud: true },
          { id: 'b', text: 'Hang up and contact tech support directly', isFraud: false },
          { id: 'c', text: 'Ask for their employee ID and call back', isFraud: true },
          { id: 'd', text: 'Let them guide you through fixing it yourself', isFraud: true }
        ],
        explanation: "Legitimate tech companies won't call unexpectedly. Always initiate contact with tech support yourself.",
        correctAnswer: 'b'
      }
    ];

    const socialEngineeringQuestions = [
      {
        id: 1,
        text: "A caller says they're from your bank and claims there's suspicious activity on your account. They ask for your full account number and PIN to verify your identity. What should you do?",
        options: [
          { id: 'a', text: 'Provide the information to verify your account', isFraud: true },
          { id: 'b', text: 'Ask them to call back on your registered number', isFraud: true },
          { id: 'c', text: 'Hang up and call your bank using their official number', isFraud: false },
          { id: 'd', text: 'Give only partial information to verify them', isFraud: true }
        ],
        explanation: "Legitimate banks will never ask for your full account number and PIN over the phone. Always verify by calling the bank's official number yourself.",
        correctAnswer: 'c'
      },
      {
        id: 2,
        text: "Someone approaches you at a coffee shop and says they work for the same company as you. They ask for your work email and password to 'sync some files'. What should you do?",
        options: [
          { id: 'a', text: 'Provide your work credentials to help them', isFraud: true },
          { id: 'b', text: 'Politely decline and report to security if needed', isFraud: false },
          { id: 'c', text: 'Give them a fake password to test their intentions', isFraud: true },
          { id: 'd', text: 'Ask for their employee ID first', isFraud: true }
        ],
        explanation: "Never share work credentials with anyone, even if they claim to be from your company. Legitimate colleagues would use proper channels.",
        correctAnswer: 'b'
      },
      {
        id: 3,
        text: "An IT support person emails you asking for your password to 'perform routine maintenance'. What's the safest response?",
        options: [
          { id: 'a', text: 'Send your password through a secure channel', isFraud: true },
          { id: 'b', text: 'Call the IT department directly to verify', isFraud: false },
          { id: 'c', text: 'Provide your password but change it later', isFraud: true },
          { id: 'd', text: 'Reply with security questions instead', isFraud: true }
        ],
        explanation: "IT departments will never ask for your password. Always verify through official channels before sharing any credentials.",
        correctAnswer: 'b'
      }
    ];

    const impersonationQuestions = [
      {
        id: 1,
        text: "Your boss contacts you via WhatsApp and urgently asks you to transfer money to a new vendor account. What should you do?",
        options: [
          { id: 'a', text: 'Transfer the money immediately as requested', isFraud: true },
          { id: 'b', text: 'Verify through a different communication channel', isFraud: false },
          { id: 'c', text: 'Ask for more details about the vendor', isFraud: true },
          { id: 'd', text: 'Transfer a small amount first to test', isFraud: true }
        ],
        explanation: "Scammers often impersonate authority figures. Always verify urgent financial requests through a different communication channel.",
        correctAnswer: 'b'
      },
      {
        id: 2,
        text: "A friend contacts you on social media saying they're stranded in another country and need money wired immediately. What's the best approach?",
        options: [
          { id: 'a', text: 'Send money immediately to help your friend', isFraud: true },
          { id: 'b', text: 'Call or video chat with your friend to verify', isFraud: false },
          { id: 'c', text: 'Ask for their bank details over the message', isFraud: true },
          { id: 'd', text: 'Send a smaller amount first', isFraud: true }
        ],
        explanation: "Scammers often hack accounts and impersonate friends. Always verify through another communication channel before sending money.",
        correctAnswer: 'b'
      },
      {
        id: 3,
        text: "A government official calls claiming you owe taxes and threatens arrest if you don't pay immediately with gift cards. What should you do?",
        options: [
          { id: 'a', text: 'Purchase gift cards and provide the codes', isFraud: true },
          { id: 'b', text: 'Hang up and contact the agency directly', isFraud: false },
          { id: 'c', text: 'Ask for a payment plan instead', isFraud: true },
          { id: 'd', text: 'Provide personal information for verification', isFraud: true }
        ],
        explanation: "Government agencies won't demand immediate payment via gift cards. Always verify by contacting the agency directly through official channels.",
        correctAnswer: 'b'
      }
    ];

    // Set questions based on game mode
    let gameQuestions = fraudQuestions;
    if (gameMode === 'social') {
      gameQuestions = socialEngineeringQuestions;
    } else if (gameMode === 'impersonation') {
      gameQuestions = impersonationQuestions;
    }

    setQuestions(gameQuestions);
  }, [gameMode]);

  // Text-to-speech functionality
  const speakText = (text) => {
    if (!voiceEnabled || !window.speechSynthesis) return;
    
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9; // Slightly slower for better comprehension
    utterance.pitch = 1;
    utterance.volume = 1;
    
    utterance.onstart = () => {
      setIsSpeaking(true);
    };
    
    utterance.onend = () => {
      setIsSpeaking(false);
    };
    
    utterance.onerror = () => {
      setIsSpeaking(false);
    };
    
    window.speechSynthesis.speak(utterance);
  };

  // Speak question when it changes
  useEffect(() => {
    if (gameState === 'playing' && questions[currentQuestion] && voiceEnabled) {
      // Small delay to ensure the question is rendered
      const timer = setTimeout(() => {
        speakText(questions[currentQuestion].text);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [currentQuestion, gameState, questions, voiceEnabled]);

  // Timer effect
  useEffect(() => {
    let timer;
    if (gameState === 'playing' && timeLeft > 0) {
      timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
    } else if (timeLeft === 0 && gameState === 'playing') {
      handleTimeUp();
    }
    return () => clearTimeout(timer);
  }, [timeLeft, gameState]);

  const startGame = (mode = 'fraud') => {
    setGameMode(mode);
    incrementUsage(); // Increment usage counter when game actually starts
    setGameState('playing');
    setCurrentLevel(1);
    setScore(0);
    setLives(3);
    setTimeLeft(30);
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setShowResult(false);
  };

  const handleAnswerSelect = (option) => {
    if (showResult) return;
    
    setSelectedAnswer(option);
    const isCorrect = option.id === questions[currentQuestion]?.correctAnswer;
    
    if (isCorrect) {
      setScore(score + 100);
      setFeedback('Correct! Well done.');
    } else {
      setLives(lives - 1);
      setFeedback('Incorrect. That was a fraud attempt.');
    }
    
    setShowFeedback(true);
    setShowResult(true);
    
    // Move to next question after delay
    setTimeout(() => {
      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
        setSelectedAnswer(null);
        setShowResult(false);
        setShowFeedback(false);
        setTimeLeft(30); // Reset timer for next question
      } else {
        setGameState('results');
      }
    }, 2000);
  };

  const handleTimeUp = () => {
    setLives(lives - 1);
    setFeedback('Time\'s up! That was a fraud attempt.');
    setShowFeedback(true);
    setShowResult(true);
    
    setTimeout(() => {
      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
        setSelectedAnswer(null);
        setShowResult(false);
        setShowFeedback(false);
        setTimeLeft(30);
      } else {
        setGameState('results');
      }
    }, 2000);
  };

  const resetGame = () => {
    setGameState('menu');
    setScore(0);
    setLives(3);
    setTimeLeft(30);
    setCurrentQuestion(0);
    setSelectedAnswer(null);
    setShowResult(false);
    setShowFeedback(false);
  };

  // Toggle voice functionality
  const toggleVoice = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
    setVoiceEnabled(!voiceEnabled);
  };

  // Render game menu
  if (gameState === 'menu') {
    return (
      <div className="min-h-screen relative" style={{ backgroundColor: '#020412' }}>
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

        <div className="relative z-10 px-4 lg:px-8 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600/20 to-indigo-600/20 rounded-full border border-purple-500/30 backdrop-blur-sm mb-8">
              <Zap className="w-5 h-5 text-purple-400 mr-2" />
              <span className="text-purple-300 text-sm font-medium">Interactive Learning</span>
            </div>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-white mb-6">
              Fraud Fighter
              <span className="block text-3xl sm:text-4xl text-purple-400 mt-2">Security Challenge</span>
            </h1>
            
            <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-12">
              Test your knowledge and learn to identify fraud attempts in this interactive game. 
              Each level presents real-world scenarios to help you protect yourself and your family.
            </p>
            
            {/* Voice Toggle */}
            <div className="flex justify-center mb-6">
              <button
                onClick={toggleVoice}
                className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all ${
                  voiceEnabled 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}
              >
                {voiceEnabled ? (
                  <>
                    <Volume2 className="w-5 h-5" />
                    <span>Voice Enabled</span>
                  </>
                ) : (
                  <>
                    <VolumeX className="w-5 h-5" />
                    <span>Voice Disabled</span>
                  </>
                )}
              </button>
            </div>
            
            {/* Game Mode Selection */}
            <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-8 border border-gray-700/50 max-w-3xl mx-auto mb-12">
              <h2 className="text-2xl font-bold text-white mb-6">Choose Your Challenge</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <button
                  onClick={() => startGame('fraud')}
                  className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl p-6 hover:from-purple-700 hover:to-indigo-700 transition-all transform hover:scale-105 shadow-lg"
                >
                  <Shield className="w-12 h-12 text-white mx-auto mb-4" />
                  <h3 className="font-semibold text-white mb-2">Fraud Detection</h3>
                  <p className="text-purple-200 text-sm">Classic fraud scenarios</p>
                </button>
                
                <button
                  onClick={() => startGame('social')}
                  className="bg-gradient-to-br from-blue-600 to-cyan-600 rounded-xl p-6 hover:from-blue-700 hover:to-cyan-700 transition-all transform hover:scale-105 shadow-lg"
                >
                  <User className="w-12 h-12 text-white mx-auto mb-4" />
                  <h3 className="font-semibold text-white mb-2">Social Engineering</h3>
                  <p className="text-blue-200 text-sm">Manipulation tactics</p>
                </button>
                
                <button
                  onClick={() => startGame('impersonation')}
                  className="bg-gradient-to-br from-pink-600 to-rose-600 rounded-xl p-6 hover:from-pink-700 hover:to-rose-700 transition-all transform hover:scale-105 shadow-lg"
                >
                  <Phone className="w-12 h-12 text-white mx-auto mb-4" />
                  <h3 className="font-semibold text-white mb-2">Impersonation</h3>
                  <p className="text-pink-200 text-sm">Identity deception</p>
                </button>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                to="/dashboard"
                className="px-8 py-4 bg-gray-800 text-gray-300 font-bold rounded-xl hover:bg-gray-700 transition-all flex items-center justify-center gap-2"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Render game results
  if (gameState === 'results') {
    return (
      <div className="min-h-screen relative" style={{ backgroundColor: '#020412' }}>
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

        <div className="relative z-10 px-4 lg:px-8 py-16">
          <div className="max-w-4xl mx-auto text-center">
            <Trophy className="w-24 h-24 text-yellow-400 mx-auto mb-6" />
            
            <h1 className="text-5xl font-bold text-white mb-4">Game Complete!</h1>
            
            <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-8 border border-gray-700/50 max-w-2xl mx-auto mb-8">
              <div className="grid grid-cols-3 gap-6">
                <div className="bg-gray-800/50 rounded-xl p-4">
                  <div className="text-3xl font-bold text-white">{score}</div>
                  <div className="text-gray-400 text-sm">Points</div>
                </div>
                <div className="bg-gray-800/50 rounded-xl p-4">
                  <div className="text-3xl font-bold text-white">{questions.length}</div>
                  <div className="text-gray-400 text-sm">Questions</div>
                </div>
                <div className="bg-gray-800/50 rounded-xl p-4">
                  <div className="text-3xl font-bold text-white">{lives}</div>
                  <div className="text-gray-400 text-sm">Lives Left</div>
                </div>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-purple-900/30 to-indigo-900/30 backdrop-blur-lg rounded-2xl p-6 border border-purple-500/30 max-w-2xl mx-auto mb-8">
              <h2 className="text-2xl font-bold text-white mb-4">Security Tips Learned</h2>
              <ul className="text-left text-gray-300 space-y-2">
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Never share OTPs or sensitive information through messages</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Verify unexpected requests through official channels</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Be skeptical of urgent or threatening messages</span>
                </li>
                <li className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-400 mr-2 mt-0.5 flex-shrink-0" />
                  <span>Legitimate organizations won't ask for sensitive info unexpectedly</span>
                </li>
              </ul>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={resetGame}
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-5 h-5" />
                Play Again
              </button>
              
              <Link 
                to="/dashboard"
                className="px-8 py-4 bg-gray-800 text-gray-300 font-bold rounded-xl hover:bg-gray-700 transition-all flex items-center justify-center gap-2"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Render game play
  const question = questions[currentQuestion];
  
  return (
    <div className="min-h-screen relative" style={{ backgroundColor: '#020412' }}>
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

      <div className="relative z-10 px-4 lg:px-8 py-8">
        {/* Animated floating elements */}
        <div className="absolute top-20 left-10 w-4 h-4 bg-purple-500 rounded-full animate-ping opacity-75"></div>
        <div className="absolute top-40 right-20 w-6 h-6 bg-cyan-400 rounded-full animate-bounce opacity-70"></div>
        <div className="absolute bottom-40 left-20 w-3 h-3 bg-pink-500 rounded-full animate-pulse opacity-80"></div>
        <div className="absolute bottom-20 right-10 w-5 h-5 bg-yellow-400 rounded-full animate-ping opacity-60"></div>

        {/* Game Header */}
        <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700/50 mb-8 animate-fade-in">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-400" />
                <span className="text-white font-bold">{score}</span>
                <span className="text-gray-400">Points</span>
              </div>
              
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-blue-400" />
                <span className="text-white font-bold">{lives}</span>
                <span className="text-gray-400">Lives</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2 bg-red-500/20 px-4 py-2 rounded-full animate-pulse">
              <span className="text-red-400 font-bold">{timeLeft}s</span>
              <span className="text-gray-400">Time Left</span>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Question</span>
                <span className="text-white font-bold">{currentQuestion + 1}</span>
                <span className="text-gray-400">of</span>
                <span className="text-white font-bold">{questions.length}</span>
              </div>
              
              {/* Voice Toggle Button */}
              <button
                onClick={toggleVoice}
                className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm transition-all ${
                  voiceEnabled 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}
              >
                {voiceEnabled ? (
                  <>
                    <Volume2 className="w-4 h-4" />
                    <span>On</span>
                  </>
                ) : (
                  <>
                    <VolumeX className="w-4 h-4" />
                    <span>Off</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-gray-900/50 backdrop-blur-lg rounded-2xl p-8 border border-gray-700/50 mb-8 animate-slide-up">
          <div className="flex items-start gap-4 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 animate-bounce">
              <span className="text-white font-bold text-xl">{currentQuestion + 1}</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                {gameMode === 'social' && 'Social Engineering Challenge'}
                {gameMode === 'impersonation' && 'Impersonation Detection'}
                {gameMode === 'fraud' && 'Fraud Detection Challenge'}
              </h2>
              <p className="text-gray-300 text-lg">{question?.text}</p>
              
              {/* Voice Status Indicator */}
              {voiceEnabled && (
                <div className="flex items-center gap-2 mt-3">
                  {isSpeaking ? (
                    <>
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-green-400 text-sm">Speaking...</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-400 text-sm">Voice enabled</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Options */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {question?.options.map((option, index) => (
              <button
                key={option.id}
                onClick={() => handleAnswerSelect(option)}
                disabled={showResult}
                className={`p-6 rounded-xl text-left transition-all transform hover:scale-105 hover:shadow-lg ${
                  showResult
                    ? option.id === question.correctAnswer
                      ? 'bg-green-500/20 border-2 border-green-500 animate-pulse'
                      : selectedAnswer?.id === option.id
                        ? 'bg-red-500/20 border-2 border-red-500 animate-shake'
                        : 'bg-gray-800/50 border border-gray-700'
                    : 'bg-gray-800/50 border border-gray-700 hover:bg-gray-700/50'
                } ${index % 4 === 0 ? 'animate-fade-in-up-1' : index % 4 === 1 ? 'animate-fade-in-up-2' : index % 4 === 2 ? 'animate-fade-in-up-3' : 'animate-fade-in-up-4'}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    showResult
                      ? option.id === question.correctAnswer
                        ? 'bg-green-500 animate-pulse'
                        : selectedAnswer?.id === option.id
                          ? 'bg-red-500 animate-shake'
                          : 'bg-gray-700'
                      : 'bg-gray-700'
                  }`}>
                    <span className="text-white font-bold">{option.id.toUpperCase()}</span>
                  </div>
                  <span className="text-white">{option.text}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Feedback */}
          {showFeedback && (
            <div className={`mt-6 p-4 rounded-xl animate-fade-in ${
              feedback.includes('Correct') 
                ? 'bg-green-500/20 border border-green-500/50' 
                : 'bg-red-500/20 border border-red-500/50'
            }`}>
              <div className="flex items-start gap-3">
                {feedback.includes('Correct') ? (
                  <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-0.5 animate-bounce" />
                ) : (
                  <XCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5 animate-shake" />
                )}
                <div>
                  <p className={`font-bold ${
                    feedback.includes('Correct') ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {feedback}
                  </p>
                  <p className="text-gray-300 mt-1">{question?.explanation}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Back to Dashboard */}
        <div className="text-center animate-fade-in">
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

export default GameFeature;