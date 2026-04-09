import { useEffect, useRef } from 'react';

export default function SnowBackground({ intensity = 0.3, windSpeed = 0.5 }) {
  const canvasRef = useRef(null);
  const snowflakesRef = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Create snowflakes
    class Snowflake {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 4 + 1;
        this.speed = Math.random() * 1 + 0.5;
        this.wind = (Math.random() - 0.5) * windSpeed;
        this.opacity = Math.random() * 0.8 + 0.2;
        this.wobble = Math.random() * 0.5;
        this.wobbleSpeed = Math.random() * 0.02 + 0.01;
        this.time = 0;
      }

      update() {
        this.time += this.wobbleSpeed;
        this.y += this.speed;
        this.x += this.wind + Math.sin(this.time) * this.wobble;
        
        // Reset if out of bounds
        if (this.y > canvas.height) {
          this.y = -10;
          this.x = Math.random() * canvas.width;
        }
        if (this.x > canvas.width + 10) this.x = -10;
        if (this.x < -10) this.x = canvas.width + 10;
      }

      draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
        ctx.fill();
        
        // Add sparkle effect
        if (Math.random() > 0.95) {
          ctx.beginPath();
          ctx.arc(this.x, this.y, this.size * 1.5, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity * 0.3})`;
          ctx.fill();
        }
      }
    }

    // Initialize snowflakes
    const snowflakeCount = Math.floor(canvas.width * canvas.height * intensity / 10000);
    snowflakesRef.current = [];
    for (let i = 0; i < snowflakeCount; i++) {
      snowflakesRef.current.push(new Snowflake());
    }

    // Animation loop
    let animationId;
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw snowflakes
      snowflakesRef.current.forEach(flake => {
        flake.update();
        flake.draw();
      });

      // Add wind gusts occasionally
      if (Math.random() > 0.995) {
        snowflakesRef.current.forEach(flake => {
          flake.wind += (Math.random() - 0.5) * windSpeed * 2;
        });
      }

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, [intensity, windSpeed]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 1 }}
    />
  );
}