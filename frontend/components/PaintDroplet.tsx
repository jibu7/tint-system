'use client';

import React from 'react';

interface PaintDropletProps {
  colorHex: string;
  colorRGB?: {
    r: number;
    g: number;
    b: number;
  };
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function PaintDroplet({ 
  colorHex, 
  colorRGB, 
  size = 'md', 
  className = '' 
}: PaintDropletProps) {
  // Size mapping
  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-14 h-14',
    lg: 'w-20 h-20'
  };

  // Generate a random shape variation (but consistent for the same color)
  // This creates slight variation in droplet shapes like in your reference image
  const colorSum = colorRGB ? colorRGB.r + colorRGB.g + colorRGB.b : 0;
  const shapeVariation = {
    borderRadius: [
      '70% 60% 70% 60% / 60% 65% 70% 65%',
      '65% 75% 60% 65% / 70% 60% 70% 60%',
      '60% 60% 75% 65% / 60% 70% 60% 75%',
      '70% 65% 60% 75% / 65% 70% 75% 60%'
    ][colorSum % 4],
    rotation: ['-10deg', '-20deg', '-15deg', '-25deg'][colorSum % 4]
  };
  
  // Generate title tooltip with color information
  const colorTitle = colorRGB 
    ? `HEX: ${colorHex} | RGB: (${colorRGB.r}, ${colorRGB.g}, ${colorRGB.b})`
    : `HEX: ${colorHex}`;

  return (
    <div 
      className={`relative inline-block ${sizeClasses[size]} ${className}`}
      title={colorTitle}
    >
      {/* Main droplet shape with paint-specific variations */}
      <div
        className="absolute inset-0 rounded-full overflow-hidden"
        style={{
          borderRadius: shapeVariation.borderRadius,
          backgroundColor: colorHex,
          transform: `rotate(${shapeVariation.rotation})`,
          boxShadow: 'inset 0 0 15px rgba(255, 255, 255, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2)'
        }}
      >
        {/* Glossy highlight effect - larger curved highlight */}
        <div
          className="absolute"
          style={{
            width: '80%',
            height: '40%',
            backgroundColor: 'rgba(255, 255, 255, 0.4)',
            borderRadius: '100%',
            top: '10%',
            left: '10%',
            transform: 'rotate(10deg)',
            filter: 'blur(2px)'
          }}
        ></div>
        
        {/* Small highlight dot */}
        <div
          className="absolute"
          style={{
            width: '15%',
            height: '15%',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderRadius: '100%',
            top: '15%',
            left: '20%',
          }}
        ></div>
        
        {/* Edge highlight for a more 3D effect */}
        <div
          className="absolute inset-0"
          style={{
            borderRadius: shapeVariation.borderRadius,
            boxShadow: 'inset 0 0 20px rgba(255, 255, 255, 0.2)',
            opacity: 0.7
          }}
        ></div>
      </div>
    </div>
  );
}
