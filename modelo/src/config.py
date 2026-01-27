"""
FlightOnTime - Configuración del Proyecto
==========================================
Archivo de configuración central con rutas y parámetros reproducibles.
Actualizado: 2026-01-13
"""

from pathlib import Path
import os

# =============================================================================
# RUTAS DEL PROYECTO
# =============================================================================

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent

# Directorios principales
DATA_DIR = PROJECT_ROOT / "data"
DATASET_ORIGINAL_DIR = PROJECT_ROOT / "0.0. DATASET ORIGINAL"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
SRC_DIR = PROJECT_ROOT / "src"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
METRICS_DIR = OUTPUTS_DIR / "metrics"

# Archivos específicos
DATASET_PATH = DATASET_ORIGINAL_DIR / "dataset_prepared.parquet"
MODEL_PATH = MODELS_DIR / "model.joblib"
METADATA_PATH = MODELS_DIR / "metadata.json"
FEATURE_ENGINEER_PATH = MODELS_DIR / "feature_engineer.joblib"

# =============================================================================
# CONFIGURACIÓN DEL MODELO
# =============================================================================

# Semilla para reproducibilidad
RANDOM_STATE = 42

# División de datos
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Umbral de decisión optimizado
DECISION_THRESHOLD = 0.5591  # Optimizado durante entrenamiento (dataset completo)

# =============================================================================
# FEATURES DEL MODELO - SEGÚN ESPECIFICACIÓN
# =============================================================================

# --------- FEATURES TEMPORALES ---------
TEMPORAL_FEATURES = [
    'year',               # Patrones 2020-2024 (cambios estructurales)
    'month',              # Mes del año (1-12)
    'day_of_week',        # Día de la semana (1-7)
    'day_of_month',       # Día del mes (1-31) - opcional
    'dep_hour',           # Hora de salida (0-23) - interpretable
    'sched_minute_of_day', # Minuto del día (0-1439) - granular
]

# --------- FEATURES DE OPERACIÓN (Categóricas) ---------
OPERATION_FEATURES = [
    'op_unique_carrier',  # Código de aerolínea
    'origin',             # Aeropuerto origen (IATA)
    'dest',               # Aeropuerto destino (IATA)
]

# --------- FEATURES DE DISTANCIA ---------
DISTANCE_FEATURES = [
    'distance',           # Distancia del vuelo (millas) - numérica continua
]

# --------- FEATURES DE CLIMA ---------
CLIMATE_FEATURES = [
    'temp',               # Temperatura
    'wind_spd',           # Velocidad del viento
    'precip_1h',          # Precipitación última hora (-1 → 0)
    'climate_severity_idx', # Índice de severidad climática
    'dist_met_km',        # Distancia a estación meteorológica (confianza)
]

# --------- FEATURES GEOGRÁFICAS ---------
GEO_FEATURES = [
    'latitude',           # Latitud del aeropuerto
    'longitude',          # Longitud del aeropuerto
]

# Lista completa de features numéricas
NUMERIC_FEATURES = TEMPORAL_FEATURES + DISTANCE_FEATURES + CLIMATE_FEATURES + GEO_FEATURES

# Features categóricas (serán codificadas)
CATEGORICAL_FEATURES = OPERATION_FEATURES

# Features encoded (después de LabelEncoder)
ENCODED_FEATURES = [f"{col}_encoded" for col in CATEGORICAL_FEATURES]

# TODAS las features del modelo
ALL_FEATURES = NUMERIC_FEATURES + ENCODED_FEATURES

# =============================================================================
# FEATURES EXCLUIDAS (EVITAR LEAKAGE)
# =============================================================================

EXCLUDED_FEATURES = [
    'DEP_DEL15',          # Target - variable objetivo
    'DEP_DELAY',          # Contiene la respuesta en minutos (leakage)
    'STATION_KEY',        # Llave técnica, no aporta valor
    'FL_DATE',            # Alta cardinalidad, usar componentes separados
    'ORIGIN_CITY_NAME',   # Redundante con origin
    'DEST_CITY_NAME',     # Redundante con dest
]

# =============================================================================
# VARIABLE OBJETIVO
# =============================================================================

TARGET_COLUMN = 'is_delayed'  # 0 = Puntual, 1 = Retrasado

# Definición de retraso (en minutos)
DELAY_THRESHOLD_MINUTES = 15  # Vuelo se considera retrasado si >= 15 min

# =============================================================================
# CONTRATO DE INTEGRACIÓN CON BACKEND
# =============================================================================

# Mapeo de predicción a texto
PREDICTION_LABELS = {
    0: "Puntual",
    1: "Retrasado"
}

# Campos de entrada del API
API_INPUT_FIELDS = {
    'aerolinea': 'op_unique_carrier',
    'origen': 'origin',
    'destino': 'dest',
    'fecha_partida': None,  # Se parsea a múltiples campos
    'distancia_km': 'distance',
}

# =============================================================================
# CONFIGURACIÓN DE MODELOS A COMPARAR
# =============================================================================

MODELS_CONFIG = {
    'LogisticRegression': {
        'params': {
            'random_state': RANDOM_STATE,
            'max_iter': 1000,
            'class_weight': 'balanced'
        }
    },
    'RandomForest': {
        'params': {
            'random_state': RANDOM_STATE,
            'n_estimators': 100,
            'max_depth': 10,
            'class_weight': 'balanced',
            'n_jobs': -1
        }
    },
    'XGBoost': {
        'params': {
            'random_state': RANDOM_STATE,
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'scale_pos_weight': 4.3,  # Ratio de desbalance ~4.3:1
            'n_jobs': -1,
            'eval_metric': 'logloss'
        }
    },
    'LightGBM': {
        'params': {
            'random_state': RANDOM_STATE,
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'class_weight': 'balanced',
            'n_jobs': -1,
            'verbose': -1
        }
    }
}

# =============================================================================
# MÉTRICAS DE EVALUACIÓN
# =============================================================================

# Métrica principal para selección de modelo
PRIMARY_METRIC = 'f1'

# Métricas secundarias a reportar
SECONDARY_METRICS = ['accuracy', 'precision', 'recall', 'roc_auc', 'pr_auc']

# Objetivos mínimos
MIN_RECALL_TARGET = 0.40    # Detectar al menos 40% de retrasos
MIN_PRECISION_TARGET = 0.35 # Al menos 35% de alertas correctas

# =============================================================================
# RESULTADOS ACTUALES DEL MODELO (XGBoost)
# =============================================================================

CURRENT_MODEL_METRICS = {
    'model_name': 'XGBoost',
    'accuracy': 0.7232,
    'precision': 0.3501,
    'recall': 0.5430,
    'f1': 0.4257,
    'roc_auc': 0.7194,
    'pr_auc': 0.3874,
    'threshold': 0.5591,
    'total_features': 17,
}
