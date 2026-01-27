interface GaugeChartProps {
  probability: number; // 0-100
}

export default function GaugeChart({ probability }: GaugeChartProps) {
  // Asegurar que la probabilidad esté entre 0 y 100
  const normalizedProbability = Math.max(0, Math.min(100, probability));
  
  // Cálculo del ángulo de rotación (0% = -90deg, 100% = 90deg)
  const rotation = (normalizedProbability / 100) * 180 - 90;

  // Determinación de colores según riesgo
  let color = '#10b981'; // verde
  let colorClass = 'text-green-600';
  if (normalizedProbability > 70) {
    color = '#ef4444'; // rojo
    colorClass = 'text-red-600';
  } else if (normalizedProbability > 40) {
    color = '#f59e0b'; // ámbar
    colorClass = 'text-amber-600';
  }

  // Configuración del trazo (basado en un radio de 60 para el arco)
  const radius = 60;
  const circumference = Math.PI * radius; // Semicírculo
  const strokeDashoffset = circumference - (normalizedProbability / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-4">
      {/* Contenedor principal: Aumentado de w-48 a w-[450px] para mayor impacto */}
      <div className="relative w-full max-w-[450px] h-auto">
        <svg 
          viewBox="0 0 200 150" 
          className="w-full h-full mx-auto -mt-14"
          style={{ overflow: 'visible' }}
        >
          {/* Definición de Gradiente */}
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="50%" stopColor="#f59e0b" />
              <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>
          </defs>

          {/* Arco de fondo (Gris) */}
          <path
            d="M 30 120 A 70 70 0 0 1 170 120"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Arco de progreso (Color/Gradiente) */}
          <path
            d="M 30 120 A 70 70 0 0 1 170 120"
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray="220" /* Valor aproximado para el arco de 70 de radio */
            strokeDashoffset={220 - (normalizedProbability / 100) * 220}
            className="transition-all duration-700 ease-out"
            style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))' }}
          />

          {/* Círculo central (Eje de la aguja) */}
          <circle cx="100" cy="120" r="6" fill="white" stroke={color} strokeWidth="3" />

          {/* Aguja (Needle) */}
          <g transform={`rotate(${rotation} 100 120)`} className="transition-transform duration-700 ease-out">
            <line
              x1="100"
              y1="120"
              x2="100"
              y2="40"
              stroke={color}
              strokeWidth="5"
              strokeLinecap="round"
              filter="drop-shadow(0 2px 4px rgba(0,0,0,0.2))"
            />
          </g>

          {/* Etiquetas de porcentaje */}
          <text x="25" y="145" fontSize="10" fill="#9ca3af" fontWeight="600" textAnchor="middle">0%</text>
          <text x="100" y="145" fontSize="10" fill="#9ca3af" fontWeight="600" textAnchor="middle">50%</text>
          <text x="175" y="145" fontSize="10" fill="#9ca3af" fontWeight="600" textAnchor="middle">100%</text>
        </svg>
      </div>

      {/* Información textual ampliada */}
      <div className="text-center mt-4">
        <div className={`text-4xl font-black ${colorClass} transition-colors duration-500 tracking-tighter`}>
          {Math.round(normalizedProbability)}%
        </div>
        <div className="text-md text-gray-600 mt-2 font-semibold">
          {normalizedProbability > 70
            ? 'Alto riesgo de retraso'
            : normalizedProbability > 40
              ? 'Riesgo moderado'
              : 'Bajo riesgo'}
        </div>
      </div>
    </div>
  );
}
