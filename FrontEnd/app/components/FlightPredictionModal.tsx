import { X, AlertCircle, CheckCircle, TrendingUp, Plane, Calendar, Clock, Briefcase} from 'lucide-react';
import GaugeChart from './GaugeChart';


interface Factor {
  name: string;
  value: number; // percentage, positive or negative
  icon?: React.ReactNode;
}

interface FlightPredictionModalProps {
  isOpen: boolean;
  onClose: () => void;
  prediction: 'on-time' | 'delayed';
  probability: number; // 0-100
  confidence: 'low' | 'medium' | 'high';
  factors: Factor[];
  origin?: string;
  destination?: string;
  airline?: string;
  departureDate?: string;
  departureTime?: string;
}

function getConfidenceColor(confidence: 'low' | 'medium' | 'high'): string {
  switch (confidence) {
    case 'low':
      return 'from-orange-500 to-orange-600';
    case 'medium':
      return 'from-yellow-500 to-yellow-600';
    case 'high':
      return 'from-green-500 to-green-600';
  }
}

function getConfidenceIcon(confidence: 'low' | 'medium' | 'high'): React.ReactNode {
  switch (confidence) {
    case 'low':
      return <AlertCircle className="w-5 h-5" />;
    case 'medium':
      return <TrendingUp className="w-5 h-5" />;
    case 'high':
      return <CheckCircle className="w-5 h-5" />;
  }
}

function getConfidenceLabel(confidence: 'low' | 'medium' | 'high'): string {
  switch (confidence) {
    case 'low':
      return 'Baja';
    case 'medium':
      return 'Media';
    case 'high':
      return 'Alta';
  }
}

function getPredictionColor(prediction: 'on-time' | 'delayed'): string {
  return prediction === 'on-time'
    ? 'from-green-500 to-emerald-600'
    : 'from-red-500 to-red-600';
}

function getPredictionIcon(prediction: 'on-time' | 'delayed'): React.ReactNode {
  return prediction === 'on-time' 
    ? <CheckCircle className="w-6 h-6" />
    : <AlertCircle className="w-6 h-6" />;
}

function getPredictionLabel(prediction: 'on-time' | 'delayed'): string {
  return prediction === 'on-time' ? 'Puntual' : 'Retrasada';
}

export default function FlightPredictionModal({
  isOpen,
  onClose,
  prediction,
  probability,
  confidence,
  origin,
  destination,
  airline,
  departureDate,
  departureTime
}: FlightPredictionModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header con Gradient */}
        <div className={`bg-gradient-to-r ${getPredictionColor(prediction)} p-8 relative overflow-hidden`}>
          <div className="absolute inset-0 opacity-10">
            <Plane className="absolute top-2 right-4 w-32 h-32 text-white" />
          </div>
          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-white bg-opacity-20 rounded-full backdrop-blur-sm">
                {getPredictionIcon(prediction)}
              </div>
              <div>
                <p className="text-white text-sm font-medium opacity-90">Resultado de la Predicción</p>
                <h2 className="text-3xl font-bold text-white">{getPredictionLabel(prediction)}</h2>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white hover:bg-opacity-20  hover:text-black p-2 rounded-full transition-all"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8">
          {/* Flight Details Section */}
          {(origin || destination || airline || departureDate || departureTime) && (
            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-6 border-2 border-indigo-200">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Plane className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-800">Detalles del Vuelo</h3>
                  <p className="text-xs text-gray-500 mt-1">Información de búsqueda</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {/* Origin and Destination */}
                {(origin || destination) && (
                  <div className="flex items-center justify-center md:col-span-1 lg:col-span-2">
                    <div className="flex items-center gap-2">
                      <div className="text-center">
                        <div className="text-sm text-gray-600 mb-1">Origen</div>
                        <div className="text-2xl font-bold text-indigo-600">{origin || '-'}</div>
                      </div>
                      <div className="text-2xl text-gray-400">→</div>
                      <div className="text-center">
                        <div className="text-sm text-gray-600 mb-1">Destino</div>
                        <div className="text-2xl font-bold text-indigo-600">{destination || '-'}</div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Airline */}
                {airline && (
                  <div className="flex flex-col items-center justify-center bg-white rounded-lg p-3 border border-indigo-100">
                    <Briefcase className="w-4 h-4 text-indigo-600 mb-2" />
                    <div className="text-xs text-gray-600 text-center">Aerolínea</div>
                    <div className="text-lg font-bold text-indigo-600 mt-1">{airline}</div>
                  </div>
                )}
                
                {/* Date */}
                {departureDate && (
                  <div className="flex flex-col items-center justify-center bg-white rounded-lg p-3 border border-indigo-100">
                    <Calendar className="w-4 h-4 text-indigo-600 mb-2" />
                    <div className="text-xs text-gray-600 text-center">Fecha</div>
                    <div className="text-sm font-bold text-indigo-600 mt-1">
                      {new Date(departureDate).toLocaleDateString('es-ES')}
                    </div>
                  </div>
                )}
                
                {/* Time */}
                {departureTime && (
                  <div className="flex flex-col items-center justify-center bg-white rounded-lg p-3 border border-indigo-100">
                    <Clock className="w-4 h-4 text-indigo-600 mb-2" />
                    <div className="text-xs text-gray-600 text-center">Hora</div>
                    <div className="text-lg font-bold text-indigo-600 mt-1">{departureTime}</div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Top Row: Main Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Probability Gauge - Left */}
            <div className="flex flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
              <div className="text-center">
                <p className="text-sm font-semibold text-gray-700 mb-4 flex items-center justify-center gap-2">
                  <TrendingUp className="w-4 h-4 text-blue-600" />
                  Probabilidad de Retraso
                </p>
                <GaugeChart probability={probability} />
              </div>
            </div>

            {/* Confidence Badge - Right */}
            <div className="flex flex-col justify-center gap-4">
              <div className={`bg-gradient-to-r ${getConfidenceColor(confidence)} rounded-xl p-6 text-white shadow-lg`}>
                <div className="flex items-center gap-3 mb-2">
                  {getConfidenceIcon(confidence)}
                  <p className="text-sm font-medium opacity-90">Nivel de Confianza</p>
                </div>
                <p className="text-3xl font-bold">{getConfidenceLabel(confidence)}</p>
                <p className="text-sm opacity-80 mt-2">
                  {confidence === 'high' && 'Predicción muy confiable'}
                  {confidence === 'medium' && 'Predicción moderadamente confiable'}
                  {confidence === 'low' && 'Predicción con baja confiabilidad'}
                </p>
              </div>

              {/* Summary Card */}
              <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200">
                <p className="text-xs text-gray-600 font-semibold uppercase tracking-wide">Resumen</p>
                <p className="text-sm text-gray-700 mt-2 leading-relaxed">
                  {probability > 70
                    ? 'Alta probabilidad de retraso basada en los factores analizados.'
                    : probability > 40
                      ? 'Probabilidad moderada de retraso. Factores neutrales detectados.'
                      : 'Baja probabilidad de retraso. Condiciones favorables.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
