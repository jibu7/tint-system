'use client';

import React, { useState } from 'react';
import FormulationSelectionTable from '../../components/FormulationSelectionTable';
import { IColorFormula } from '@/types/color';

// API URL from environment variable or default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function TestComponentsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFormulation, setSelectedFormulation] = useState<IColorFormula | null>(null);
  const [searchResults, setSearchResults] = useState<IColorFormula[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleFormulationSelect = (formulation: IColorFormula) => {
    console.log('Selected formulation:', formulation);
    setSelectedFormulation(formulation);
    // Scroll to selection results
    setTimeout(() => {
      document.getElementById('selection-results')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!searchTerm.trim()) {
      setError('Please enter a color code');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSelectedFormulation(null);
    setHasSearched(true);

    try {
      // Call backend API to search for the color code
      const encodedTerm = encodeURIComponent(searchTerm.trim());
      const url = `${API_BASE_URL}/api/search/${encodedTerm}`;
      console.log('Fetching from:', url);

      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        mode: 'cors',
      });

      if (!response.ok) {
        if (response.status === 404) {
          setSearchResults([]);
          setError(`No formulations found for color code "${searchTerm}"`);
        } else {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
      } else {
        const data = await response.json();

        // Handle both single result or array of results
        const formulations = Array.isArray(data) ? data : [data];
        setSearchResults(formulations);

        if (formulations.length === 0) {
          setError(`No formulations found for color code "${searchTerm}"`);
        } else if (formulations.length === 1) {
          // Auto-select if only one result
          setSelectedFormulation(formulations[0]);
        }
      }
    } catch (err) {
      console.error('Search failed:', err);
      setError(`Failed to search: ${err instanceof Error ? err.message : 'Unknown error'}`);
      setSearchResults([]);
    } finally {
      setIsLoading(false);

      // Scroll to results
      setTimeout(() => {
        document.getElementById('search-results')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  return (
    <div className="p-6 font-sans text-gray-800">
      {/* Search field */}
      <div className="mb-8 max-w-2xl mx-auto">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter color code to search"
            className="flex-grow px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition shadow-sm"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition shadow-md disabled:bg-blue-400 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </form>
      </div>

      {/* Search Results Section */}
      <div id="search-results">
        {isLoading && (
          <div className="text-center py-6">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-2 text-gray-600">Searching...</p>
          </div>
        )}

        {error && !isLoading && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {!isLoading && searchResults.length > 0 && (
          <div className="mb-10">
            <h2 className="text-2xl font-semibold mb-6 text-gray-800">
              {searchResults.length > 1
                ? `Found ${searchResults.length} formulations for "${searchTerm}"`
                : `Found 1 formulation for "${searchTerm}"`}
            </h2>

            <div className="bg-white rounded-lg shadow-md p-6">
              <FormulationSelectionTable
                formulations={searchResults}
                onSelect={handleFormulationSelect}
              />
            </div>
          </div>
        )}

        {!isLoading && hasSearched && searchResults.length === 0 && !error && (
          <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded-lg mb-6">
            No formulations found for &quot;{searchTerm}&quot;. Please try another color code.
          </div>
        )}
      </div>

      {/* Selection Results */}
      {selectedFormulation && (
        <div id="selection-results" className="mt-10 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Selected Formulation:</h2>

          {/* Display colorant details in a table if available */}
          {selectedFormulation.colorant_details && selectedFormulation.colorant_details.length > 0 && (
            <div className="mb-4">
              <h3 className="font-medium text-gray-700 mb-2">Colorant Details:</h3>
              <table className="min-w-full divide-y divide-gray-200 border rounded-lg">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Colorant</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weight (g)</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Volume (ml)</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {selectedFormulation.colorant_details.map((detail, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-2 whitespace-nowrap">{detail.colorant_name}</td>
                      <td className="px-4 py-2 whitespace-nowrap font-mono">{detail.weight_g.toFixed(5)}</td>
                      <td className="px-4 py-2 whitespace-nowrap font-mono">{detail.volume_ml.toFixed(5)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
