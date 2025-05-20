'use client';

import React, { useState } from 'react';
import FormulationSelectionTable from '../../components/FormulationSelectionTable';
import PaintDroplet from '@/components/PaintDroplet';
import { IColorFormula } from '@/types/color';

// API URL from environment variable or default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (process.env.NEXT_PUBLIC_VERCEL_URL ? '' : 'http://localhost:8001');

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
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 font-sans text-gray-800">
      <div className="py-6 sm:py-10 mb-6 sm:mb-12 text-center">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Color Formulation</h1>
        <p className="text-gray-600 text-sm sm:text-base max-w-2xl mx-auto">Search for color formulations by entering a color code</p>
      </div>
      
      {/* Search field */}
      <div className="mb-8 sm:mb-12 max-w-2xl mx-auto">
        <div className="bg-white p-4 sm:p-6 rounded-xl shadow-md">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Enter color code"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition shadow-sm text-base"
              aria-label="Color code search"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full sm:w-auto px-5 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition shadow-md disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Searching</span>
                </>
              ) : 'Search'}
            </button>
          </form>
        </div>
      </div>

      {/* Search Results Section */}
      <div id="search-results" className="mb-8 sm:mb-12 scroll-mt-6">
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600 font-medium">Searching for formulations...</p>
          </div>
        )}

        {error && !isLoading && (
          <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-6 py-4 rounded-lg mb-8 shadow-sm">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-500 mr-3" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p>{error}</p>
            </div>
          </div>
        )}

        {!isLoading && searchResults.length > 0 && (
          <div className="mb-8 sm:mb-12 animate-fadeIn">
            <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6 text-gray-900 border-b pb-2">
              {searchResults.length > 1
                ? `Found ${searchResults.length} formulations for "${searchTerm}"`
                : `Found 1 formulation for "${searchTerm}"`}
            </h2>

            <div className="bg-white rounded-xl shadow-md p-3 sm:p-6 border border-gray-100 overflow-x-auto">
              <FormulationSelectionTable
                formulations={searchResults}
                onSelect={handleFormulationSelect}
              />
            </div>
          </div>
        )}

        {!isLoading && hasSearched && searchResults.length === 0 && !error && (
          <div className="bg-blue-50 border-l-4 border-blue-500 text-blue-700 px-6 py-4 rounded-lg mb-8 shadow-sm">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-blue-500 mr-3" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <p>No formulations found for &quot;{searchTerm}&quot;. Please try another color code.</p>
            </div>
          </div>
        )}
      </div>

      {/* Selection Results */}
      {selectedFormulation && (
        <div id="selection-results" className="mt-8 sm:mt-12 mb-8 bg-white rounded-xl shadow-lg p-4 sm:p-8 border border-gray-100 scroll-mt-6 animate-fadeIn">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6 border-b pb-3">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-2 sm:mb-0">Selected Formulation</h2>
            <div className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full self-start">
              {selectedFormulation.color_code}
            </div>
          </div>

          {/* Base Paint Details */}
          {selectedFormulation.colorant_details && selectedFormulation.colorant_details.length > 0 && (
            <div className="mb-6 sm:mb-8">
              <div className="flex items-center mb-3">
                <svg className="h-5 w-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <h3 className="font-semibold text-lg text-gray-800">Base Information</h3>
              </div>
              
              {/* Mobile view - card style for small screens */}
              <div className="block sm:hidden bg-gray-50 rounded-lg overflow-hidden border border-gray-200 p-4">
                <div className="mb-4">
                  <div className="text-xs font-bold text-gray-600 uppercase mb-1">Base Paint</div>
                  <div className="text-sm font-medium text-gray-900">{selectedFormulation.base_paint}</div>
                </div>
                <div className="mb-4">
                  <div className="text-xs font-bold text-gray-600 uppercase mb-1">Paint Type</div>
                  <div className="text-sm text-gray-700">{selectedFormulation.paint_type}</div>
                </div>
                <button 
                  className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                >
                  Select
                </button>
              </div>
              
              {/* Desktop view - table style for larger screens */}              <div className="hidden sm:block bg-gray-50 rounded-lg overflow-hidden border border-gray-200">                <table className="min-w-full divide-y divide-gray-200"><thead className="bg-gray-100"><tr><th className="px-6 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Base Paint</th><th className="px-6 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Paint Type</th><th className="px-6 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Color</th></tr></thead><tbody><tr className="bg-white"><td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{selectedFormulation.base_paint}</td><td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{selectedFormulation.paint_type}</td><td className="px-6 py-4 whitespace-nowrap">{selectedFormulation.color_rgb?.hex ? (<PaintDroplet colorHex={selectedFormulation.color_rgb.hex} colorRGB={selectedFormulation.color_rgb.rgb} size="md" />) : (<span className="text-sm text-gray-500">N/A</span>)}</td></tr></tbody></table>
              </div>
            </div>
          )}
          
          {/* Colorant Details */}
          {selectedFormulation.colorant_details && selectedFormulation.colorant_details.length > 0 && (
            <div>
              <div className="flex items-center mb-3">
                <svg className="h-5 w-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                </svg>
                <h3 className="font-semibold text-lg text-gray-800">Colorant Composition</h3>
              </div>
              
              {/* Mobile view - cards for each colorant */}
              <div className="block sm:hidden space-y-3">
                {selectedFormulation.colorant_details.map((detail, index) => (
                  <div key={index} className={`p-3 rounded-lg border ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                    <div className="font-medium text-gray-900 mb-1">{detail.colorant_name}</div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-xs text-gray-500">Weight:</span>
                        <span className="ml-1 font-mono">{detail.weight_g.toFixed(5)} g</span>
                      </div>
                      <div>
                        <span className="text-xs text-gray-500">Volume:</span>
                        <span className="ml-1 font-mono">{detail.volume_ml.toFixed(5)} ml</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Desktop view - table for larger screens */}
              <div className="hidden sm:block bg-gray-50 rounded-lg overflow-hidden border border-gray-200">                <div className="overflow-x-auto"><table className="min-w-full divide-y divide-gray-200"><thead className="bg-gray-100"><tr><th className="px-6 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Colorant</th><th className="px-6 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Weight (g)</th><th className="px-6 py-3 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">Volume (ml)</th></tr></thead><tbody className="bg-white divide-y divide-gray-200">{selectedFormulation.colorant_details.map((detail, index) => (<tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}><td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{detail.colorant_name}</td><td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-700">{detail.weight_g.toFixed(5)}</td><td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-700">{detail.volume_ml.toFixed(5)}</td></tr>))}</tbody></table></div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
