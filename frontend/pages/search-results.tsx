import React, { useEffect } from 'react';
import FormulationSelectionTable from '../components/FormulationSelectionTable';
import { useRouter } from 'next/router';
import { IColorFormula } from '@/types/color';
import PaintDroplet from '../components/PaintDroplet';

interface SearchResultsProps {
  results?: IColorFormula[];
}

export default function SearchResults({ results = [] }: SearchResultsProps) {
  const router = useRouter();

  // Wake up the database as soon as the search results page loads
  useEffect(() => {
    const wakeUpDatabase = async () => {
      try {
        console.log('Search Results: Sending database wake-up call...');
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${baseUrl}/api/wakeup`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          console.log('Database wake-up successful from search results page');
        } else {
          console.warn('Database wake-up returned non-200 status:', response.status);
        }
      } catch (error) {
        console.error('Failed to wake up database from search results page:', error);
      }
    };

    wakeUpDatabase();
  }, []);

  // For demo/example purposes
  const searchResults = results.length > 0 ? results : [
    {
      id: 1,
      color_code: '1294T',
      paint_type: 'Interior',
      base_paint: 'Pastel Base',
      colorant_type: 'Universal',
      packaging_spec: '1 Gallon',
      colorant_details: [
        { colorant_name: 'Black', weight_g: 12.5, volume_ml: 10.2 },
        { colorant_name: 'Yellow Oxide', weight_g: 24.3, volume_ml: 18.7 }
      ]
    },
    {
      id: 2,
      color_code: '1294T',
      paint_type: 'Exterior',
      base_paint: 'Pastel Base',
      colorant_type: 'Universal',
      packaging_spec: '1 Gallon',
      colorant_details: [
        { colorant_name: 'Black', weight_g: 13.1, volume_ml: 10.7 },
        { colorant_name: 'Yellow Oxide', weight_g: 25.0, volume_ml: 19.2 }
      ]
    },
  ];

  const handleFormulationSelect = (formulation: IColorFormula) => {
    // Navigate to details page or show details panel
    router.push(`/formulation/${formulation.id}`);
  };

  if (searchResults.length === 0) {
    return (
      <div className="container mx-auto py-16 px-4">
        <div className="bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded mb-4">
          No formulations found for this color code. Please try another search.
        </div>
        <button 
          className="bg-blue-500 text-white px-4 py-2 rounded"
          onClick={() => router.push('/')}
        >
          Back to Search
        </button>
      </div>
    );
  }

  if (searchResults.length === 1) {
    // If only one result, auto-select it or show differently
    return (
      <div className="container mx-auto py-16 px-4">
        <h1 className="text-2xl font-bold mb-4">
          One formula found for color code {searchResults[0].color_code}
        </h1>
        <div className="mt-8">
          <div 
            className="border rounded-lg p-5 hover:shadow-md cursor-pointer transition-all hover:border-blue-500"
            onClick={() => handleFormulationSelect(searchResults[0])}
          >
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xl font-medium mb-2">Base Paint: {searchResults[0].base_paint}</div>
                <div className="text-gray-600">Paint Type: {searchResults[0].paint_type}</div>
                <div className="text-gray-600 mt-1">Colorant Type: {searchResults[0].colorant_type}</div>
              </div>
              {searchResults[0].color_rgb?.hex && (
                <PaintDroplet 
                  colorHex={searchResults[0].color_rgb.hex}
                  colorRGB={searchResults[0].color_rgb.rgb}
                  size="lg"
                />
              )}
            </div>
            <div className="mt-3 text-sm text-blue-600">Click to view full details</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-16 px-4">
      <h1 className="text-2xl font-bold mb-4 text-center">
        Multiple Formulas for {searchResults[0].color_code}
      </h1>
      
      <p className="text-center mb-8">
        We found {searchResults.length} formulations for this color code.
        Please select the right one for your project.
      </p>
      
      <FormulationSelectionTable 
        formulations={searchResults} 
        onSelect={handleFormulationSelect}
      />
    </div>
  );
}

// If you're using Next.js data fetching
export async function getServerSideProps(context: {query: {colorCode?: string}}) {
  const { colorCode } = context.query;

  if (!colorCode) {
    return {
      redirect: {
        destination: '/',
        permanent: false,
      },
    };
  }

  try {
    // First, wake up the database before performing any search
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const wakeupUrl = `${baseUrl}/api/wakeup`;
    
    try {
      // Send wake-up call to the database
      console.log('SSR: Sending database wake-up call...');
      await fetch(wakeupUrl);
      console.log('SSR: Database wake-up call completed');
    } catch (wakeupError) {
      console.error('SSR: Failed to wake up database:', wakeupError);
      // Continue even if wake-up fails
    }
    
    // Then perform the actual search
    const res = await fetch(`${baseUrl}/api/search/${colorCode}`);
    const results = await res.json();

    return {
      props: { results },
    };
  } catch (error) {
    console.error('Error fetching results:', error);
    return {
      props: { results: [] },
    };
  }
}
