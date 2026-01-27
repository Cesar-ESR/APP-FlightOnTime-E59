interface ProgressBarProps {
  label: string;
  value: number;
  color?: string;
  showPercentage?: boolean;
}

export default function ProgressBar({ 
  label, 
  value, 
  color = "bg-blue-600", 
  showPercentage = true 
}: ProgressBarProps) {
  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-sm text-gray-600">{label}</span>
        {showPercentage && (
          <span className="text-sm font-medium text-gray-400">{value}%</span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`${color} h-2 rounded-full`} 
          style={{width: `${value}%`}}
        ></div>
      </div>
    </div>
  );
}