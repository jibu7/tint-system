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
                {Array.from(values).sort().map(value => ( // Sort values alphabetically
                  <option key={value} value={value}>{value}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}

      <div className="overflow-x-auto border border-gray-200 rounded-lg shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100">
            <tr>              <th className="px-2 py-3 text-left text-xs sm:text-sm font-semibold text-gray-600 uppercase tracking-wider">Base Paint</th>
              <th className="px-2 py-3 text-left text-xs sm:text-sm font-semibold text-gray-600 uppercase tracking-wider">Paint Type</th>
              {/* Replace Colorant Type with Color */}
              <th className="px-2 py-3 text-left text-xs sm:text-sm font-semibold text-gray-600 uppercase tracking-wider">Color</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredFormulations.length > 0 ? (
              filteredFormulations.map((formulation) => (
                <tr 
                  key={formulation.id}
                  className="hover:bg-blue-50 transition duration-150 ease-in-out cursor-pointer"
                  onClick={() => onSelect(formulation)}
                >
                  <td className="px-2 py-3 whitespace-nowrap text-sm sm:text-base text-gray-800">{formulation.base_paint}</td>                  <td className="px-2 py-3 whitespace-nowrap text-sm sm:text-base text-gray-800">{formulation.paint_type}</td>                  {/* Display Paint Droplet */}
                  <td className="px-2 py-3 whitespace-nowrap">
                    {formulation.color_rgb?.hex ? (
                      <PaintDroplet 
                        colorHex={formulation.color_rgb.hex}
                        colorRGB={formulation.color_rgb.rgb}
                        size="sm"
                      />
                    ) : (
                      <span className="text-sm text-gray-500">N/A</span> // Fallback if no color
                    )}
                  </td>
                </tr>
              ))
            ) : (              // Display a message when no formulations match the filters
              <tr>
                <td colSpan={3} className="px-6 py-12 text-center text-gray-500">
                  No formulations match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}