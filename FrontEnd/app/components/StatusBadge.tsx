interface StatusBadgeProps {
  status: 'On Time' | 'Delayed' | 'Cancelled';
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const getStatusStyles = () => {
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

  return (
    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusStyles()}`}>
      {status}
    </span>
  );
}