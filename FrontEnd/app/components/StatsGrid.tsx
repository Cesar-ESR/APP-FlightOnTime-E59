import StatsCard from './StatsCard';

interface StatItem {
  label: string;
  value: string;
  valueColor?: string;
}

interface StatsSection {
  title: string;
  stats: StatItem[];
}

interface StatsGridProps {
  sections: StatsSection[];
  columns?: 1 | 2 | 3 | 4;
}

export default function StatsGrid({ sections, columns = 2 }: StatsGridProps) {
  const getGridCols = () => {
    switch (columns) {
      case 1: return 'grid-cols-1';
      case 2: return 'grid-cols-1 md:grid-cols-2';
      case 3: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
      case 4: return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4';
      default: return 'grid-cols-1 md:grid-cols-2';
    }
  };

  return (
    <div className={`grid ${getGridCols()} gap-6`}>
      {sections.map((section, index) => (
        <StatsCard
          key={index}
          title={section.title}
          stats={section.stats}
        />
      ))}
    </div>
  );
}