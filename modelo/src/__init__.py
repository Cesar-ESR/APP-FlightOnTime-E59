"""
FlightOnTime - Módulo de Ciencia de Datos
==========================================
Sistema de predicción de retrasos de vuelos usando Machine Learning.

Features del modelo (17 total):
- Temporales (6): year, month, day_of_week, day_of_month, dep_hour, sched_minute_of_day
- Operación (3): op_unique_carrier_encoded, origin_encoded, dest_encoded
- Distancia (1): distance
- Clima (5): temp, wind_spd, precip_1h, climate_severity_idx, dist_met_km
- Geográficas (2): latitude, longitude

Actualizado: 2026-01-13
"""

from .config import (
    # Rutas
    PROJECT_ROOT, DATA_DIR, MODELS_DIR, OUTPUTS_DIR, FIGURES_DIR, METRICS_DIR,
    DATASET_PATH, MODEL_PATH, METADATA_PATH, FEATURE_ENGINEER_PATH,
    # Configuración
    RANDOM_STATE, TEST_SIZE, DECISION_THRESHOLD,
    # Features
    TEMPORAL_FEATURES, OPERATION_FEATURES, DISTANCE_FEATURES, 
    CLIMATE_FEATURES, GEO_FEATURES, ALL_FEATURES,
    CATEGORICAL_FEATURES, EXCLUDED_FEATURES,
    # Target
    TARGET_COLUMN, DELAY_THRESHOLD_MINUTES, PREDICTION_LABELS,
    # Métricas
    PRIMARY_METRIC, SECONDARY_METRICS, MIN_RECALL_TARGET, MIN_PRECISION_TARGET,
)

from .features import (
    FlightFeatureEngineer, 
    get_features_for_model, 
    get_excluded_features,
    prepare_input_from_api
)

from .modeling import (
    FlightDelayModel, 
    cross_validate_model
)

from .evaluation import (
    ModelEvaluator
)

__version__ = '3.0.0'
__author__ = 'FlightOnTime Team'
