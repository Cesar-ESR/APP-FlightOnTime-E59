'use client';

import { useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import SearchForm from '../components/SearchForm';
import WeatherInfoCard from '../components/WeatherInfoCard';
import WeatherCard from '../components/WeatherCard';
import TitlePage from '../components/TitlePage';

interface WeatherInfo {
  iataCode: string;
  airportName: string;
  city: string;
  country: string;
  temperature: number;
  humidity: number;
  windSpeed: number;
  pressure?: number | null;
  condition: string;
  conditionIcon?: string;
  lastUpdated?: string;
}

interface WeatherData {
  origin: WeatherInfo;
  destination: WeatherInfo;
}

export default function Weather() {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Backend payload shape (support current and legacy variants)
  interface AirportWeather {
    iata?: string;
    iataCode?: string;
    airportName?: string;
    cityName?: string;
    country?: string;
    temperatureCelsius?: number;
    humidityPercentage?: number;
    windSpeedKmh?: number;
    pressure?: number;
    condition?: {
      text?: string;
      icon?: string;
      code?: number;
    };
    lastUpdated?: string;
    measurementTime?: string;
    weatherSummary?: string;
    data?: {
      cityName?: string;
      latitude?: number;
      longitude?: number;
      measurementTime?: string;
      temperatureCelsius?: number;
      humidityPercentage?: number;
      windSpeedKmh?: number;
      country?: string;
      favorableForFlights?: boolean;
      weatherSummary?: string;
      pressure?: number;
      condition?: {
        text?: string;
        icon?: string;
        code?: number;
      };
      lastUpdated?: string;
      airportName?: string;
    };
  }

  const fetchWeather = async (iata: string): Promise<AirportWeather> => {
    const res = await fetch(`/weather/${iata}`);
    if (!res.ok) throw new Error(`Failed to fetch weather for ${iata}: ${res.status}`);
    return res.json();
  };

  function mapToWeatherInfo(payload: AirportWeather, fallbackIata: string): WeatherInfo {
    const details = payload.data ?? payload;
    const cityName = details?.cityName ?? 'Unknown';
    const airportName = details?.airportName ?? cityName;
    const iataCode = payload.iata ?? payload.iataCode ?? fallbackIata;
    const conditionText =
      details?.weatherSummary ??
      details?.condition?.text ??
      payload.condition?.text ??
      'Weather data unavailable';
    const conditionIcon = details?.condition?.icon ?? payload.condition?.icon;
    return {
      iataCode,
      airportName,
      city: cityName,
      country: details?.country ?? payload.country ?? 'Unknown',
      temperature: Math.round(details?.temperatureCelsius ?? 0),
      humidity: details?.humidityPercentage ?? 0,
      windSpeed: Math.round(details?.windSpeedKmh ?? 0),
      pressure: details?.pressure ?? payload.pressure ?? null,
      condition: conditionText,
      conditionIcon,
      lastUpdated: details?.measurementTime ?? details?.lastUpdated ?? payload.lastUpdated,
    };
  }

  const handleSearch = async () => {
    if (!origin || !destination) return;

    setLoading(true);
    setError(null);

    try {
      const [originResp, destResp] = await Promise.all([
        fetchWeather(origin),
        fetchWeather(destination)
      ]);

      setWeatherData({
        origin: mapToWeatherInfo(originResp, origin),
        destination: mapToWeatherInfo(destResp, destination)
      });
    } catch (err) {
      console.error(err);
      setError('No se pudo obtener el clima. Verifica los códigos IATA y el backend.');
      setWeatherData(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="w-full">
        <div className="mb-10">
          <TitlePage title="Weather Conditions" />
        </div>

        <SearchForm
          origin={origin}
          destination={destination}
          loading={loading}
          onOriginChange={setOrigin}
          onDestinationChange={setDestination}
          onSearch={handleSearch}
        />

        {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>}

        {/* Weather Results */}
        {weatherData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <WeatherInfoCard
              title="Origin"
              weatherInfo={weatherData.origin}
            />
            <WeatherInfoCard
              title="Destination"
              weatherInfo={weatherData.destination}
            />
          </div>
        )}

        {/* Flight Impact Analysis */}
        {weatherData && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Flight Impact Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <WeatherCard
                title="Route Conditions"
                description={`${weatherData.origin.city} → ${weatherData.destination.city}`}
                color="blue"
              />
              <WeatherCard
                title="Weather Status"
                description="Conditions are suitable for flight operations"
                color="green"
              />
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
