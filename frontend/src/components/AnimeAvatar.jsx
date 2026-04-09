import { useEffect, useRef } from 'react';

export default function AnimeAvatar({ emotion = 'neutral', isSpeaking = false, isListening = false, audioLevel = 0 }) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const timeRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = 400;
    canvas.height = 600;

    // Emotion colors
    const emotionColors = {
      happy: { hair: '#FFB6C1', skin: '#FFDAB9', dress: '#87CEEB', eyes: '#4682B4' },
      neutral: { hair: '#D8BFD8', skin: '#F5DEB3', dress: '#98FB98', eyes: '#2E8B57' },
      concerned: { hair: '#DDA0DD', skin: '#F4A460', dress: '#FFA07A', eyes: '#B22222' },
      listening: { hair: '#E6E6FA', skin: '#FFE4B5', dress: '#AFEEEE', eyes: '#20B2AA' },
      speaking: { hair: '#FFE4E1', skin: '#FFDEAD', dress: '#FFB6C1', eyes: '#DC143C' }
    };

    const colors = emotionColors[emotion] || emotionColors.neutral;

    const drawAvatar = (time) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      timeRef.current = time * 0.001;

      // Calculate animations
      const breath = Math.sin(timeRef.current * 2) * 3;
      const blink = Math.sin(timeRef.current * 3) > 0 ? 1 : 0.1;
      const speakOffset = isSpeaking ? Math.sin(timeRef.current * 20) * 5 : 0;
      const listenWiggle = isListening ? Math.sin(timeRef.current * 8) * 3 : 0;

      // Center coordinates
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2 - 50;

      // Draw hair
      ctx.fillStyle = colors.hair;
      ctx.beginPath();
      ctx.ellipse(centerX, centerY - 60, 100 + listenWiggle, 120, 0, 0, Math.PI * 2);
      ctx.fill();

      // Draw face
      ctx.fillStyle = colors.skin;
      ctx.beginPath();
      ctx.ellipse(centerX, centerY, 70, 90, 0, 0, Math.PI * 2);
      ctx.fill();

      // Draw eyes
      const eyeY = centerY - 10;
      const eyeSpacing = 25;
      
      // Left eye
      ctx.fillStyle = colors.eyes;
      ctx.beginPath();
      ctx.ellipse(centerX - eyeSpacing, eyeY, 12, 18 * blink, 0, 0, Math.PI * 2);
      ctx.fill();
      
      // Right eye
      ctx.beginPath();
      ctx.ellipse(centerX + eyeSpacing, eyeY, 12, 18 * blink, 0, 0, Math.PI * 2);
      ctx.fill();

      // Draw mouth
      ctx.fillStyle = '#FF69B4';
      const mouthWidth = isSpeaking ? 30 + speakOffset : 20;
      const mouthHeight = isSpeaking ? 10 : 5;
      ctx.beginPath();
      if (emotion === 'happy') {
        ctx.ellipse(centerX, centerY + 30, mouthWidth, mouthHeight, 0, 0, Math.PI);
      } else if (emotion === 'concerned') {
        ctx.ellipse(centerX, centerY + 35, mouthWidth * 0.7, mouthHeight, 0, Math.PI, 0);
      } else {
        ctx.ellipse(centerX, centerY + 30, mouthWidth, mouthHeight, 0, 0, Math.PI);
      }
      ctx.fill();

      // Draw dress
      ctx.fillStyle = colors.dress;
      ctx.beginPath();
      ctx.moveTo(centerX - 60, centerY + 50);
      ctx.lineTo(centerX - 80, centerY + 200);
      ctx.lineTo(centerX + 80, centerY + 200);
      ctx.lineTo(centerX + 60, centerY + 50);
      ctx.closePath();
      ctx.fill();

      // Draw glow effect when speaking
      if (isSpeaking) {
        ctx.shadowColor = colors.dress;
        ctx.shadowBlur = 30;
        ctx.beginPath();
        ctx.arc(centerX, centerY, 150, 0, Math.PI * 2);
        ctx.strokeStyle = `${colors.dress}40`;
        ctx.lineWidth = 5;
        ctx.stroke();
        ctx.shadowBlur = 0;
      }

      // Draw audio level rings
      if (audioLevel > 0.1) {
        for (let i = 0; i < 3; i++) {
          const radius = 180 + i * 30;
          const opacity = audioLevel * (1 - i * 0.3);
          ctx.strokeStyle = `rgba(135, 206, 235, ${opacity})`;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
    };

    animationRef.current = requestAnimationFrame(drawAvatar);

    return () => {
      cancelAnimationFrame(animationRef.current);
    };
  }, [emotion, isSpeaking, isListening, audioLevel]);

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        className="rounded-2xl shadow-2xl border-4 border-white/20"
      />
      
      {/* Status indicator */}
      <div className="absolute -top-2 -right-2">
        <div className={`w-6 h-6 rounded-full border-2 border-white ${
          isSpeaking ? 'bg-red-500 animate-pulse' :
          isListening ? 'bg-green-500 animate-pulse' :
          'bg-blue-500'
        }`}></div>
      </div>
      
      {/* Emotion label */}
      <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2">
        <div className="px-3 py-1 bg-white/90 backdrop-blur-sm rounded-full border border-gray-200">
          <span className="text-sm font-medium text-gray-700 capitalize">{emotion}</span>
        </div>
      </div>
    </div>
  );
}