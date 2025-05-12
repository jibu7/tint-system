'use client';

import React, { useState, useEffect } from 'react';
import { IColorFormula } from '@/types/color';
import PaintDroplet from './PaintDroplet';

interface FormulationCardSelectorProps {
  formulations: IColorFormula[];
  onSelect: (formulation: IColorFormula) => void;
}

export default function FormulationCardSelector({ formulations, onSelect }: FormulationCardSelectorProps) {
  const [activeStep, setActiveStep] = useState(0);
  const [filteredFormulations, setFilteredFormulations] = useState<IColorFormula[]>(formulations);
  const [selections, setSelections] = useState<Record<string, string>>({});

  // Wake up the database when the component mounts
  useEffect(() => {
    const wakeUpDatabase = async () => {
      try {
        console.log('Sending database wake-up call...');
        // Determine the base API URL based on the environment
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/wakeup`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          console.log('Database wake-up successful');
        } else {
          console.warn('Database wake-up returned non-200 status:', response.status);
        }
      } catch (error) {
        console.error('Failed to wake up database:', error);
        // We don't want to block the UI if the wake-up fails
      }
    };

    // Call the wake-up function immediately when component mounts
    wakeUpDatabase();
  }, []);

  // Determine selection steps dynamically based on available attributes
  const steps = ['Paint Type', 'Base Paint', 'Colorant Type', 'Final Selection'];
  
  // When a selection is made, filter formulations and move to next step
  const handleSelection = (attribute: string, value: string) => {
    const newSelections = { ...selections, [attribute.toLowerCase()]: value };
    setSelections(newSelections);
    
    // Filter formulations based on all current selections
    const filtered = formulations.filter(f => {
      return Object.entries(newSelections).every(([key, val]) => 
        f[key === 'paint_type' ? 'paint_type' : key] === val
      );
    });
    
    setFilteredFormulations(filtered);
    setActiveStep(prevStep => prevStep + 1);
  };

  // Render different step content based on activeStep
  const getStepContent = (step: number) => {
    switch (step) {
      case 0: // Paint Type selection
        const paintTypes = [...new Set(formulations.map(f => f.paint_type))];
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {paintTypes.map(type => type && (
              <div 
                key={type}
                className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-all hover:translate-y-[-4px]"
                onClick={() => handleSelection('paint_type', type)}
              >
                <h3 className="font-medium text-lg mb-2">{type}</h3>                <p className="text-sm text-gray-600">
                  {`${formulations.filter(f => f.paint_type === type).length} options available`}
                </p>
              </div>
            ))}
          </div>
        );
      
      case 1: // Base Paint selection
        const basePaints = [...new Set(filteredFormulations.map(f => f.base_paint))];
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {basePaints.map(base => base && (
              <div 
                key={base}
                className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-all hover:translate-y-[-4px]"
                onClick={() => handleSelection('base_paint', base)}
              >              <h3 className="font-medium text-lg">{base}</h3>
              </div>
            ))}
          </div>
        );
      
      case 2: // Colorant Type selection
        const colorantTypes = [...new Set(filteredFormulations.map(f => f.colorant_type))];
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {colorantTypes.map(colorant => colorant && (
              <div 
                key={colorant}
                className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-all hover:translate-y-[-4px]"
                onClick={() => handleSelection('colorant_type', colorant)}
              >              <h3 className="font-medium text-lg">{colorant}</h3>
              </div>
            ))}
          </div>
        );
      
      case 3: // Final selection with all details
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {filteredFormulations.map((formulation) => (
              <div 
                key={formulation.id} 
                className="border rounded-lg p-5 flex flex-col h-full hover:shadow-md cursor-pointer transition-all hover:translate-y-[-4px]"
                onClick={() => onSelect(formulation)}
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-bold text-lg text-blue-700">
                      {formulation.color_code}
                    </h3>
                    <div className="text-lg font-medium text-gray-800 mt-1">
                      Base: {formulation.base_paint}
                    </div>
                  </div>
                  {formulation.color_rgb?.hex && (
                    <PaintDroplet 
                      colorHex={formulation.color_rgb.hex}
                      colorRGB={formulation.color_rgb.rgb}
                      size="lg"
                    />
                  )}
                </div>
                <div className="space-y-2">
                  <div><span className="font-medium">Paint Type:</span> {formulation.paint_type}</div>
                  <div><span className="font-medium">Colorant:</span> {formulation.colorant_type}</div>
                  <div><span className="font-medium">Packaging:</span> {formulation.packaging_spec}</div>
                </div>
              </div>
            ))}
          </div>
        );
      
      default:
        return 'Unknown step';
    }
  };

  return (
    <div className="font-sans">
      <div className="flex mb-8">
        {steps.map((label, index) => (
          <div key={label} className="flex-1">
            <div className={`text-center p-2 ${activeStep === index ? 'font-bold text-blue-600' : 'text-gray-500'}`}>
              {label}
            </div>
            {index < steps.length - 1 && (
              <div className="flex items-center justify-center">
                <div className={`h-0.5 w-full ${index < activeStep ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="my-6">
        {activeStep < steps.length ? (
          <>
            <h2 className="text-xl font-semibold mb-6 text-center text-gray-800">
              {steps[activeStep]}
            </h2>
            {getStepContent(activeStep)}
          </>
        ) : (
          <div className="text-center text-lg font-medium text-green-600">
            Formula selected successfully!
          </div>
        )}
      </div>
      
      {activeStep > 0 && (
        <div className="mt-4">
          <button 
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
            onClick={() => setActiveStep(prev => prev - 1)}
          >
            Back
          </button>
        </div>
      )}
    </div>
  );
}