import { useState, useEffect, useRef } from 'react';
import { LogOut, Home, Users, Volume2, VolumeX, Cloud } from 'lucide-react';
import AiCard from './AiCard';
import { sendMessage } from '../services/api';
import voiceService from '../services/voiceService';

export default function AlwaysOnAssistant({ member, onLogout }) {
  const [assistantState, setAssistantState] = useState('idle');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [currentSubtitle, setCurrentSubtitle] = useState('');
  const [lastResponse, setLastResponse] = useState('');
  const [weather, setWeather] = useState(null);
  const [morningGreeted, setMorningGreeted] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [volume, setVolume] = useState(0);
  const [eyePos, setEyePos] = useState({ x: 0, y: 0 });
  const [userCoords, setUserCoords] = useState({ lat: null, lon: null });
  const isProcessingRef = useRef(false);
  const hasInitializedRef = useRef(false);

  // ─────────────────────────────────────────────────────────────
  // ✅ STEP 1: Set Gemini key IMMEDIATELY on mount (no deps = runs
  //    first, before weather fetch or init effect). This guarantees
  //    the Kore (female) voice is ready before the greeting fires.
  // ─────────────────────────────────────────────────────────────
  useEffect(() => {
    const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
    if (apiKey) {
      voiceService.setGeminiApiKey(apiKey);
      console.log('✅ [AlwaysOnAssistant] Gemini key injected → Kore female voice active');
    } else {
      console.warn('⚠️ [AlwaysOnAssistant] VITE_GEMINI_API_KEY missing in .env — browser TTS fallback will be used');
    }
  }, []); // ← empty deps: runs once, synchronously before all other effects

  // ─────────────────────────────────────────────────────────────
  // ✅ STEP 2: Fetch weather using device location
  // ─────────────────────────────────────────────────────────────
  useEffect(() => {
    const fetchWeatherWithLocation = async () => {
      if (!navigator.geolocation) {
        console.warn('Geolocation not supported');
        return;
      }

      navigator.geolocation.getCurrentPosition(
        async (position) => {
          try {
            const { latitude, longitude } = position.coords;

            console.log(`Your coords: ${latitude}, ${longitude}`); // ← debug line

            const response = await fetch(
              // Use backtick template literal carefully — make sure lat/lon are numbers
              `http://localhost:8000/weather?lat=${latitude}&lon=${longitude}`
            );

            if (!response.ok) {
              throw new Error(`HTTP error: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
              setWeather(data.weather);
              setUserCoords({ lat: latitude, lon: longitude }); // ← add this line
            } else {
              console.error('API returned failure:', data); // ← see what backend says
            }
          } catch (error) {
            console.error('Weather fetch failed:', error);
          }
        },
        (error) => {
          console.error('Location permission denied:', error);
        },
        { enableHighAccuracy: true, timeout: 10000 } // ← add geolocation options
      );
    };

    fetchWeatherWithLocation();
  }, []);
  // ─────────────────────────────────────────────────────────────
  // ✅ STEP 3: Morning greeting builder
  // ─────────────────────────────────────────────────────────────
  const morningGreeting = () => {
    if (morningGreeted) return;

    const hour = new Date().getHours();
    let timeGreeting = '';
    if (hour < 12) timeGreeting = 'morning';
    else if (hour < 17) timeGreeting = 'afternoon';
    else timeGreeting = 'evening';

    let greeting = `Good ${timeGreeting}, ${member.name}! `;

    if (hour < 12 && weather) {
      // Avoid "°C" symbol — preprocessor handles numbers, but degree symbol
      // can confuse TTS. Write it out plainly.
      greeting += `It is ${weather.temperature} degrees Celsius with ${weather.description} in ${weather.city}. `;
      greeting += `Would you like me to tell you today's news? `;
    } else {
      greeting += `How are you doing today? `;
    }

    greeting += `So, what are you up to?`;

    setMorningGreeted(true);
    isProcessingRef.current = true;
    handleAssistantResponse(greeting, 'happy');

    setTimeout(() => {
      isProcessingRef.current = false;
    }, 4000);
  };

  // ─────────────────────────────────────────────────────────────
  // ✅ STEP 4: Initialize assistant
  //    Greeting delayed to 2000ms — safely after Gemini key effect
  // ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (hasInitializedRef.current) return;
    hasInitializedRef.current = true;

    console.log('🌟 A.M.I. Activated for:', member.name);

    if (!voiceService.isSpeechAvailable()) {
      console.warn('Speech synthesis not available');
      setAudioEnabled(false);
    }

    // ✅ 2000ms gives the Gemini key effect (declared first) plenty of
    //    time to run, so Kore voice is definitely set before first speak()
    setTimeout(() => {
      morningGreeting();
    }, 2000);

    startListening();

    // Eye wander effect
    const wander = () => {
      setTimeout(() => {
        setEyePos({
          x: (Math.random() - 0.5) * 12,
          y: (Math.random() - 0.5) * 7,
        });
        wander();
      }, 900 + Math.random() * 2400);
    };
    wander();

    return () => {
      voiceService.stopListening();
      voiceService.stopSpeaking();
    };
  }, [weather]);

  // ─────────────────────────────────────────────────────────────
  // Listening
  // ─────────────────────────────────────────────────────────────
  const startListening = () => {
    if (isProcessingRef.current) return;
    const started = voiceService.startContinuousListening(handleUserSpeech);
    setIsListening(started);
    if (started) setAssistantState('idle');
  };

  const handleUserSpeech = async (text) => {
    if (isProcessingRef.current) return;
    if (!text || text.trim() === '') return;

    try {
      isProcessingRef.current = true;
      setIsListening(false);
      setAssistantState('thinking');
      setTranscript(`You said: "${text}"`);
      setCurrentSubtitle(`You said: "${text}"`);

      const lowerText = text.toLowerCase();

      if (lowerText.includes('news')) { handleNewsRequest(); return; }
      if (lowerText.includes('first') || lowerText.includes('1st')) { fetchNewsDetail(0); return; }
      if (lowerText.includes('second') || lowerText.includes('2nd')) { fetchNewsDetail(1); return; }
      if (lowerText.includes('third') || lowerText.includes('3rd')) { fetchNewsDetail(2); return; }

      console.log(`💬 Sending to backend: "${text}"`);
      const response = await sendMessage(member.id, text, audioEnabled, userCoords.lat, userCoords.lon);
      if (response.duplicate) {
        console.log('⏭️ Duplicate message ignored');
        isProcessingRef.current = false;
        startListening();
        return;
      }

      if (response?.response) {
        console.log(`✅ Got response: "${response.response.substring(0, 50)}..."`);
        setTranscript('');
        handleAssistantResponse(response.response, response.emotion || 'neutral');
      } else {
        throw new Error('Invalid response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      handleAssistantResponse("Sorry, I am having trouble connecting.", 'concerned');
    }
  };

  // ─────────────────────────────────────────────────────────────
  // News
  // ─────────────────────────────────────────────────────────────
  const handleNewsRequest = async () => {
    try {
      handleAssistantResponse("Fetching today's top headlines.", 'happy');

      const response = await fetch('http://localhost:8000/news');
      const data = await response.json();

      if (data.success && data.articles) {
        const numberWords = ['one', 'two', 'three', 'four', 'five'];
        let newsText = "Here are today's top headlines. ";
        data.articles.slice(0, 3).forEach((article, index) => {
          newsText += `Number ${numberWords[index]}. ${article.title}. `;
        });
        newsText += 'Would you like more details on any of these?';
        handleAssistantResponse(newsText, 'neutral');
      } else {
        handleAssistantResponse('I could not fetch the news right now.', 'concerned');
      }
    } catch (error) {
      handleAssistantResponse('I could not fetch the news right now.', 'concerned');
    }
  };

  const fetchNewsDetail = async (index) => {
    try {
      const response = await fetch(`http://localhost:8000/news-detail/${index}`);
      const data = await response.json();

      if (data.success) {
        handleAssistantResponse(`${data.title}. ${data.description || ''}`, 'neutral');
      } else {
        handleAssistantResponse('I could not find that article.', 'concerned');
      }
    } catch (error) {
      handleAssistantResponse('Something went wrong while fetching details.', 'concerned');
    }
  };

  // ─────────────────────────────────────────────────────────────
  // Response & speech
  // ─────────────────────────────────────────────────────────────
  const handleAssistantResponse = (text, emotion) => {
    setLastResponse(text);
    setCurrentSubtitle(text);
    setAssistantState('speaking');

    if (audioEnabled) {
      speakResponse(text);
    } else {
      setTimeout(() => {
        setAssistantState('idle');
        isProcessingRef.current = false;
        startListening();
      }, 3000);
    }
  };

  const speakResponse = (text) => {
    if (!audioEnabled) return;

    setIsSpeaking(true);
    setAssistantState('speaking');
    setIsListening(false);

    voiceService.speak(text, () => {
      setIsSpeaking(false);
      setAssistantState('idle');
      setTranscript('');

      setTimeout(() => {
        isProcessingRef.current = false;
        if (!isProcessingRef.current) startListening();
      }, 1500);
    });
  };

  const toggleAudio = () => {
    const newState = !audioEnabled;
    setAudioEnabled(newState);

    if (newState) {
      handleAssistantResponse('Audio is back on!', 'happy');
    } else {
      voiceService.stopSpeaking();
      setIsSpeaking(false);
      setAssistantState('idle');
      isProcessingRef.current = false;
      startListening();
    }
  };

  const getStatusMessage = () => {
    if (isSpeaking) return 'A.M.I. is talking...';
    if (isListening) return 'Listening...';
    if (assistantState === 'thinking') return 'Thinking...';
    return 'Ready';
  };

  // ─────────────────────────────────────────────────────────────
  // UI
  // ─────────────────────────────────────────────────────────────
  return (
    <div className="fixed inset-0" style={{ backgroundColor: '#f8f9fa' }}>
      <div
        className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center"
        style={{
          background: 'rgba(74, 134, 207, 0.1)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(74, 134, 207, 0.2)',
          zIndex: 50,
        }}
      >
        <div className="flex items-center gap-4">
          <button
            onClick={() => (window.location.href = '/')}
            className="flex items-center gap-2 px-4 py-2 rounded-full"
            style={{ background: '#4A86CF', color: '#FFFFFF' }}
          >
            <Home size={20} />
            <span>Home</span>
          </button>

          <div className="flex items-center gap-2" style={{ color: '#4A86CF' }}>
            <Users size={20} />
            <span>{member.family_name} Family</span>
          </div>

          <div style={{ color: '#333333' }}>👋 {member.name}</div>

          {weather && (
            <div className="flex items-center gap-2" style={{ color: '#82ACE0' }}>
              <Cloud size={16} />
              <span>{weather.temperature}°C</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div
            className="px-3 py-1 rounded-full text-sm"
            style={{ background: '#FFFFFF', color: '#4A86CF' }}
          >
            {getStatusMessage()}
          </div>

          <button
            onClick={toggleAudio}
            className="p-2 rounded-full"
            style={{
              background: audioEnabled ? '#4A86CF' : '#D6E2F0',
              color: '#FFFFFF',
            }}
          >
            {audioEnabled ? <Volume2 /> : <VolumeX />}
          </button>

          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-full"
            style={{ background: '#82ACE0', color: '#FFFFFF' }}
          >
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </div>

      <div className="absolute inset-0 flex flex-col items-center justify-center pt-16">
        <AiCard
          mode={assistantState}
          isSpeaking={isSpeaking}
          isListening={isListening}
          transcript={transcript}
          response={lastResponse}
          volume={volume}
          eyePos={eyePos}
        />
      </div>
    </div>
  );
}