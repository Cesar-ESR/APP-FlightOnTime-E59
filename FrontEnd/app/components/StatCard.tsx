import { Plane, Clock, AlertTriangle, CloudRain } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle: string;
  color: 'blue' | 'green' | 'orange' | 'yellow' | 'red';
}

export default function StatCard({ title, value, subtitle, color }: StatCardProps) {
  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    orange: 'text-orange-600',
    yellow: 'text-yellow-600',
    red: 'text-red-600'
  };

  const getIcon = () => {
    if (title.includes('Flights')) return <Plane className="w-6 h-6" />;
    if (title.includes('Rate') || title.includes('Delay')) return <Clock className="w-6 h-6" />;
    if (title.includes('Weather') || title.includes('Alert')) return <CloudRain className="w-6 h-6" />;
    return <AlertTriangle className="w-6 h-6" />;
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <div className={colorClasses[color]}>
          {getIcon()}
        </div>
      </div>
      <p className={`text-3xl font-bold ${colorClasses[color]}`}>{value}</p>
      <p className="text-sm text-gray-500">{subtitle}</p>
    </div>
  );
}