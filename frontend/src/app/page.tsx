'use client'; // Required for client-side hooks (useState, useEffect)

import React, { useState, FormEvent, useCallback, useEffect } from 'react';
import { IColorFormula, IApiError, IColorantDetail } from '@/types/color'; // Adjust path if needed

// Read API URL from environment variable, fallback for safety
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper for consistent number formatting
const formatNumber = (value: number, fractionDigits: number): string => {
    // Avoid issues with -0.00000 display if needed, though toFixed handles precision
    const fixedValue = value.toFixed(fractionDigits);
    return fixedValue === `-0.${'0'.repeat(fractionDigits)}` ? `0.${'0'.repeat(fractionDigits)}` : fixedValue;
};
const formatWeight = (value: number) => formatNumber(value, 5); // 5 decimal places for grams
const formatVolume = (value: number) => formatNumber(value, 7); // 7 decimal places for ml

export default function HomePage() {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [result, setResult] = useState<IColorFormula | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  // Store the actual term searched to display "No results for..." message correctly
  const [searchedTermDisplay, setSearchedTermDisplay] = useState<string | null>(null);

  // Test backend connection on component mount
  useEffect(() => {
    const testConnection = async () => {
      try {
        console.log("Testing connection to backend at:", API_BASE_URL);
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log("Backend health check result:", data);
      } catch (err) {
        console.error("Backend connection test failed:", err);
        console.log("Check that your backend is running and accessible at:", API_BASE_URL);
      }
    };
    
    testConnection();
  }, []);

  const handleSearch = useCallback(async (term: string) => {
    if (!term) {
      setError('Please enter a Color Code.');
      setResult(null);
      setSearchedTermDisplay(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setSearchedTermDisplay(term); // Store the term we are actually searching for

    try {
      // Encode the search term for safe use in URL
      const encodedTerm = encodeURIComponent(term);
      const url = `${API_BASE_URL}/api/search/${encodedTerm}`;
      console.log("Fetching from URL:", url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        // Adding explicit mode can help with CORS issues
        mode: 'cors',
        // Increase timeout with signal if needed
        // signal: AbortSignal.timeout(10000), // 10 second timeout (only works in modern browsers)
      });

      if (!response.ok) {
        let errorData: IApiError = { detail: `HTTP error! Status: ${response.status}` };
        try {
          // Try to parse specific error message from backend
          errorData = await response.json();
        } catch (jsonError) {
          // Fallback if response is not JSON
          console.error("Failed to parse error response:", jsonError);
        }
        throw new Error(errorData.detail || `Request failed with status ${response.status}`);
      }

      const data: IColorFormula = await response.json();
      setResult(data);

    } catch (err: any) {
      console.error("Search failed:", err);
      
      // More verbose error reporting
      if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
        setError('Network error: Could not connect to the API server. Please check that the backend is running and accessible.');
      } else {
        setError(err.message || 'An unexpected error occurred while fetching data.');
      }
      
      setResult(null); // Clear results on error
    } finally {
      setIsLoading(false);
    }
  }, []); // Empty dependency array as API_BASE_URL is constant within component lifecycle

  const onFormSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); // Prevent default form submission (page reload)
    handleSearch(searchTerm.trim());
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-start p-6 sm:p-12 md:p-24 bg-gradient-to-b from-gray-50 to-gray-100 font-sans">
      <div className="w-full max-w-3xl bg-white rounded-xl shadow-xl p-6 md:p-10 border border-gray-200">
        <h1 className="text-3xl md:text-4xl font-bold text-center text-gray-800 mb-8">
          Color Code Search
        </h1>

        {/* Search Form */}
        <form onSubmit={onFormSubmit} className="flex flex-col sm:flex-row gap-3 mb-10">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter Color Code (e.g., BC0001-4)"
            className="flex-grow px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition duration-200 ease-in-out shadow-sm"
            aria-label="Color Code Input"
            required // Basic HTML5 validation
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-7 py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed transition duration-200 ease-in-out shadow-md hover:shadow-lg"
          >
            {isLoading ? (
               <svg className="animate-spin h-5 w-5 text-white inline mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                 <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                 <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
               </svg>
            ) : null}
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </form>

        {/* Status/Results Area */}
        <div className="mt-6 min-h-[250px] p-1"> {/* Min height to prevent layout shifts */}
          {isLoading && (
             <div className="flex justify-center items-center h-full">
                <p className="text-lg text-gray-500 animate-pulse">Loading results...</p>
             </div>
          )}

          {error && !isLoading && (
             <div className="text-center bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg shadow-sm" role="alert">
                <strong className="font-bold">Error: </strong>
                <span className="block sm:inline">{error}</span>
             </div>
          )}

          {result && !isLoading && !error && (
            <div className="border border-gray-200 rounded-lg p-5 md:p-6 bg-gray-50 shadow-sm transition-opacity duration-500 ease-in-out opacity-100">
               {/* General Info */}
               <h2 className="text-2xl font-semibold mb-5 text-gray-700 border-b pb-2">
                 Color Code: <span className="font-bold text-gray-900">{result.color_code}</span>
               </h2>
               <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 mb-6 text-base text-gray-600">
                 <p><strong className="font-medium text-gray-800">Color Series:</strong> {result.color_series || 'N/A'}</p>
                 <p><strong className="font-medium text-gray-800">Color Card:</strong> {result.color_card || 'N/A'}</p>
                 <p><strong className="font-medium text-gray-800">Paint Type:</strong> {result.paint_type || 'N/A'}</p>
                 <p><strong className="font-medium text-gray-800">Base Paint:</strong> {result.base_paint || 'N/A'}</p>
               </div>

               {/* Colorants Table */}
               <h3 className="text-xl font-semibold mb-3 text-gray-700">Colorants Required:</h3>
               {result.colorants && result.colorants.length > 0 ? (
                  <div className="overflow-x-auto rounded-md border border-gray-300">
                     <table className="min-w-full divide-y divide-gray-200">
                     <thead className="bg-gray-100">
                       <tr>
                         <th scope="col" className="px-5 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Name</th>
                         <th scope="col" className="px-5 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Weight (g)</th>
                         <th scope="col" className="px-5 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Volume (ml)</th>
                       </tr>
                     </thead>
                     <tbody className="bg-white divide-y divide-gray-200">
                       {result.colorants.map((colorant: IColorantDetail, index: number) => (
                         <tr key={index} className="hover:bg-blue-50 transition duration-150 ease-in-out">
                           <td className="px-5 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{colorant.name}</td>
                           <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-700 font-mono">{formatWeight(colorant.weight_g)}</td>
                           <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-700 font-mono">{formatVolume(colorant.volume_ml)}</td>
                         </tr>
                       ))}
                     </tbody>
                   </table>
                  </div>
               ) : (
                 <p className="text-sm text-gray-500 italic">No specific colorant data available for this code.</p>
               )}
            </div>
          )}

           {/* Initial state or No Results Found */}
           {!isLoading && !error && !result && searchedTermDisplay && (
             <p className="text-center text-gray-500 pt-10">No results found for "{searchedTermDisplay}".</p>
           )}
            {!isLoading && !error && !result && !searchedTermDisplay && (
             <p className="text-center text-gray-400 pt-10">Enter a color code above and click Search.</p>
           )}
        </div>
      </div>
    </main>
  );
}
