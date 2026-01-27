import ProgressBar from './ProgressBar';

interface PerformanceMetric {
  label: string;
  value: number;
  color?: string;
}

interface PerformanceChartProps {
  title: string;
  metrics: PerformanceMetric[];
}

export default function PerformanceChart({ title, metrics }: PerformanceChartProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
      <div className="space-y-4">
        {metrics.map((metric, index) => (
          <ProgressBar
            key={index}
            label={metric.label}
            value={metric.value}
            color={metric.color}
          />
        ))}
      </div>
    </div>
  );
}