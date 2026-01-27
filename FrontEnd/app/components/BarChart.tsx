interface BarData {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  title: string;
  data: BarData[];
  maxValue?: number;
}

export default function BarChart({ title, data, maxValue }: BarChartProps) {
  const max = maxValue || Math.max(...data.map(d => d.value));
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
      <div className="space-y-4">
        {data.map((item, index) => (
          <div key={index} className="flex items-center space-x-3">
            <div className="w-20 text-sm text-gray-600 text-right">
              {item.label}
            </div>
            <div className="flex-1 flex items-center space-x-2">
              <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                <div 
                  className={`${item.color || 'bg-blue-500'} h-6 rounded-full flex items-center justify-end pr-2`}
                  style={{width: `${(item.value / max) * 100}%`}}
                >
                  <span className="text-xs text-white font-medium">{item.value}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}