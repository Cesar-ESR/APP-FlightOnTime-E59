interface PieData {
  label: string;
  value: number;
  color: string;
}

interface PieChartProps {
  title: string;
  data: PieData[];
}

export default function PieChart({ title, data }: PieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
      <div className="flex items-center space-x-6">
        <div className="relative w-32 h-32">
          <div className="w-32 h-32 rounded-full overflow-hidden">
            {data.map((item, index) => {
              const percentage = (item.value / total) * 100;
              const rotation = data.slice(0, index).reduce((sum, prev) => sum + (prev.value / total) * 360, 0);
              
              return (
                <div
                  key={index}
                  className="absolute w-full h-full"
                  style={{
                    background: `conic-gradient(from ${rotation}deg, ${item.color} 0deg, ${item.color} ${percentage * 3.6}deg, transparent ${percentage * 3.6}deg)`,
                  }}
                />
              );
            })}
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center border-2 border-gray-100">
              <span className="text-sm font-semibold text-gray-700">{total}</span>
            </div>
          </div>
        </div>
        
        <div className="flex-1 space-y-2">
          {data.map((item, index) => (
            <div key={index} className="flex items-center space-x-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{backgroundColor: item.color}}
              />
              <span className="text-sm text-gray-600">{item.label}</span>
              <span className="text-sm font-medium text-gray-800">
                {item.value} ({((item.value / total) * 100).toFixed(1)}%)
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}