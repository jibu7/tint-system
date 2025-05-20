'use client';

import React, { useState } from 'react';
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
  
  // Define keys to exclude from filters
  const excludedFilterKeys = ['id', 'colorant_details', 'color_code', 'created_at', 'updated_at', 'color_rgb'];

  // Extract unique values for each attribute to build filters
  const filterOptions = formulations.reduce<FilterOptions>((options, form) => {
    Object.keys(form).forEach(key => {
      // Exclude specified keys from filters
      if (!excludedFilterKeys.includes(key)) {
        if (!options[key]) options[key] = new Set<string>();
        // Ensure value exists and convert to string before adding
        if (form[key] !== null && form[key] !== undefined) {
          options[key].add(String(form[key]));
        }
      }
    });
    return options;
  }, {});
  
  // Apply filters to formulations
  const filteredFormulations = formulations.filter(form => {
    return Object.entries(filters).every(([key, value]) => 
      !value || String(form[key]) === value // Ensure comparison is done with string values
    );
  });

  return (
    <div className="font-sans">
      {/* Filter Section - Only render if there are options */} 
      {Object.keys(filterOptions).length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          {Object.entries(filterOptions).map(([key, values]) => (
            <div key={key} className="flex flex-col">
              <label className="text-sm font-medium mb-1.5 capitalize text-gray-700">
                {key.replace(/_/g, ' ')}
              </label>
              <select
                value={filters[key] || ''}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setFilters({...filters, [key]: e.target.value})}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm bg-white text-gray-800 shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition duration-150 ease-in-out"
              >
                <option value="">All</option>
                {Array.from(values).sort().map(value => (
                  <option key={value} value={value}>{value}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}

      {filteredFormulations.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
          {filteredFormulations.map((formulation) => (
            <div 
              key={`${formulation.color_code}-${formulation.paint_type}-${formulation.base_paint}`}
              onClick={() => onSelect(formulation)}
              className="flex flex-col items-center p-4 hover:bg-gray-50 rounded-lg transition duration-150 ease-in-out cursor-pointer group border border-gray-200"
            >
              <div className="mb-3 transform group-hover:scale-105 transition duration-150">
                <PaintDroplet 
                  colorHex={formulation.color_rgb?.hex || '#CCCCCC'}
                  colorRGB={formulation.color_rgb?.rgb}
                  size="lg"
                />
              </div>
              <div className="text-center">
                <h3 className="font-medium text-gray-900">
                  {formulation.color_code || 'Unknown'}
                </h3>
                <p className="text-sm font-medium text-blue-600 mt-1">
                  {formulation.base_paint}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  {formulation.paint_type}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-white border border-gray-200 rounded-lg">
          <p className="text-gray-500">No formulations match the current filters.</p>
        </div>
      )}
    </div>
  );
}