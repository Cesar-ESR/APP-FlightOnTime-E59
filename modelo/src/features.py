"""
FlightOnTime - Feature Engineering
==================================
Módulo para crear y transformar features del modelo de predicción.
Todas las features son calculables 24 horas antes del vuelo.

Features utilizadas (17 total):
- Temporales (6): year, month, day_of_week, day_of_month, dep_hour, sched_minute_of_day
- Operación (3): op_unique_carrier, origin, dest (encoded)
- Distancia (1): distance
- Clima (5): temp, wind_spd, precip_1h, climate_severity_idx, dist_met_km
- Geográficas (2): latitude, longitude

Actualizado: 2026-01-12
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.preprocessing import LabelEncoder, StandardScaler
import warnings
warnings.filterwarnings('ignore')


class FlightFeatureEngineer:
    """
    Clase para ingeniería de features de vuelos.
    Diseñada para ser reutilizable en entrenamiento y predicción.
    """
    
    def __init__(self):
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scaler: Optional[StandardScaler] = None
        self.feature_names: List[str] = []
        self.categorical_columns: List[str] = []
        self.numerical_columns: List[str] = []
        self.is_fitted = False
        
    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza nombres de columnas de mayúsculas a minúsculas.
        """
        column_mapping = {
            'YEAR': 'year',
            'MONTH': 'month',
            'DAY_OF_MONTH': 'day_of_month',
            'DAY_OF_WEEK': 'day_of_week',
            'OP_UNIQUE_CARRIER': 'op_unique_carrier',
            'ORIGIN': 'origin',
            'DEST': 'dest',
            'DISTANCE': 'distance',
            'DEP_HOUR': 'dep_hour',
            'LATITUDE': 'latitude',
            'LONGITUDE': 'longitude',
            'DIST_MET_KM': 'dist_met_km',
            'TEMP': 'temp',
            'WIND_SPD': 'wind_spd',
            'PRECIP_1H': 'precip_1h',
            'CLIMATE_SEVERITY_IDX': 'climate_severity_idx',
        }
        
        cols_to_rename = {k: v for k, v in column_mapping.items() if k in df.columns}
        return df.rename(columns=cols_to_rename)
    
    def clean_precipitation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia valores de precipitación: -1 → 0
        """
        if 'precip_1h' in df.columns:
            df['precip_1h'] = df['precip_1h'].replace(-1, 0)
        return df
        
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features temporales derivadas de la fecha/hora.
        Todas calculables 24h antes del vuelo.
        """
        df = df.copy()
        
        # Convertir fecha si es necesario
        if 'fl_date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['fl_date']):
            df['fl_date'] = pd.to_datetime(df['fl_date'])
        
        # Features de fecha (disponibles 24h antes)
        if 'fl_date' in df.columns:
            df['year'] = df['fl_date'].dt.year
            df['month'] = df['fl_date'].dt.month
            df['day_of_month'] = df['fl_date'].dt.day
            df['day_of_week'] = df['fl_date'].dt.dayofweek + 1  # 1=Lunes, 7=Domingo
        
        # Hora del día (de la hora programada de salida)
        if 'crs_dep_time' in df.columns:
            # crs_dep_time está en formato HHMM (ej: 1430 = 14:30)
            df['dep_hour'] = (df['crs_dep_time'] // 100).astype(int)
            df['dep_minute'] = (df['crs_dep_time'] % 100).astype(int)
            df['sched_minute_of_day'] = df['dep_hour'] * 60 + df['dep_minute']
        
        return df
    
    def fit_encoders(self, df: pd.DataFrame, categorical_cols: List[str]) -> None:
        """
        Ajusta los encoders para las columnas categóricas.
        """
        self.categorical_columns = categorical_cols
        
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                # Incluir valor 'unknown' para manejar categorías nuevas
                unique_vals = df[col].astype(str).unique().tolist()
                unique_vals.append('__unknown__')
                le.fit(unique_vals)
                self.label_encoders[col] = le
    
    def transform_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforma columnas categóricas a numéricas usando los encoders ajustados.
        """
        df = df.copy()
        
        for col, le in self.label_encoders.items():
            if col in df.columns:
                # Reemplazar valores desconocidos con '__unknown__'
                df[col] = df[col].astype(str).apply(
                    lambda x: x if x in le.classes_ else '__unknown__'
                )
                df[col + '_encoded'] = le.transform(df[col])
        
        return df
    
    def create_target_variable(self, df: pd.DataFrame, 
                                delay_column: str = 'dep_delay',
                                threshold_minutes: int = 15) -> pd.DataFrame:
        """
        Crea la variable objetivo binaria (is_delayed).
        Un vuelo se considera retrasado si el retraso >= threshold_minutes.
        """
        df = df.copy()
        
        # Si ya existe DEP_DEL15, usarlo directamente
        if 'DEP_DEL15' in df.columns:
            df['is_delayed'] = df['DEP_DEL15'].fillna(0).astype(int)
        elif delay_column in df.columns:
            df['is_delayed'] = (df[delay_column] >= threshold_minutes).astype(int)
        
        return df
    
    def get_feature_list(self) -> Dict[str, List[str]]:
        """
        Retorna la lista de features organizadas por categoría.
        """
        return {
            'temporal': ['year', 'month', 'day_of_week', 'day_of_month', 
                        'dep_hour', 'sched_minute_of_day'],
            'operation': ['op_unique_carrier_encoded', 'origin_encoded', 'dest_encoded'],
            'distance': ['distance'],
            'climate': ['temp', 'wind_spd', 'precip_1h', 'climate_severity_idx', 'dist_met_km'],
            'geo': ['latitude', 'longitude'],
        }
    
    def get_all_features(self) -> List[str]:
        """
        Retorna lista plana de todas las features.
        """
        feature_dict = self.get_feature_list()
        all_features = []
        for category_features in feature_dict.values():
            all_features.extend(category_features)
        return all_features
    
    def fit_transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Pipeline completo: normalizar, limpiar y codificar.
        """
        # Normalizar nombres
        df = self.normalize_column_names(df)
        
        # Limpiar precipitación
        df = self.clean_precipitation(df)
        
        # Codificar categóricas
        categorical_cols = ['op_unique_carrier', 'origin', 'dest']
        categorical_cols = [c for c in categorical_cols if c in df.columns]
        
        self.fit_encoders(df, categorical_cols)
        df = self.transform_categorical(df)
        
        self.is_fitted = True
        
        # Retornar features
        feature_cols = self.get_all_features()
        feature_cols = [f for f in feature_cols if f in df.columns]
        
        return df, feature_cols
    
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Transforma un nuevo DataFrame usando los transformers ajustados.
        """
        if not self.is_fitted:
            raise ValueError("FeatureEngineer no ha sido ajustado. Llama fit_transform primero.")
        
        # Normalizar nombres
        df = self.normalize_column_names(df)
        
        # Limpiar precipitación
        df = self.clean_precipitation(df)
        
        # Transformar categóricas
        df = self.transform_categorical(df)
        
        # Retornar features
        feature_cols = self.get_all_features()
        feature_cols = [f for f in feature_cols if f in df.columns]
        
        return df, feature_cols


def get_features_for_model() -> List[str]:
    """
    Retorna la lista de features a usar en el modelo.
    """
    return [
        # Temporales
        'year', 'month', 'day_of_week', 'day_of_month', 
        'dep_hour', 'sched_minute_of_day',
        # Distancia
        'distance',
        # Clima
        'temp', 'wind_spd', 'precip_1h', 'climate_severity_idx', 'dist_met_km',
        # Geográficas
        'latitude', 'longitude',
        # Operación (encoded)
        'op_unique_carrier_encoded', 'origin_encoded', 'dest_encoded',
    ]


def get_excluded_features() -> List[str]:
    """
    Retorna la lista de features excluidas para evitar leakage.
    """
    return [
        'DEP_DEL15',      # Target
        'DEP_DELAY',      # Contiene respuesta (leakage)
        'STATION_KEY',    # Llave técnica
        'FL_DATE',        # Alta cardinalidad
        'is_delayed',     # Target derivado
    ]


def prepare_input_from_api(input_data: Dict) -> pd.DataFrame:
    """
    Prepara los datos de entrada del API para predicción.
    Convierte el formato del contrato al formato del modelo.
    
    Input esperado:
    {
        "aerolinea": "AA",
        "origen": "JFK",
        "destino": "LAX",
        "fecha_partida": "2025-03-15T14:30:00",
        "distancia_km": 3983
    }
    """
    from datetime import datetime
    
    # Parsear fecha
    fecha = datetime.fromisoformat(input_data['fecha_partida'])

    # Convertir distancia de km a millas (modelo espera millas)
    distance_km = input_data['distancia_km']
    distance_miles = distance_km * 0.621371

    
    # Crear DataFrame con formato del modelo
    df = pd.DataFrame([{
        'year': fecha.year,
        'month': fecha.month,
        'day_of_month': fecha.day,
        'day_of_week': fecha.isoweekday(),  # 1=Lunes, 7=Domingo
        'dep_hour': fecha.hour,
        'sched_minute_of_day': fecha.hour * 60 + fecha.minute,
        'op_unique_carrier': input_data['aerolinea'],
        'origin': input_data['origen'],
        'dest': input_data['destino'],
        'distance': distance_miles,
        # Valores por defecto para clima (si no vienen del API)
        'temp': input_data.get('temp', input_data.get('temperatura', 20.0)),
        'wind_spd': input_data.get('wind_spd', input_data.get('velocidad_viento', 5.0)),
        'precip_1h': input_data.get('precip_1h', input_data.get('precipitacion', 0.0)),
        'climate_severity_idx': input_data.get('climate_severity_idx', 0.0),
        'dist_met_km': input_data.get('dist_met_km', 10.0),
        'latitude': input_data.get('latitude', 40.0),
        'longitude': input_data.get('longitude', -74.0),
    }])
    
    return df
