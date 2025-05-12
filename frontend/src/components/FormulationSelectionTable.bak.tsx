'use client';

import React, { useState, useEffect } from 'react';
import { IColorFormula } from '@/types/color';
import PaintDroplet from './PaintDroplet';

interface FormulationSelectionTableProps {
  formulations: IColorFormula[];
  onSelect: (formulation: IColorFormula) => void;
}

interface FilterOptions {
  [key: string]: Set<string>;
}

export default function FormulationSelectionTable({ formulations, onSelect }: FormulationSelectionTableProps) {
  const [filters, setFilters] = useState<Record<string, string>>({});

  useEffect(() => {
    fetch('/api/wakeup');
  }, []);
  
  // Extract unique values for each attribute to build filters
  const filterOptions = formulations.reduce<FilterOptions>((options, form) => {
    Object.keys(form).forEach(key => {
      // Exclude non-filterable or internal keys
      if (!['id', 'colorant_details', 'color_code', 'created_at', 'updated_at', 'color_rgb'].includes(key)) {
        if (!options[key]) options[key] = new Set<string>();
        // Ensure value exists and is stringifiable before adding
        if (form[key] !== null && form[key] !== undefined) {
          options[key].add(form[key]!.toString());
        }
      }
    });
    return options;
  }, {});
  
  // Apply filters to formulations
  const filteredFormulations = formulations.filter(form => {
    return Object.entries(filters).every(([key, value]) => 
      !value || form[key] === value
    );
  });

  return (
    <div className="font-sans">
      <div className="flex flex-wrap gap-4 mb-6 p-2">
        {Object.entries(filterOptions).map(([key, values]) => (
          <div key={key} className="flex flex-col">
            <label className="text-sm font-medium mb-1.5 capitalize text-gray-700">
              {key.replace(/_/g, ' ')}
            </label>
            <select
              value={filters[key] || ''}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFilters({...filters, [key]: e.target.value})}
              className="border border-gray-300 rounded-md px-3 py-2 text-base bg-white text-gray-800 shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All</option>
              {Array.from(values).map(value => (
                <option key={value} value={value}>{value}</option>
              ))}
            </select>
          </div>
        ))}
      </div>      {filteredFormulations.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {filteredFormulations.map((formulation) => (
            <div 
              key={formulation.id}
              className="border border-gray-200 rounded-lg shadow-sm overflow-hidden hover:shadow-md transition duration-200 cursor-pointer"
              onClick={() => onSelect(formulation)}
            >
              <div className="p-4 flex justify-center">
                {formulation.color_rgb?.hex ? (
                  <PaintDroplet 
                    colorHex={formulation.color_rgb.hex}
                    colorRGB={formulation.color_rgb.rgb}
                    size="lg"
                  />
                ) : (
                  <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center">
                    <span className="text-gray-500 text-sm">No color</span>
                  </div>
                )}
              </div>
              
              <div className="px-4 py-3 border-t border-gray-100 bg-gray-50">
                <div className="font-medium text-center text-gray-800">
                  {formulation.color_code || 'Unknown'}
                </div>
                <div className="mt-1 text-sm text-center text-gray-500">
                  {formulation.base_paint}
                </div>
              </div>
            </div>
          ))}
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
