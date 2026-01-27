import { Plane, Clock, X } from 'lucide-react';

interface FlightCardProps {
  id: string;
  route: string;
  status: 'On Time' | 'Delayed' | 'Cancelled';
  delay: string;
}

export default function FlightCard({ id, route, status, delay }: FlightCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'On Time':
        return 'bg-green-100 text-green-800';
      case 'Delayed':
        return 'bg-yellow-100 text-yellow-800';
      case 'Cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'On Time':
        return <Plane className="w-4 h-4" />;
      case 'Delayed':
        return <Clock className="w-4 h-4" />;
      case 'Cancelled':
        return <X className="w-4 h-4" />;
      default:
        return <Plane className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex justify-between items-center p-3 bg-gray-100 rounded">
      <div>
        <span className="font-medium text-gray-900">{id}</span>
        <p className="text-sm text-gray-600">{route}</p>
      </div>
      <div className="text-right">
        <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(status)}`}>
          {getStatusIcon()}
          {status}
        </span>
        <p className="text-sm text-gray-500">{delay}</p>
      </div>
    </div>
  );
}