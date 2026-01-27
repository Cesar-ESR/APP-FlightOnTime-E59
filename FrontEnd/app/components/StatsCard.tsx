interface StatItem {
  label: string;
  value: string;
  valueColor?: string;
}

interface StatsCardProps {
  title: string;
  stats: StatItem[];
}

export default function StatsCard({ title, stats }: StatsCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      <div className="space-y-3">
        {stats.map((stat, index) => (
          <div key={index} className="flex justify-between items-center">
            <span className="text-gray-600">{stat.label}</span>
            <span className={`font-medium ${stat.valueColor || 'text-gray-400'}`}>
              {stat.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}