'use client';

import React, { useState, useEffect } from 'react';
import { IColorFormula } from '@/types/color';

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
      </div>

      <div className="overflow-x-auto border border-gray-300 rounded-lg shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100">
            <tr><th className="px-2 py-3 text-left text-xs sm:text-sm font-semibold text-gray-700 uppercase tracking-wider">Base Paint</th><th className="px-2 py-3 text-left text-xs sm:text-sm font-semibold text-gray-700 uppercase tracking-wider">Paint Type</th><th className="px-2 py-3 text-left text-xs sm:text-sm font-semibold text-gray-700 uppercase tracking-wider">Color</th><th className="px-2 py-3 text-left text-xs sm:text-sm font-semibold text-gray-700 uppercase tracking-wider">Action</th></tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredFormulations.map((formulation) => (
              <tr key={formulation.id} className="hover:bg-blue-50 cursor-pointer" onClick={() => onSelect(formulation)}>
                <td className="px-2 py-3 text-sm sm:text-base text-gray-800">{formulation.base_paint}</td><td className="px-2 py-3 text-sm sm:text-base text-gray-800">{formulation.paint_type}</td><td className="px-2 py-3">{formulation.color_rgb?.hex ? (<div className="w-6 h-6 rounded border border-gray-300" style={{ backgroundColor: formulation.color_rgb.hex }} title={`HEX: ${formulation.color_rgb.hex} | RGB: (${formulation.color_rgb.rgb.r}, ${formulation.color_rgb.rgb.g}, ${formulation.color_rgb.rgb.b})`}></div>) : (<div className="w-6 h-6 rounded border border-gray-300 bg-gray-200" title="Color data not available"></div>)}</td><td className="px-2 py-3"><button className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-3 py-1.5 sm:px-4 sm:py-2 rounded-md text-xs sm:text-sm shadow-sm" onClick={(e: React.MouseEvent) => { e.stopPropagation(); onSelect(formulation); }}>Select</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
