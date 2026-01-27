import { useState } from 'react';
import InputField from './InputField';

interface SearchFormProps {
  origin: string;
  destination: string;
  loading: boolean;
  onOriginChange: (value: string) => void;
  onDestinationChange: (value: string) => void;
  onSearch: () => void;
}

export default function SearchForm({
  origin,
  destination,
  loading,
  onOriginChange,
  onDestinationChange,
  onSearch
}: SearchFormProps) {
  const [originError, setOriginError] = useState<string | null>(null);
  const [destinationError, setDestinationError] = useState<string | null>(null);

  const validateIata = (code: string) => /^[A-Z]{3}$/.test(code);

  const handleOriginInput = (value: string) => {
    const clean = value.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3);
    onOriginChange(clean);
    setOriginError(clean && !validateIata(clean) ? 'IATA must have 3 letters (A–Z)' : null);
  };

  const handleDestinationInput = (value: string) => {
    const clean = value.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3);
    onDestinationChange(clean);
    setDestinationError(clean && !validateIata(clean) ? 'IATA must have 3 letters (A–Z)' : null);
  };

  const isSearchDisabled = loading || !validateIata(origin) || !validateIata(destination);

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Flight Route Weather</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <InputField
            label="Origin (IATA)"
            type="text"
            value={origin}
            onChange={handleOriginInput}
            placeholder="e.g., JFK"
          />
          {originError && <p className="text-sm text-red-500 mt-1">{originError}</p>}
        </div>

        <div>
          <InputField
            label="Destination (IATA)"
            type="text"
            value={destination}
            onChange={handleDestinationInput}
            placeholder="e.g., LAX"
          />
          {destinationError && <p className="text-sm text-red-500 mt-1">{destinationError}</p>}
        </div>

        <div className="flex items-end">
          <button
            onClick={onSearch}
            disabled={isSearchDisabled}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading...' : 'Get Weather'}
          </button>
        </div>
      </div>
    </div>
  );
}