import { TrendingUp, TrendingDown } from 'lucide-react';

interface Factor {
  name: string;
  value: number; // percentage, positive or negative
}

interface FactorsChartProps {
  factors: Factor[];
}

export default function FactorsChart({ factors }: FactorsChartProps) {
  // Find max absolute value for scaling
  const maxValue = Math.max(...factors.map(f => Math.abs(f.value)), 1);

  return (
    <div className="space-y-4">
      {factors.map((factor, index) => {
        const isPositive = factor.value > 0;
        const percentage = (Math.abs(factor.value) / maxValue) * 100;
        const barColor = isPositive ? 'bg-gradient-to-r from-red-400 to-red-500' : 'bg-gradient-to-r from-green-400 to-green-500';
        const labelColor = isPositive ? 'text-red-600' : 'text-green-600';
        const bgColor = isPositive ? 'bg-red-50' : 'bg-green-50';
        const borderColor = isPositive ? 'border-red-200' : 'border-green-200';

        return (
          <div key={index} className={`flex items-center gap-4 p-3 rounded-lg ${bgColor} border ${borderColor} transition-all hover:shadow-md`}>
            {/* Icon and Factor Name */}
            <div className="w-44 flex items-center gap-2">
              <div className={`p-2 rounded-lg ${isPositive ? 'bg-red-100' : 'bg-green-100'}`}>
                {isPositive ? (
                  <TrendingUp className={`w-4 h-4 ${labelColor}`} />
                ) : (
                  <TrendingDown className={`w-4 h-4 ${labelColor}`} />
                )}
              </div>
              <span className="text-sm font-medium text-gray-700 truncate">
                {factor.name}
              </span>
            </div>

            {/* Bar Container */}
            <div className="flex-1 flex items-center gap-3">
              <div className="flex-1 h-8 bg-gray-200 rounded-full overflow-hidden relative">
                <div
                  className={`h-full ${barColor} transition-all duration-500 shadow-md`}
                  style={{ width: `${percentage}%` }}
                />
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20" />
              </div>
            </div>

            {/* Value Badge */}
            <div className={`px-4 py-2 rounded-lg font-bold text-sm ${isPositive ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
              {isPositive ? '+' : ''}{factor.value}%
            </div>
          </div>
        );
      })}

      {/* Legend */}
      <div className="mt-8 p-5 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl border border-gray-200">
        <p className="text-xs font-bold text-gray-600 uppercase tracking-wide mb-3">Leyenda</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <TrendingUp className="w-4 h-4 text-red-600" />
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-700">Factor Positivo</p>
              <p className="text-xs text-gray-500">Aumenta probabilidad de retraso</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingDown className="w-4 h-4 text-green-600" />
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-700">Factor Negativo</p>
              <p className="text-xs text-gray-500">Disminuye probabilidad de retraso</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
