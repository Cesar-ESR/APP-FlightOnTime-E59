import { Cloud, Sun, CloudRain, AlertTriangle } from 'lucide-react';

interface WeatherCardProps {
  title: string;
  description: string;
  color: 'blue' | 'green' | 'yellow' | 'orange' | 'red';
}

export default function WeatherCard({ title, description, color }: WeatherCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-800',
    green: 'bg-green-50 text-green-800',
    yellow: 'bg-yellow-50 text-yellow-800',
    orange: 'bg-orange-50 text-orange-800',
    red: 'bg-red-50 text-red-800'
  };

  const textColorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    orange: 'text-orange-600',
    red: 'text-red-600'
  };

  const getWeatherIcon = () => {
    if (title.includes('Clear')) return <Sun className="w-5 h-5" />;
    if (title.includes('cloudy')) return <Cloud className="w-5 h-5" />;
    if (title.includes('Impact')) return <AlertTriangle className="w-5 h-5" />;
    return <CloudRain className="w-5 h-5" />;
  };

  return (
    <div className={`p-4 rounded-lg ${colorClasses[color]}`}>
      <div className="flex items-center gap-2 mb-1">
        <div className={textColorClasses[color]}>
          {getWeatherIcon()}
        </div>
        <h3 className="font-medium">{title.replace(/[▲▼]/g, '').trim()}</h3>
      </div>
      <p className={`text-sm ${textColorClasses[color]}`}>{description}</p>
    </div>
  );
}