import React from 'react';
import FormulationSelectionTable from '../components/FormulationSelectionTable';
import { useRouter } from 'next/router';
import { IColorFormula } from '@/types/color';

interface SearchResultsProps {
  results?: IColorFormula[];
}

export default function SearchResults({ results = [] }: SearchResultsProps) {
  const router = useRouter();

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
          <button 
            className="bg-blue-600 text-white px-4 py-2 rounded font-medium"
            onClick={() => handleFormulationSelect(searchResults[0])}
          >
            View Formula Details
          </button>
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
    const res = await fetch(`http://localhost:8000/api/search/${colorCode}`);
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
