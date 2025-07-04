'use client'
import React, { useEffect, useState } from 'react';

interface Star {
  id: number;
  x: number;
  y: number;
  size: number;
  opacity: number;
}

const Stars: React.FC = () => {
  const [stars, setStars] = useState<Star[]>([]);

  useEffect(() => {
    // Generate random stars
    const generateStars = () => {
      const newStars: Star[] = [];
      const count = 150; // Number of stars
      
      for (let i = 0; i < count; i++) {
        newStars.push({
          id: i,
          x: Math.random() * 100, // Random x position (percentage)
          y: Math.random() * 100, // Random y position (percentage)
          size: Math.random() * 2 + 1, // Random size between 1-3px
          opacity: Math.random() * 0.8 + 0.2, // Random opacity between 0.2-1
        });
      }
      
      setStars(newStars);
    };

    generateStars();

    // Animate stars
    const interval = setInterval(() => {
      setStars(prevStars => 
        prevStars.map(star => ({
          ...star,
          opacity: Math.random() * 0.8 + 0.2, // Randomly change opacity
        }))
      );
    }, 2000); // Update every 2 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {stars.map(star => (
        <div
          key={star.id}
          className="absolute rounded-full bg-white"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            opacity: star.opacity,
            transition: 'opacity 2s ease-in-out',
          }}
        />
      ))}
    </div>
  );
};

export default Stars; 