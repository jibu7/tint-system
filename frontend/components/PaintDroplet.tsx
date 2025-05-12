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
  const colorSum = colorRGB ? colorRGB.r + colorRGB.g + colorRGB.b : 0;
  const shapeVariation = {
    borderRadius: [
      '75% 65% 70% 70% / 65% 70% 65% 70%',
      '70% 75% 65% 70% / 70% 65% 75% 65%',
      '65% 70% 75% 65% / 75% 70% 65% 70%',
      '70% 65% 70% 75% / 70% 75% 70% 65%'
    ][colorSum % 4],
    rotation: ['-12deg', '-18deg', '-15deg', '-20deg'][colorSum % 4]
  };
  
  // Generate title tooltip with color information
  const colorTitle = colorRGB 
    ? `HEX: ${colorHex} | RGB: (${colorRGB.r}, ${colorRGB.g}, ${colorRGB.b})`
    : `HEX: ${colorHex}`;

  // Calculate darker shade for bottom shadow
  const darkenColor = (hex: string, amount: number) => {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.max(0, (num >> 16) - amount);
    const g = Math.max(0, ((num >> 8) & 0xff) - amount);
    const b = Math.max(0, (num & 0xff) - amount);
    return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`;
  };

  return (
    <div 
      className={`relative inline-block ${sizeClasses[size]} ${className}`}
      title={colorTitle}
    >
      {/* Shadow underneath */}
      <div
        className="absolute bottom-0 w-full h-1/2 blur-sm opacity-40"
        style={{
          background: `radial-gradient(ellipse at center, ${darkenColor(colorHex, 60)} 0%, transparent 70%)`
        }}
      />

      {/* Main droplet shape with paint-specific variations */}
      <div
        className="absolute inset-0"
        style={{
          borderRadius: shapeVariation.borderRadius,
          transform: `rotate(${shapeVariation.rotation})`,
          background: `linear-gradient(135deg, 
            ${darkenColor(colorHex, 20)} 0%,
            ${colorHex} 50%,
            ${darkenColor(colorHex, 10)} 100%
          )`,
          boxShadow: `
            inset 0 0 20px rgba(255, 255, 255, 0.4),
            inset 0 0 10px rgba(255, 255, 255, 0.2),
            0 4px 8px rgba(0, 0, 0, 0.15),
            0 1px 3px rgba(0, 0, 0, 0.3)
          `,
          overflow: 'hidden'
        }}
      >
        {/* Main highlight gradient */}
        <div
          className="absolute"
          style={{
            width: '120%',
            height: '120%',
            top: '-30%',
            left: '-10%',
            background: `
              radial-gradient(
                ellipse at center,
                rgba(255, 255, 255, 0.5) 0%,
                rgba(255, 255, 255, 0.2) 40%,
                transparent 70%
              )
            `,
            transform: 'rotate(-20deg)',
            filter: 'blur(3px)',
            mixBlendMode: 'soft-light'
          }}
        />

        {/* Glossy highlight effect - curved highlight */}
        <div
          className="absolute"
          style={{
            width: '70%',
            height: '30%',
            background: `
              linear-gradient(
                to bottom,
                rgba(255, 255, 255, 0.7) 0%,
                rgba(255, 255, 255, 0.3) 100%
              )
            `,
            borderRadius: '50%',
            top: '15%',
            left: '15%',
            transform: 'rotate(5deg) skew(-15deg)',
            filter: 'blur(2px)'
          }}
        />

        {/* Small bright highlight */}
        <div
          className="absolute"
          style={{
            width: '12%',
            height: '12%',
            background: `
              radial-gradient(
                circle at center,
                rgba(255, 255, 255, 0.9) 0%,
                rgba(255, 255, 255, 0.6) 60%,
                transparent 100%
              )
            `,
            borderRadius: '50%',
            top: '20%',
            left: '25%'
          }}
        />

        {/* Bottom shadow gradient */}
        <div
          className="absolute bottom-0 w-full h-1/2"
          style={{
            background: `
              linear-gradient(
                to bottom,
                transparent 0%,
                rgba(0, 0, 0, 0.1) 100%
              )
            `
          }}
        />

        {/* Edge reflection */}
        <div
          className="absolute inset-0"
          style={{
            borderRadius: shapeVariation.borderRadius,
            background: `
              linear-gradient(
                135deg,
                transparent 0%,
                rgba(255, 255, 255, 0.1) 50%,
                transparent 100%
              )
            `
          }}
        />
      </div>
    </div>
  );
}
