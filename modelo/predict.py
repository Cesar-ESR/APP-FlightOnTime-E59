"""
FlightOnTime - Predicción en Tiempo Real
=========================================
Script para realizar predicciones de retrasos de vuelos en tiempo real.

Uso:
    python predict.py

Autor: FlightOnTime Team
Fecha: 2026-01-13
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import joblib
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configuración
MODEL_PATH = Path("models/model.joblib")
METADATA_PATH = Path("models/metadata.json")
FEATURE_ENGINEER_PATH = Path("models/feature_engineer.joblib")


class FlightDelayPredictor:
    """Predictor de retrasos de vuelos en tiempo real."""
    
    def __init__(self):
        """Inicializa el predictor cargando el modelo y metadatos."""
        print("🔄 Cargando modelo entrenado...")
        
        # Cargar modelo
        self.model = joblib.load(MODEL_PATH)
        print(f"   ✅ Modelo cargado: {MODEL_PATH}")
        
        # Cargar metadata
        with open(METADATA_PATH, 'r') as f:
            self.metadata = json.load(f)
        print(f"   ✅ Metadatos cargados: {METADATA_PATH}")
        
        # Cargar feature engineer
        self.feature_engineer = joblib.load(FEATURE_ENGINEER_PATH)
        print(f"   ✅ Feature engineer cargado: {FEATURE_ENGINEER_PATH}")
        
        self.threshold = float(self.metadata['threshold'])
        self.features = self.metadata['feature_names']
        
        print(f"\n📊 Modelo: {self.metadata['model_name']}")
        print(f"📊 Umbral optimizado: {self.threshold:.4f}")
        print(f"📊 ROC-AUC: {self.metadata['metrics']['roc_auc']:.4f}")
        print(f"📊 Entrenado: {self.metadata['trained_at']}")
        
    def prepare_input(self, flight_data):
        """
        Prepara los datos de entrada para predicción.
        
        Args:
            flight_data (dict): Datos del vuelo
                {
                    'year': int,
                    'month': int,
                    'day_of_month': int,
                    'day_of_week': int,
                    'dep_hour': int,
                    'sched_minute_of_day': int,
                    'op_unique_carrier': str,
                    'origin': str,
                    'dest': str,
                    'distance': float,
                    'temp': float,
                    'wind_spd': float,
                    'precip_1h': float,
                    'climate_severity_idx': float,
                    'dist_met_km': float,
                    'latitude': float,
                    'longitude': float
                }
        
        Returns:
            pd.DataFrame: DataFrame con las features preparadas
        """
        df = pd.DataFrame([flight_data])
        
        # Si hay categóricas, transformarlas
        if hasattr(self.feature_engineer, 'label_encoders'):
            df = self.feature_engineer.transform_categorical(df)
        
        # Asegurarse de que tiene todas las features necesarias
        for feature in self.features:
            if feature not in df.columns:
                print(f"⚠️ Feature faltante: {feature}")
        
        return df[self.features]
    
    def predict(self, flight_data, return_proba=True):
        """
        Realiza una predicción de retraso.
        
        Args:
            flight_data (dict): Datos del vuelo
            return_proba (bool): Si True, retorna probabilidades
        
        Returns:
            dict: Resultado de la predicción
        """
        # Preparar datos
        X = self.prepare_input(flight_data)
        
        # Predecir probabilidad
        proba = self.model.predict_proba(X)[0, 1]
        
        # Predicción binaria usando el umbral optimizado
        prediction = 1 if proba >= self.threshold else 0
        label = "Retrasado" if prediction == 1 else "Puntual"
        
        result = {
            'prevision': label,
            'probabilidad': float(proba),
            'umbral_usado': self.threshold,
            'confianza': 'Alta' if abs(proba - 0.5) > 0.3 else 'Media' if abs(proba - 0.5) > 0.15 else 'Baja'
        }
        
        if return_proba:
            result['prob_puntual'] = float(1 - proba)
            result['prob_retrasado'] = float(proba)
        
        return result
    
    def predict_batch(self, flights_data):
        """
        Realiza predicciones para múltiples vuelos.
        
        Args:
            flights_data (list): Lista de diccionarios con datos de vuelos
        
        Returns:
            list: Lista de resultados de predicciones
        """
        results = []
        for i, flight in enumerate(flights_data):
            try:
                result = self.predict(flight)
                result['vuelo_id'] = i + 1
                results.append(result)
            except Exception as e:
                print(f"❌ Error en vuelo {i+1}: {str(e)}")
                results.append({
                    'vuelo_id': i + 1,
                    'error': str(e)
                })
        
        return results


def ejemplo_prediccion_simple():
    """Ejemplo de predicción simple."""
    print("\n" + "="*70)
    print("📝 EJEMPLO: PREDICCIÓN SIMPLE")
    print("="*70)
    
    # Inicializar predictor
    predictor = FlightDelayPredictor()
    
    # Datos de ejemplo (vuelo de AA de JFK a LAX)
    flight_data = {
        'year': 2024,
        'month': 3,
        'day_of_month': 15,
        'day_of_week': 5,  # Viernes
        'dep_hour': 14,
        'sched_minute_of_day': 870,  # 14:30
        'op_unique_carrier': 'AA',
        'origin': 'JFK',
        'dest': 'LAX',
        'distance': 2475.0,
        'temp': 25.5,
        'wind_spd': 15.3,
        'precip_1h': 0.0,
        'climate_severity_idx': 0.35,
        'dist_met_km': 12.5,
        'latitude': 40.6413,
        'longitude': -73.7781
    }
    
    # Realizar predicción
    print("\n📋 Datos del vuelo:")
    print(f"   Aerolínea: {flight_data['op_unique_carrier']}")
    print(f"   Ruta: {flight_data['origin']} → {flight_data['dest']}")
    print(f"   Fecha: 2024-{flight_data['month']:02d}-{flight_data['day_of_month']:02d}")
    print(f"   Hora: {flight_data['dep_hour']:02d}:30")
    print(f"   Distancia: {flight_data['distance']:.0f} millas")
    print(f"   Clima: {flight_data['temp']}°C, viento {flight_data['wind_spd']} km/h")
    
    result = predictor.predict(flight_data)
    
    print("\n🎯 RESULTADO:")
    print(f"   Previsión: {result['prevision']}")
    print(f"   Probabilidad de retraso: {result['probabilidad']:.2%}")
    print(f"   Confianza: {result['confianza']}")
    print(f"   Umbral usado: {result['umbral_usado']:.4f}")


def ejemplo_prediccion_batch():
    """Ejemplo de predicción por lotes."""
    print("\n" + "="*70)
    print("📝 EJEMPLO: PREDICCIÓN POR LOTES")
    print("="*70)
    
    predictor = FlightDelayPredictor()
    
    # Varios vuelos
    flights = [
        {
            'year': 2024, 'month': 6, 'day_of_month': 10, 'day_of_week': 1,
            'dep_hour': 8, 'sched_minute_of_day': 480,
            'op_unique_carrier': 'DL', 'origin': 'ATL', 'dest': 'ORD',
            'distance': 606.0, 'temp': 28.0, 'wind_spd': 10.0,
            'precip_1h': 0.0, 'climate_severity_idx': 0.2,
            'dist_met_km': 5.0, 'latitude': 33.6407, 'longitude': -84.4277
        },
        {
            'year': 2024, 'month': 12, 'day_of_month': 20, 'day_of_week': 5,
            'dep_hour': 18, 'sched_minute_of_day': 1080,
            'op_unique_carrier': 'UA', 'origin': 'SFO', 'dest': 'JFK',
            'distance': 2586.0, 'temp': 15.0, 'wind_spd': 25.0,
            'precip_1h': 5.0, 'climate_severity_idx': 0.85,
            'dist_met_km': 8.0, 'latitude': 37.6213, 'longitude': -122.3790
        },
        {
            'year': 2024, 'month': 4, 'day_of_month': 5, 'day_of_week': 3,
            'dep_hour': 12, 'sched_minute_of_day': 720,
            'op_unique_carrier': 'WN', 'origin': 'DAL', 'dest': 'HOU',
            'distance': 239.0, 'temp': 30.0, 'wind_spd': 12.0,
            'precip_1h': 0.0, 'climate_severity_idx': 0.15,
            'dist_met_km': 3.0, 'latitude': 32.8471, 'longitude': -96.8518
        }
    ]
    
    results = predictor.predict_batch(flights)
    
    print("\n📊 Resultados:")
    for i, result in enumerate(results):
        if 'error' not in result:
            flight = flights[i]
            print(f"\n   Vuelo {i+1}: {flight['origin']} → {flight['dest']}")
            print(f"      Previsión: {result['prevision']}")
            print(f"      Probabilidad: {result['probabilidad']:.2%}")
            print(f"      Confianza: {result['confianza']}")


def modo_interactivo():
    """Modo interactivo para ingresar datos de vuelo."""
    print("\n" + "="*70)
    print("🖥️  MODO INTERACTIVO")
    print("="*70)
    
    predictor = FlightDelayPredictor()
    
    print("\n📝 Ingrese los datos del vuelo:")
    
    try:
        flight_data = {
            'year': int(input("   Año (ej: 2024): ")),
            'month': int(input("   Mes (1-12): ")),
            'day_of_month': int(input("   Día del mes (1-31): ")),
            'day_of_week': int(input("   Día de la semana (1=Lun, 7=Dom): ")),
            'dep_hour': int(input("   Hora de salida (0-23): ")),
            'op_unique_carrier': input("   Código aerolínea (ej: AA, DL, UA): ").upper(),
            'origin': input("   Aeropuerto origen (ej: JFK): ").upper(),
            'dest': input("   Aeropuerto destino (ej: LAX): ").upper(),
            'distance': float(input("   Distancia en millas: ")),
            'temp': float(input("   Temperatura (°C): ")),
            'wind_spd': float(input("   Velocidad viento (km/h): ")),
            'precip_1h': float(input("   Precipitación (mm, 0 si no hay): ")),
            'climate_severity_idx': float(input("   Índice severidad clima (0-1): ")),
            'dist_met_km': float(input("   Distancia a estación meteo (km): ")),
            'latitude': float(input("   Latitud aeropuerto: ")),
            'longitude': float(input("   Longitud aeropuerto: ")),
        }
        
        # Calcular sched_minute_of_day
        flight_data['sched_minute_of_day'] = flight_data['dep_hour'] * 60
        
        result = predictor.predict(flight_data)
        
        print("\n" + "="*70)
        print("🎯 RESULTADO DE LA PREDICCIÓN")
        print("="*70)
        print(f"\n   ✈️  Vuelo: {flight_data['origin']} → {flight_data['dest']}")
        print(f"   📅 Fecha: {flight_data['year']}-{flight_data['month']:02d}-{flight_data['day_of_month']:02d}")
        print(f"   🕐 Hora: {flight_data['dep_hour']:02d}:00")
        print(f"\n   {'='*66}")
        print(f"   🎯 PREVISIÓN: {result['prevision'].upper()}")
        print(f"   {'='*66}")
        print(f"\n   📊 Probabilidad de retraso: {result['probabilidad']:.2%}")
        print(f"   📊 Confianza: {result['confianza']}")
        print(f"   📊 Umbral usado: {result['umbral_usado']:.4f}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Predicción cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def main():
    """Función principal."""
    print("="*70)
    print("✈️  FLIGHTONTIME - PREDICTOR DE RETRASOS DE VUELOS")
    print("="*70)
    print("\nModos de uso:")
    print("  1. Ejemplo simple")
    print("  2. Ejemplo por lotes (múltiples vuelos)")
    print("  3. Modo interactivo")
    print("  0. Salir")
    
    try:
        opcion = input("\nSeleccione una opción (1-3): ").strip()
        
        if opcion == '1':
            ejemplo_prediccion_simple()
        elif opcion == '2':
            ejemplo_prediccion_batch()
        elif opcion == '3':
            modo_interactivo()
        elif opcion == '0':
            print("\n👋 ¡Hasta luego!")
            return
        else:
            print("\n⚠️ Opción inválida. Ejecutando ejemplo simple...")
            ejemplo_prediccion_simple()
        
        print("\n" + "="*70)
        print("✅ Predicción completada")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Programa interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
