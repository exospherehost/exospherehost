import { useEffect, useRef } from 'react';

const PulsatingGradient = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    // Extended color palette from the provided image
    const colors = [
      { hex: '#8bdfff', baseAlpha: 0.25, radius: 0.35, speed: 1.0 }, // light blue
      { hex: '#061d5f', baseAlpha: 0.18, radius: 0.32, speed: 0.8 }, // sky blue
      { hex: '#66d1b5', baseAlpha: 0.15, radius: 0.38, speed: 0.6 }, // deep blue
      { hex: '#e4587d', baseAlpha: 0.18, radius: 0.30, speed: 1.2 }, // navy blue
      { hex: '#ffed9e', baseAlpha: 0.13, radius: 0.33, speed: 0.7 }, // purple
    //   { hex: '#2B2342', baseAlpha: 0.13, radius: 0.28, speed: 1.1 }, // dark purple
    ];
    const base = '#031035'; // darkest blue

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const animate = () => {
      time += 0.003;
      // Fill background with the darkest blue
      ctx.fillStyle = base;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw each moving gradient point
      colors.forEach((color, i) => {
        const offset = (i / colors.length) * Math.PI * 2;
        const x = Math.sin(time * color.speed + offset) * canvas.width * 0.35 + canvas.width * 0.5;
        const y = Math.cos(time * color.speed * 0.7 + offset) * canvas.height * 0.35 + canvas.height * 0.5;
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, canvas.width * color.radius);
        const pulse = Math.sin(time * 2 * color.speed + offset) * 0.5 + 0.5;
        const alpha1 = Math.floor((color.baseAlpha + pulse * 0.15) * 255).toString(16).padStart(2, '0');
        const alpha2 = Math.floor((color.baseAlpha * 0.5 + pulse * 0.07) * 255).toString(16).padStart(2, '0');
        gradient.addColorStop(0, `${color.hex}${alpha1}`);
        gradient.addColorStop(0.5, `${color.hex}${alpha2}`);
        gradient.addColorStop(1, `${color.hex}00`);
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute top-0 left-0 w-full h-full"
      style={{ zIndex: 0 }}
    />
  );
};

export default PulsatingGradient; 