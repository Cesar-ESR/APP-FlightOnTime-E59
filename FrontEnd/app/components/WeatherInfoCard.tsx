import Image from 'next/image';
import { Droplets, Wind, Gauge } from 'lucide-react';

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

interface WeatherInfoCardProps {
  title: string;
  weatherInfo: WeatherInfo;
}

function getWeatherIcon(condition: string): string {
  const conditionLower = condition.toLowerCase();
  if (conditionLower.includes('sunny')) return '/assets/weather/sunny.svg';
  if (conditionLower.includes('cloudy')) return '/assets/weather/cloudy.svg';
  if (conditionLower.includes('partly')) return '/assets/weather/partly-cloudy.svg';
  if (conditionLower.includes('heavy rain')) return '/assets/weather/heavy-rain.svg';
  if (conditionLower.includes('rain')) return '/assets/weather/rain.svg';
  if (conditionLower.includes('snow')) return '/assets/weather/snow.svg';
  if (conditionLower.includes('thunderstorm')) return '/assets/weather/thunderstorm.svg';
  if (conditionLower.includes('haze')) return '/assets/weather/haze.svg';
  if (conditionLower.includes('sleet')) return '/assets/weather/sleet.svg';
  if (conditionLower.includes('windy')) return '/assets/weather/windy.svg';
  return '/assets/weather/sunny.svg';
}

function isDayTime(localtime: string | undefined): boolean {
  if (!localtime) return true;
  const parsedDate = new Date(localtime);
  if (!Number.isNaN(parsedDate.getTime())) {
    const hour = parsedDate.getHours();
    return hour >= 6 && hour < 18;
  }
  const timePart = localtime.split(' ')[1] ?? localtime;
  const hour = parseInt(timePart.split(':')[0] || '12', 10);
  return hour >= 6 && hour < 18;
}

function getBackgroundStyle(isDayTime: boolean) {
  const bgImage = isDayTime
    ? 'url("data:image/svg+xml,%3Csvg width="100" height="100" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3ClinearGradient id="dayGrad"%3E%3Cstop offset="0%25" style="stop-color:rgba(251,191,36,0.1)"%3E%3C/stop%3E%3Cstop offset="100%25" style="stop-color:rgba(251,146,60,0.05)"%3E%3C/stop%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="100" height="100" fill="url(%23dayGrad)"%3E%3C/rect%3E%3C/svg%3E")'
    : 'url("data:image/svg+xml,%3Csvg width="100" height="100" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3ClinearGradient id="nightGrad"%3E%3Cstop offset="0%25" style="stop-color:rgba(33, 39, 49, 0.1)"%3E%3C/stop%3E%3Cstop offset="100%25" style="stop-color:rgba(17,24,39,0.05)"%3E%3C/stop%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="100" height="100" fill="url(%23nightGrad)"%3E%3C/rect%3E%3C/svg%3E")';
  
  return {
    backgroundImage: bgImage,
    backgroundSize: '100px 100px',
    backgroundRepeat: 'repeat'
  };
}

export default function WeatherInfoCard({ title, weatherInfo }: WeatherInfoCardProps) {
  const isDay = isDayTime(weatherInfo.lastUpdated);
  const dayGradient = 'from-yellow-100 to-orange-400';
  const nightGradient = 'from-gray-700 to-gray-900';
  const gradient = isDay ? dayGradient : nightGradient;
  const textColor = isDay ? 'text-gray-900' : 'text-white';
  const secondaryTextColor = isDay ? 'text-gray-700' : 'text-gray-200';
  const accentColor = isDay ? 'text-amber-700' : 'text-blue-300';
  const conditionText = weatherInfo.condition || 'Weather data unavailable';
  const pressureValue = weatherInfo.pressure;
  const pressureLabel = pressureValue ?? 'No disponible';
  
  return (
    <div className={`group relative overflow-hidden rounded-lg shadow-lg transition-all duration-300 hover:shadow-2xl hover:scale-105 bg-gradient-to-br ${gradient}`}>
      {/* Fondo con patrón */}
      <div
        className="absolute inset-0 opacity-20"
        style={getBackgroundStyle(isDay)}
      />

      {/* Overlay oscuro/claro */}
      <div className={`absolute inset-0 ${isDay ? 'bg-white opacity-10' : 'bg-black opacity-30'} group-hover:opacity-5 transition-opacity`} />

      {/* Contenido */}
      <div className="relative p-6">
        {/* Header */}
        <div className="mb-4">
          <h3 className={`text-xl font-semibold ${accentColor}`}>{title}: {weatherInfo.iataCode} - {weatherInfo.airportName}</h3>
          <div className={`text-md font-semibold ${secondaryTextColor} mt-1`}> {weatherInfo.city} - {weatherInfo.country} </div>
          {weatherInfo.lastUpdated && (
            <div className={`text-sm ${isDay ? 'text-gray-600' : 'text-gray-300'}`}>{weatherInfo.lastUpdated}Hs</div>
          )}
        </div>
        
        <div className="grid grid-cols-2 gap-6">
          {/* Left Column - Main Temperature Section */}
          <div className="flex items-center justify-center">
            {weatherInfo.conditionIcon ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={weatherInfo.conditionIcon!.startsWith('//') ? `https:${weatherInfo.conditionIcon!}` : weatherInfo.conditionIcon!}
                alt={conditionText}
                width={80}
                height={80}
                className="mr-4"
              />
            ) : (
              <Image
                src={getWeatherIcon(conditionText)}
                alt={conditionText}
                width={80}
                height={80}
                className="mr-4"
              />
            )}

            <div>
              <div className={`text-6xl font-light ${accentColor}`}>
                {weatherInfo.temperature}°C
              </div>
              <div className={`text-lg capitalize ${secondaryTextColor}`}>
                {conditionText.toLowerCase()}
              </div>
            </div>
          </div>
          
          {/* Right Column - Weather Details */}
          <div className="space-y-3 flex flex-col justify-center items-center">
            <div className={`flex items-center ${isDay ? 'text-gray-700' : 'text-gray-300'}`}>
              <Droplets className={`w-4 h-4 mr-2 ${isDay ? 'text-orange-600' : 'text-blue-400'}`} />
              <span className="text-sm mr-2">Humidity</span>
              <span className={`text-sm font-medium ${accentColor}`}>{weatherInfo.humidity}%</span>
            </div>
            
            <div className={`flex items-center ${isDay ? 'text-gray-700' : 'text-gray-300'}`}>
              <Wind className={`w-4 h-4 mr-2 ${isDay ? 'text-orange-600' : 'text-blue-400'}`} />
              <span className="text-sm mr-2">Wind</span>
              <span className={`text-sm font-medium ${accentColor}`}>{weatherInfo.windSpeed} kph</span>
            </div>
            
            <div className={`flex items-center ${isDay ? 'text-gray-700' : 'text-gray-300'}`}>
              <Gauge className={`w-4 h-4 mr-2 ${isDay ? 'text-orange-600' : 'text-blue-400'}`} />
              <span className="text-sm mr-2">Pressure</span>
              <span className={`text-sm font-medium ${accentColor}`}>
                {pressureLabel}
                {pressureValue != null ? ' hPa' : ''}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Efecto de brillo en hover */}
      <div className={`absolute -inset-1 bg-gradient-to-r ${isDay ? 'from-yellow-200 via-transparent to-yellow-200' : 'from-white via-transparent to-white'} opacity-0 group-hover:opacity-20 blur-xl transition-opacity pointer-events-none`} />
    </div>
  );
}
