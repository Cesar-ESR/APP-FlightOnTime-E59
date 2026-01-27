"""
FlightOnTime - Script de Interacción con el Modelo
===================================================
Script para probar predicciones del modelo entrenado.
Actualizado: 2026-01-12
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import joblib
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / 'models' / 'model.joblib'
METADATA_PATH = PROJECT_ROOT / 'models' / 'metadata.json'
FE_PATH = PROJECT_ROOT / 'models' / 'feature_engineer.joblib'


def load_model():
    """Carga el modelo y el feature engineer."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo no encontrado en {MODEL_PATH}. Ejecuta train_model.py primero.")
    
    model = joblib.load(MODEL_PATH)
    
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)
    
    fe = None
    if FE_PATH.exists():
        fe = joblib.load(FE_PATH)
    
    return model, metadata, fe


def predict_flight(aerolinea: str, origen: str, destino: str, 
                   fecha_partida: str, distancia_km: float,
                   temp: float = 20.0, wind_spd: float = 5.0,
                   precip_1h: float = 0.0, climate_severity_idx: float = 0.0,
                   dist_met_km: float = 10.0, latitude: float = 40.0,
                   longitude: float = -74.0) -> dict:
    """
    Realiza predicción para un vuelo.
    
    Args:
        aerolinea: Código de aerolínea (ej: "AA")
        origen: Código IATA origen (ej: "JFK")
        destino: Código IATA destino (ej: "LAX")
        fecha_partida: Fecha/hora ISO (ej: "2025-03-15T14:30:00")
        distancia_km: Distancia en kilómetros
        temp: Temperatura (°C)
        wind_spd: Velocidad del viento (km/h)
        precip_1h: Precipitación última hora (mm)
        climate_severity_idx: Índice de severidad climática
        dist_met_km: Distancia a estación meteorológica (km)
        latitude: Latitud del aeropuerto
        longitude: Longitud del aeropuerto
    
    Returns:
        dict con prevision y probabilidad
    """
    # Cargar modelo
    model, metadata, fe = load_model()
    
    # Parsear fecha
    fecha = datetime.fromisoformat(fecha_partida)
    
    # Crear DataFrame con formato del modelo
    df = pd.DataFrame([{
        # Temporales
        'year': fecha.year,
        'month': fecha.month,
        'day_of_week': fecha.isoweekday(),  # 1=Lunes, 7=Domingo
        'day_of_month': fecha.day,
        'dep_hour': fecha.hour,
        'sched_minute_of_day': fecha.hour * 60 + fecha.minute,
        # Distancia
        'distance': distancia_km,
        # Clima
        'temp': temp,
        'wind_spd': wind_spd,
        'precip_1h': max(0, precip_1h),  # -1 → 0
        'climate_severity_idx': climate_severity_idx,
        'dist_met_km': dist_met_km,
        # Geográficas
        'latitude': latitude,
        'longitude': longitude,
        # Operación (para encoding)
        'op_unique_carrier': aerolinea,
        'origin': origen,
        'dest': destino,
    }])
    
    # Transformar categóricas si hay feature engineer
    if fe is not None:
        df = fe.transform_categorical(df)
    else:
        # Encoding manual simple
        df['op_unique_carrier_encoded'] = 0
        df['origin_encoded'] = 0
        df['dest_encoded'] = 0
    
    # Obtener features del modelo
    feature_names = metadata.get('feature_names', [])
    
    # Preparar X para predicción
    available_features = [f for f in feature_names if f in df.columns]
    X = df[available_features].fillna(0)
    
    # Predecir
    threshold = float(metadata.get('threshold', 0.5))
    proba = model.predict_proba(X)[0, 1]
    prediction = 1 if proba >= threshold else 0
    
    return {
        "prevision": "Retrasado" if prediction == 1 else "Puntual",
        "probabilidad": round(float(proba), 4)
    }


def interactive_mode():
    """Modo interactivo para probar predicciones."""
    print("\n" + "="*60)
    print("✈️  FlightOnTime - Predictor de Retrasos")
    print("="*60)
    
    try:
        model, metadata, _ = load_model()
        print(f"✅ Modelo cargado: {metadata.get('model_name', 'Unknown')}")
        print(f"📊 Umbral: {metadata.get('threshold', 0.5)}")
        print(f"📊 Features: {len(metadata.get('feature_names', []))}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    # Ejemplos de prueba
    examples = [
        {
            "aerolinea": "AA",
            "origen": "JFK",
            "destino": "LAX",
            "fecha_partida": "2025-03-15T06:00:00",  # Madrugada
            "distancia_km": 3983,
            "temp": 15.0,
            "wind_spd": 10.0,
            "precip_1h": 0.0,
            "climate_severity_idx": 0.1
        },
        {
            "aerolinea": "UA",
            "origen": "ORD",
            "destino": "ATL",
            "fecha_partida": "2025-03-15T18:30:00",  # Tarde/noche
            "distancia_km": 975,
            "temp": 28.0,
            "wind_spd": 25.0,
            "precip_1h": 5.0,
            "climate_severity_idx": 0.6
        },
        {
            "aerolinea": "DL",
            "origen": "SFO",
            "destino": "DEN",
            "fecha_partida": "2025-07-20T14:00:00",  # Verano, tarde
            "distancia_km": 1528,
            "temp": 35.0,
            "wind_spd": 15.0,
            "precip_1h": 0.0,
            "climate_severity_idx": 0.3
        }
    ]
    
    print("\n" + "-"*60)
    print("📋 EJEMPLOS DE PREDICCIÓN")
    print("-"*60)
    
    for i, ex in enumerate(examples, 1):
        print(f"\n{'='*50}")
        print(f"📍 Ejemplo {i}")
        print(f"{'='*50}")
        print(f"   Aerolínea: {ex['aerolinea']}")
        print(f"   Ruta: {ex['origen']} → {ex['destino']}")
        print(f"   Fecha: {ex['fecha_partida']}")
        print(f"   Distancia: {ex['distancia_km']} km")
        print(f"   Clima: Temp={ex['temp']}°C, Viento={ex['wind_spd']}km/h")
        print(f"   Precipitación: {ex['precip_1h']}mm")
        print(f"   Severidad climática: {ex['climate_severity_idx']}")
        
        try:
            result = predict_flight(**ex)
            emoji = "🟢" if result['prevision'] == "Puntual" else "🔴"
            print(f"\n   {emoji} Predicción: {result['prevision']}")
            print(f"   📊 Probabilidad de retraso: {result['probabilidad']:.1%}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ Pruebas completadas")
    print("="*60)


def batch_predict(data: list) -> list:
    """
    Realiza predicciones en lote.
    
    Args:
        data: Lista de diccionarios con datos de vuelos
        
    Returns:
        Lista de diccionarios con predicciones
    """
    results = []
    for flight in data:
        try:
            result = predict_flight(**flight)
            result['input'] = flight
            results.append(result)
        except Exception as e:
            results.append({
                'input': flight,
                'error': str(e)
            })
    return results


if __name__ == "__main__":
    interactive_mode()
