import StatusBadge from './StatusBadge';

interface Flight {
  id: string;
  route: string;
  date: string;
  status: 'On Time' | 'Delayed' | 'Cancelled';
  delay: string;
}

interface FlightTableProps {
  flights: Flight[];
  title?: string;
}

export default function FlightTable({ flights, title = "Flight Records" }: FlightTableProps) {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Flight ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Route
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Delay
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {flights.map((flight) => (
              <tr key={flight.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {flight.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {flight.route}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {flight.date}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge status={flight.status} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {flight.delay}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}