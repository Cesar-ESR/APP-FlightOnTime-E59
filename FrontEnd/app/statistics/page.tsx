'use client';

import DashboardLayout from '../components/DashboardLayout';
import { ExternalLink, Map, Zap, TrendingUp } from 'lucide-react';
import TitlePage from '../components/TitlePage';

export default function Statistics() {
  const cards = [
    {
      id: 1,
      title: 'Mapa 3D de Rutas Aéreas',
      description: 'Visualización interactiva de probabilidades de retraso por ruta',
      buttonText: 'Abrir 3D Routes Map',
      href: 'https://retrasosvuelos40-gmlvzsuujjty5epk5ydbzs.streamlit.app/ROI_Calculator',
      icon: Map,
      bgGradient: 'from-blue-600 to-blue-900',
      bgImage: 'url("data:image/svg+xml,%3Csvg width="100" height="100" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3ClinearGradient id="grad"%3E%3Cstop offset="0%25" style="stop-color:rgba(59,130,246,0.1)"%3E%3C/stop%3E%3Cstop offset="100%25" style="stop-color:rgba(59,130,246,0.05)"%3E%3C/stop%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="100" height="100" fill="url(%23grad)"%3E%3C/rect%3E%3C/svg%3E")'
    },
    {
      id: 2,
      title: 'Predictive Simulator',
      description: 'Prueba el modelo de predicción en tiempo real',
      buttonText: 'Abrir Predictive Simulator',
      href: 'https://retrasosvuelos40-gmlvzsuujjty5epk5ydbzs.streamlit.app/Predictive_Simulator',
      icon: Zap,
      bgGradient: 'from-purple-600 to-purple-900',
      bgImage: 'url("data:image/svg+xml,%3Csvg width="100" height="100" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3ClinearGradient id="grad2"%3E%3Cstop offset="0%25" style="stop-color:rgba(147,51,234,0.1)"%3E%3C/stop%3E%3Cstop offset="100%25" style="stop-color:rgba(147,51,234,0.05)"%3E%3C/stop%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="100" height="100" fill="url(%23grad2)"%3E%3C/rect%3E%3C/svg%3E")'
    },
    {
      id: 3,
      title: 'ROI Calculator',
      description: 'Calculadora de Retorno de Inversión del Sistema FlightOnTime',
      buttonText: 'Abrir ROI Calculator',
      href: 'https://retrasosvuelos40-gmlvzsuujjty5epk5ydbzs.streamlit.app/ROI_Calculator',
      icon: TrendingUp,
      bgGradient: 'from-emerald-600 to-emerald-900',
      bgImage: 'url("data:image/svg+xml,%3Csvg width="100" height="100" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3ClinearGradient id="grad3"%3E%3Cstop offset="0%25" style="stop-color:rgba(5,150,105,0.1)"%3E%3C/stop%3E%3Cstop offset="100%25" style="stop-color:rgba(5,150,105,0.05)"%3E%3C/stop%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width="100" height="100" fill="url(%23grad3)"%3E%3C/rect%3E%3C/svg%3E")'
    }
  ];

  return (
    <DashboardLayout>
      <div className="w-full">
      <div className="mb-10">        
        <TitlePage title="Flight Statistics" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.id}
                className={`group relative overflow-hidden rounded-xl shadow-lg transition-all duration-300 hover:shadow-2xl hover:scale-105 bg-gradient-to-br ${card.bgGradient}`}
              >
                {/* Fondo con patrón */}
                <div
                  className="absolute inset-0 opacity-20"
                  style={{
                    backgroundImage: card.bgImage,
                    backgroundSize: '100px 100px',
                    backgroundRepeat: 'repeat'
                  }}
                />

                {/* Overlay oscuro */}
                <div className="absolute inset-0 bg-black opacity-40 group-hover:opacity-30 transition-opacity" />

                {/* Contenido */}
                <div className="relative h-full p-8 flex flex-col justify-between min-h-80">
                  {/* Header con icono */}
                  <div className="flex items-start justify-between mb-4">
                    <Icon className="w-12 h-12 text-white opacity-80" />
                    <ExternalLink className="w-5 h-5 text-white opacity-60" />
                  </div>

                  {/* Texto */}
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-white mb-3">
                      {card.title}
                    </h2>
                    <p className="text-gray-100 text-sm leading-relaxed">
                      {card.description}
                    </p>
                  </div>

                  {/* Botón */}
                  <a
                    href={card.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-6 inline-flex items-center justify-center px-4 py-3 bg-white text-gray-900 font-semibold rounded-lg transition-all duration-300 hover:bg-gray-100 group/btn"
                  >
                    {card.buttonText}
                    <ExternalLink className="ml-2 w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                  </a>
                </div>

                {/* Efecto de brillo en hover */}
                <div className="absolute -inset-1 bg-gradient-to-r from-white via-transparent to-white opacity-0 group-hover:opacity-20 blur-xl transition-opacity pointer-events-none" />
              </div>
            );
          })}
        </div>
      </div>
    </DashboardLayout>
  );
}