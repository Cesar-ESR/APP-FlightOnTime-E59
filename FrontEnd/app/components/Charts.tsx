'use client';

import { BarChart } from '@mui/x-charts/BarChart';
import { PieChart } from '@mui/x-charts/PieChart';
import { LineChart } from '@mui/x-charts/LineChart';
import { Gauge } from '@mui/x-charts/Gauge';

interface ChartWrapperProps {
  title: string;
  children: React.ReactNode;
}

export function ChartWrapper({ title, children }: ChartWrapperProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      {children}
    </div>
  );
}

export function useChartTheme() {
  return {
    '& .MuiChartsAxis-tick': {
      stroke: '#000000',
    },
    '& .MuiChartsAxis-tickLabel': {
      fill: '#000000',
    },
    '& .MuiChartsAxis-line': {
      stroke: '#000000',
    },
    '& .MuiChartsAxis-label': {
      fill: '#000000',
    },
    '& .MuiChartsGrid-line': {
      stroke: '#e5e7eb',
    }
  };
}

export { BarChart, PieChart, LineChart, Gauge };