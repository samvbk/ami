import { useEffect, useRef, useState } from 'react';

export default function VideoCharacter({ 
  state = 'idle', 
  isSpeaking = false, 
  isListening = false,
  isThinking = false 
}) {
  const videoRef = useRef(null);
  const [currentVideo, setCurrentVideo] = useState('amy_idle.mp4');
  const [hasInteracted, setHasInteracted] = useState(false);

  // Determine which video to play
  useEffect(() => {
    let newVideo = 'amy_idle.mp4';
    
    if (isListening) {
      newVideo = 'amy_listening.mp4';
    } else if (isThinking) {
      newVideo = 'amy_thinking.mp4';
    } else if (isSpeaking) {
      newVideo = 'amy_speaking.mp4';
    } else if (state && state !== 'idle') {
      newVideo = `amy_${state}.mp4`;
    }
    
    setCurrentVideo(newVideo);
  }, [state, isSpeaking, isListening, isThinking]);

  // Handle video playback
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const playVideo = () => {
      if (!hasInteracted) {
        // Wait for user interaction
        const handleFirstClick = () => {
          setHasInteracted(true);
          video.play().catch(e => {
            console.log('Video play after interaction:', e.name);
          });
          document.removeEventListener('click', handleFirstClick);
        };
        
        document.addEventListener('click', handleFirstClick);
        return;
      }
      
      video.play().catch(e => {
        console.log('Video play error:', e.name);
      });
    };

    playVideo();

    // Handle video end
    const handleEnded = () => {
      if (currentVideo === 'amy_idle.mp4' && hasInteracted) {
        video.currentTime = 0;
        video.play().catch(() => {});
      }
    };

    video.addEventListener('ended', handleEnded);
    
    return () => {
      video.removeEventListener('ended', handleEnded);
    };
  }, [currentVideo, hasInteracted]);

  return (
    <div className="relative w-full max-w-lg mx-auto">
      <div className="relative rounded-3xl overflow-hidden bg-black">
        <video
          ref={videoRef}
          src={`/videos/${currentVideo}`}
          className="w-full h-auto max-h-[500px] object-contain"
          muted
          loop={currentVideo === 'amy_idle.mp4'}
          playsInline
          preload="auto"
        />
      </div>
      
      {/* Status indicators */}
      <div className="flex justify-center gap-2 mt-3">
        {isListening && <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>}
        {isSpeaking && <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>}
        {isThinking && <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>}
      </div>
      
      {/* State label */}
      <div className="text-center mt-2">
        <span className="text-xs text-gray-400">
          {isListening ? 'Listening...' : 
           isSpeaking ? 'Speaking...' : 
           isThinking ? 'Thinking...' : 
           state === 'idle' ? 'Ready' : state}
        </span>
      </div>
    </div>
  );
}