"""
FlightOnTime - Script Principal de Entrenamiento
=================================================
Ejecuta el pipeline completo: carga datos, feature engineering,
entrenamiento con división Train/Validation/Test, evaluación y exportación.

Configuración:
- Sample: dataset completo (sin muestreo)
- División: 70% Train / 15% Validation / 15% Test
- Features: 17 (según especificación)

Uso:
    python train_model.py
"""

import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
import pyarrow.dataset as ds
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import warnings
import time
warnings.filterwarnings('ignore')

# Imports locales
from config import (
    DATASET_PATH, MODEL_PATH, METADATA_PATH,
    OUTPUTS_DIR,
    FIGURES_DIR, METRICS_DIR, RANDOM_STATE,
    DELAY_THRESHOLD_MINUTES, MIN_RECALL_TARGET, MIN_PRECISION_TARGET
)
from features import FlightFeatureEngineer, get_features_for_model
from modeling import FlightDelayModel, OutOfCoreXGBModel
from evaluation import ModelEvaluator

# =============================================================================
# CONFIGURACIÓN DEL ENTRENAMIENTO
# =============================================================================

# Tama??o del sample (None = dataset completo)
_env_sample_size = os.getenv("SAMPLE_SIZE")
SAMPLE_SIZE = int(_env_sample_size) if _env_sample_size else None

# Entrenamiento out-of-core (XGBoost) para dataset completo
OUT_OF_CORE = os.getenv("OUT_OF_CORE") == "1"


# División de datos
TRAIN_SIZE = 0.70      # 70% para entrenamiento
VALIDATION_SIZE = 0.15 # 15% para validaci?n
TEST_SIZE = 0.15       # 15% para test final


def load_and_explore_data(dataset_path: Path, sample_size: int = None) -> pd.DataFrame:
    """Carga el dataset y muestra información básica."""
    print("\n" + "="*70)
    print("📂 FASE 1: CARGA DE DATOS")
    print("="*70)
    
    print(f"📁 Cargando dataset desde: {dataset_path}")
    start_time = time.time()
    df = pd.read_parquet(dataset_path)
    load_time = time.time() - start_time
    
    original_size = len(df)
    print(f"\n📊 Dimensiones originales: {original_size:,} filas x {df.shape[1]} columnas")
    print(f"⏱️ Tiempo de carga: {load_time:.1f} segundos")
    
    # Muestreo estratificado si el dataset es muy grande
    if sample_size and len(df) > sample_size:
        print(f"\n⚠️ Usando sample de {sample_size:,} registros ({100*sample_size/original_size:.1f}% del total)")
        
        # Muestreo estratificado por la variable objetivo
        if 'DEP_DEL15' in df.columns:
            from sklearn.model_selection import train_test_split
            df_sampled, _ = train_test_split(
                df, train_size=sample_size, random_state=RANDOM_STATE,
                stratify=df['DEP_DEL15']
            )
            df = df_sampled
            print(f"   ✓ Muestreo estratificado completado")
        else:
            df = df.sample(n=sample_size, random_state=RANDOM_STATE)
            print(f"   ✓ Muestreo aleatorio completado")
        
        print(f"📊 Dimensiones del sample: {len(df):,} filas")
    
    print(f"\n📋 Columnas disponibles ({len(df.columns)}):")
    for i, col in enumerate(df.columns):
        print(f"   {i+1:2d}. {col}")
    
    return df


def create_target_variable(df: pd.DataFrame, delay_col: str = 'dep_delay',
                           threshold: int = 15) -> pd.DataFrame:
    """Crea la variable objetivo binaria."""
    print("\n" + "="*70)
    print("🎯 FASE 2: CREACIÓN DE VARIABLE OBJETIVO")
    print("="*70)
    
    df = df.copy()
    
    # Usar DEP_DEL15 si existe (variable objetivo precalculada)
    if 'DEP_DEL15' in df.columns:
        print("📍 Usando variable objetivo precalculada: DEP_DEL15")
        df['is_delayed'] = df['DEP_DEL15'].fillna(0).astype(int)
        
        delayed_count = df['is_delayed'].sum()
        total = len(df)
        
        print(f"📍 Definición: Retraso >= 15 minutos = 1, Puntual = 0")
        print(f"\n📊 Distribución de clases:")
        print(f"   - Vuelos puntuales (0): {total - delayed_count:,} ({100*(total-delayed_count)/total:.1f}%)")
        print(f"   - Vuelos retrasados (1): {delayed_count:,} ({100*delayed_count/total:.1f}%)")
        if delayed_count > 0:
            ratio = (total-delayed_count)/delayed_count
            print(f"   - Ratio de desbalance: {ratio:.2f}:1")
        
        return df
    
    # Si no existe DEP_DEL15, buscar columna de delay
    if delay_col not in df.columns:
        delay_candidates = ['dep_delay', 'arr_delay', 'DEP_DELAY', 'ARR_DELAY', 'delay']
        for col in delay_candidates:
            if col in df.columns:
                delay_col = col
                break
    
    if delay_col in df.columns:
        df[delay_col] = df[delay_col].fillna(0)
        df['is_delayed'] = (df[delay_col] >= threshold).astype(int)
        
        delayed_count = df['is_delayed'].sum()
        total = len(df)
        
        print(f"📍 Columna de retraso usada: {delay_col}")
        print(f"📍 Umbral de retraso: >= {threshold} minutos")
        print(f"\n📊 Distribución de clases:")
        print(f"   - Vuelos puntuales (0): {total - delayed_count:,} ({100*(total-delayed_count)/total:.1f}%)")
        print(f"   - Vuelos retrasados (1): {delayed_count:,} ({100*delayed_count/total:.1f}%)")
        if delayed_count > 0:
            print(f"   - Ratio de desbalance: {(total-delayed_count)/delayed_count:.2f}:1")
    else:
        print(f"⚠️ No se encontró columna de retraso. Disponibles: {df.columns.tolist()}")
        raise ValueError("No se puede crear variable objetivo sin columna de delay")
    
    return df


def feature_engineering(df: pd.DataFrame) -> tuple:
    """Aplica feature engineering y retorna datos preparados."""
    print("\n" + "="*70)
    print("🔧 FASE 3: FEATURE ENGINEERING")
    print("="*70)
    
    # Inicializar feature engineer
    fe = FlightFeatureEngineer()
    
    # Normalizar nombres de columnas (el dataset tiene columnas en mayúsculas)
    print("\n📝 Normalizando nombres de columnas...")
    
    # Mapeo de columnas del dataset a nombres esperados (minúsculas)
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
    
    # Renombrar columnas que existen
    cols_to_rename = {k: v for k, v in column_mapping.items() if k in df.columns}
    df = df.rename(columns=cols_to_rename)
    
    # Manejar PRECIP_1H: reemplazar -1 con 0
    if 'precip_1h' in df.columns:
        df['precip_1h'] = df['precip_1h'].replace(-1, 0)
        print("   ✓ PRECIP_1H: valores -1 reemplazados por 0")
    
    # =========================================================================
    # FEATURES EXPLÍCITAS SEGÚN ESPECIFICACIÓN
    # =========================================================================
    
    print("\n📋 Features Pre-Vuelo seleccionadas:")
    
    # ----- TIEMPO -----
    print("\n   🕐 TIEMPO:")
    temporal_features = []
    
    for feat in ['year', 'month', 'day_of_week', 'day_of_month', 'dep_hour', 'sched_minute_of_day']:
        if feat in df.columns:
            temporal_features.append(feat)
            print(f"      ✓ {feat}")
    
    # ----- OPERACIÓN (categóricas) -----
    print("\n   ✈️ OPERACIÓN:")
    categorical_cols = []
    
    for feat in ['op_unique_carrier', 'origin', 'dest']:
        if feat in df.columns:
            categorical_cols.append(feat)
            print(f"      ✓ {feat}")
    
    # Codificar variables categóricas
    if categorical_cols:
        fe.fit_encoders(df, categorical_cols)
        df = fe.transform_categorical(df)
        print(f"      → Codificadas: {len(categorical_cols)} categorías")
    
    # ----- DISTANCIA -----
    print("\n   📏 DISTANCIA:")
    distance_features = []
    
    if 'distance' in df.columns:
        distance_features.append('distance')
        print(f"      ✓ distance")
    
    # ----- CLIMA -----
    print("\n   🌦️ CLIMA:")
    climate_features = []
    
    for feat in ['temp', 'wind_spd', 'precip_1h', 'climate_severity_idx', 'dist_met_km']:
        if feat in df.columns:
            climate_features.append(feat)
            print(f"      ✓ {feat}")
    
    # ----- GEOGRÁFICAS -----
    print("\n   🗺️ GEOGRÁFICAS:")
    geo_features = []
    
    for feat in ['latitude', 'longitude']:
        if feat in df.columns:
            geo_features.append(feat)
            print(f"      ✓ {feat}")
    
    # =========================================================================
    # LISTA FINAL DE FEATURES
    # =========================================================================
    
    # Features numéricas originales
    numeric_features = temporal_features + distance_features + climate_features + geo_features
    
    # Features categóricas codificadas
    encoded_features = [f"{col}_encoded" for col in categorical_cols]
    
    # Lista completa de features
    feature_cols = numeric_features + encoded_features
    
    # Verificar que todas existen
    feature_cols = [f for f in feature_cols if f in df.columns]
    
    # =========================================================================
    # RESUMEN
    # =========================================================================
    print("\n" + "-"*60)
    print(f"📊 RESUMEN DE FEATURES SELECCIONADAS:")
    print("-"*60)
    print(f"   Temporales: {len(temporal_features)}")
    print(f"   Operación:  {len(categorical_cols)} (encoded)")
    print(f"   Distancia:  {len(distance_features)}")
    print(f"   Clima:      {len(climate_features)}")
    print(f"   Geo:        {len(geo_features)}")
    print("-"*60)
    print(f"   TOTAL: {len(feature_cols)} features")
    
    return df, fe, feature_cols


def build_label_encoders(dataset_path: Path, batch_size: int = 200000) -> tuple:
    """
    Construye LabelEncoders para categoricas leyendo el dataset por lotes.
    """
    dataset = ds.dataset(str(dataset_path))
    columns = ['OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST']
    category_sets = {col: set() for col in columns}

    for batch in dataset.to_batches(columns=columns, batch_size=batch_size):
        for col in columns:
            values = batch.column(col).to_pylist()
            category_sets[col].update(v for v in values if v is not None)

    encoders = {}
    class_sets = {}
    for col, values in category_sets.items():
        ordered = sorted(values)
        ordered.append('__unknown__')
        le = LabelEncoder()
        le.fit(ordered)
        key = col.lower()
        encoders[key] = le
        class_sets[key] = set(le.classes_)

    return encoders, class_sets


def prepare_batch_dataframe(batch, encoders: dict, class_sets: dict) -> pd.DataFrame:
    """
    Convierte un batch Arrow a DataFrame con features normalizadas y categorizadas.
    """
    df = batch.to_pandas()

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
        'DEP_DEL15': 'is_delayed'
    }
    df = df.rename(columns=column_mapping)

    if 'precip_1h' in df.columns:
        df['precip_1h'] = df['precip_1h'].replace(-1, 0)

    # Encodings con '__unknown__'
    for col in ['op_unique_carrier', 'origin', 'dest']:
        le = encoders[col]
        valid = class_sets[col]
        values = df[col].astype(str).str.upper()
        values = values.where(values.isin(valid), '__unknown__')
        df[f"{col}_encoded"] = le.transform(values)

    return df


class ParquetDataIter(xgb.core.DataIter):
    """
    Iterador para XGBoost QuantileDMatrix leyendo Parquet por lotes.
    """

    def __init__(self, dataset_path: Path, encoders: dict, class_sets: dict,
                 feature_cols: list, split: str, batch_size: int = 50000):
        super().__init__()
        self.dataset = ds.dataset(str(dataset_path))
        self.encoders = encoders
        self.class_sets = class_sets
        self.feature_cols = feature_cols
        self.split = split
        self.batch_size = batch_size
        self.columns = [
            'YEAR', 'MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK',
            'OP_UNIQUE_CARRIER', 'ORIGIN', 'DEST', 'DEP_DEL15',
            'DISTANCE', 'DEP_HOUR', 'sched_minute_of_day',
            'LATITUDE', 'LONGITUDE', 'DIST_MET_KM',
            'TEMP', 'WIND_SPD', 'PRECIP_1H', 'CLIMATE_SEVERITY_IDX'
        ]
        self.rng = np.random.default_rng(RANDOM_STATE)
        self._reset_batches()

    def _reset_batches(self) -> None:
        self._batches = iter(self.dataset.to_batches(columns=self.columns, batch_size=self.batch_size))

    def reset(self) -> None:
        self.rng = np.random.default_rng(RANDOM_STATE)
        self._reset_batches()

    def next(self, input_data) -> int:
        while True:
            try:
                batch = next(self._batches)
            except StopIteration:
                return 0

            df = prepare_batch_dataframe(batch, self.encoders, self.class_sets)
            df[self.feature_cols] = df[self.feature_cols].fillna(0)
            df['is_delayed'] = df['is_delayed'].fillna(0)

            if df.empty:
                continue

            y = df['is_delayed'].astype(int).to_numpy()
            X = df[self.feature_cols].to_numpy()

            rand = self.rng.random(len(y))
            train_mask = rand < TRAIN_SIZE
            val_mask = (rand >= TRAIN_SIZE) & (rand < TRAIN_SIZE + VALIDATION_SIZE)
            test_mask = rand >= (TRAIN_SIZE + VALIDATION_SIZE)

            if self.split == 'train':
                mask = train_mask
            elif self.split == 'val':
                mask = val_mask
            else:
                mask = test_mask

            if not np.any(mask):
                continue

            input_data(data=X[mask], label=y[mask])
            return 1


def optimize_threshold(y_true: np.ndarray, y_proba: np.ndarray,
                       min_recall: float, min_precision: float) -> float:
    """
    Optimiza el umbral usando precision/recall.
    """
    from sklearn.metrics import precision_recall_curve

    precision_vals, recall_vals, thresholds = precision_recall_curve(y_true, y_proba)
    best_threshold = 0.5
    best_f1 = 0

    for i, threshold in enumerate(thresholds):
        if precision_vals[i] >= min_precision and recall_vals[i] >= min_recall:
            f1 = 2 * (precision_vals[i] * recall_vals[i]) / (precision_vals[i] + recall_vals[i] + 1e-10)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = threshold

    return float(best_threshold)


def train_out_of_core_xgboost(encoders: dict, class_sets: dict,
                              feature_cols: list) -> dict:
    """
    Entrena XGBoost en modo out-of-core usando archivos libsvm.
    """
    print("\n" + "="*70)
    print("🚀 ENTRENAMIENTO OUT-OF-CORE (XGBoost)")
    print("="*70)
    print("📌 Modo: QuantileDMatrix con DataIter")
    print("📌 Modelos: solo XGBoost")
    train_iter = ParquetDataIter(DATASET_PATH, encoders, class_sets, feature_cols, split='train')
    val_iter = ParquetDataIter(DATASET_PATH, encoders, class_sets, feature_cols, split='val')
    test_iter = ParquetDataIter(DATASET_PATH, encoders, class_sets, feature_cols, split='test')

    dtrain = xgb.QuantileDMatrix(train_iter, max_bin=256)
    dval = xgb.QuantileDMatrix(val_iter, max_bin=256, ref=dtrain)
    dtest = xgb.QuantileDMatrix(test_iter, max_bin=256, ref=dtrain)

    train_labels = dtrain.get_label()
    train_pos = np.sum(train_labels == 1)
    train_neg = np.sum(train_labels == 0)
    class_balance_ratio = train_neg / train_pos if train_pos else 1.0
    params = {
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'tree_method': 'hist',
        'max_depth': 6,
        'eta': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'scale_pos_weight': class_balance_ratio,
        'nthread': -1
    }

    evals = [(dtrain, 'train'), (dval, 'val')]
    booster = xgb.train(params, dtrain, num_boost_round=120, evals=evals, early_stopping_rounds=10)

    y_test = dtest.get_label()
    y_proba = booster.predict(dtest)

    threshold = optimize_threshold(y_test, y_proba, MIN_RECALL_TARGET, MIN_PRECISION_TARGET)
    y_pred = (y_proba >= threshold).astype(int)

    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        roc_auc_score, average_precision_score, confusion_matrix
    )

    test_metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_proba),
        'pr_auc': average_precision_score(y_test, y_proba),
    }

    cm = confusion_matrix(y_test, y_pred)
    test_metrics['confusion_matrix'] = cm.tolist()
    test_metrics['true_negatives'] = int(cm[0, 0])
    test_metrics['false_positives'] = int(cm[0, 1])
    test_metrics['false_negatives'] = int(cm[1, 0])
    test_metrics['true_positives'] = int(cm[1, 1])

    print(f"\n📌 Umbral optimizado: {threshold:.4f}")
    print(f"📌 Accuracy:  {test_metrics['accuracy']:.4f}")
    print(f"📌 Precision: {test_metrics['precision']:.4f}")
    print(f"📌 Recall:    {test_metrics['recall']:.4f}")
    print(f"📌 F1-Score:  {test_metrics['f1']:.4f}")
    print(f"📌 ROC-AUC:   {test_metrics['roc_auc']:.4f}")

    model_wrapper = OutOfCoreXGBModel(booster, feature_cols)

    return {
        'model': model_wrapper,
        'metrics': test_metrics,
        'threshold': threshold,
        'counts': {
            'train': int(dtrain.num_row()),
            'val': int(dval.num_row()),
            'test': int(dtest.num_row()),
            'train_pos': int(train_pos),
            'train_neg': int(train_neg),
            'val_pos': int(np.sum(dval.get_label() == 1)),
            'val_neg': int(np.sum(dval.get_label() == 0)),
            'test_pos': int(np.sum(dtest.get_label() == 1)),
            'test_neg': int(np.sum(dtest.get_label() == 0))
        },
        'class_balance_ratio': class_balance_ratio
    }


def save_out_of_core_artifacts(result: dict, encoders: dict,
                               feature_cols: list) -> None:
    """
    Guarda modelo, metadata, feature engineer y reportes para out-of-core.
    """
    import joblib
    import json
    from evaluation import ModelEvaluator

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(result['model'], MODEL_PATH)
    print(f"✅ Modelo guardado en: {MODEL_PATH}")

    # Feature engineer con encoders completos
    fe = FlightFeatureEngineer()
    fe.label_encoders = encoders
    fe.categorical_columns = ['op_unique_carrier', 'origin', 'dest']
    fe.feature_names = feature_cols
    fe.is_fitted = True

    fe_path = MODEL_PATH.parent / 'feature_engineer.joblib'
    joblib.dump(fe, fe_path)
    print(f"✅ Feature engineer guardado en: {fe_path}")

    metadata = {
        'model_name': 'XGBoost',
        'threshold': result['threshold'],
        'feature_names': feature_cols,
        'class_balance_ratio': result['class_balance_ratio'],
        'metrics': result['metrics'],
        'metrics_source': 'test_set_optimized_threshold_out_of_core',
        'trained_at': time.strftime("%Y-%m-%dT%H:%M:%S"),
        'random_state': RANDOM_STATE
    }

    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f"✅ Metadata guardada en: {METADATA_PATH}")

    counts = result['counts']
    splits_info = {
        'sample_size': None,
        'train_size': counts['train'],
        'validation_size': counts['val'],
        'test_size': counts['test'],
        'train_pct': TRAIN_SIZE * 100,
        'validation_pct': VALIDATION_SIZE * 100,
        'test_pct': TEST_SIZE * 100,
        'feature_names': feature_cols,
        'test_metrics': result['metrics'],
        'metrics_source': 'test_set_optimized_threshold_out_of_core'
    }

    splits_path = MODEL_PATH.parent / 'training_info.json'
    with open(splits_path, 'w') as f:
        json.dump(splits_info, f, indent=2, default=str)
    print(f"✅ Info de entrenamiento guardada en: {splits_path}")

    evaluator = ModelEvaluator(figures_dir=str(FIGURES_DIR), metrics_dir=str(METRICS_DIR))
    results = {'XGBoost': result['metrics']}
    evaluator.save_metrics_report(results, 'XGBoost')


def split_data(df: pd.DataFrame, feature_cols: list) -> dict:
    """
    Divide los datos en Train/Validation/Test con estratificación.
    
    Retorna diccionario con X_train, X_val, X_test, y_train, y_val, y_test
    """
    print("\n" + "="*70)
    print("📦 FASE 4: DIVISIÓN DE DATOS (Train/Validation/Test)")
    print("="*70)
    
    from sklearn.model_selection import train_test_split
    
    # Filtrar solo features disponibles
    available_features = [c for c in feature_cols if c in df.columns]
    
    # Eliminar filas con valores nulos
    df_clean = df[available_features + ['is_delayed']].dropna()
    
    print(f"\n📊 Registros totales: {len(df):,}")
    print(f"📊 Registros después de limpiar nulos: {len(df_clean):,}")
    print(f"📊 Features: {len(available_features)}")
    
    X = df_clean[available_features]
    y = df_clean['is_delayed'].values
    
    # Primera división: separar Test (15%)
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, 
        test_size=TEST_SIZE, 
        random_state=RANDOM_STATE, 
        stratify=y
    )
    
    # Segunda división: separar Train (70%) y Validation (15%)
    # Validation es 15% del total, que es ~17.6% de X_temp
    val_ratio = VALIDATION_SIZE / (TRAIN_SIZE + VALIDATION_SIZE)
    
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, 
        test_size=val_ratio, 
        random_state=RANDOM_STATE, 
        stratify=y_temp
    )
    
    print(f"\n📊 División de datos:")
    print(f"   ┌─────────────────────────────────────────────────┐")
    print(f"   │ Conjunto       │ Registros │ Porcentaje │ Retrasos │")
    print(f"   ├─────────────────────────────────────────────────┤")
    print(f"   │ Train          │ {len(X_train):>9,} │   {100*len(X_train)/len(X):>5.1f}%  │  {100*y_train.mean():>5.1f}%  │")
    print(f"   │ Validation     │ {len(X_val):>9,} │   {100*len(X_val)/len(X):>5.1f}%  │  {100*y_val.mean():>5.1f}%  │")
    print(f"   │ Test           │ {len(X_test):>9,} │   {100*len(X_test)/len(X):>5.1f}%  │  {100*y_test.mean():>5.1f}%  │")
    print(f"   └─────────────────────────────────────────────────┘")
    print(f"   │ TOTAL          │ {len(X):>9,} │  100.0%  │  {100*y.mean():>5.1f}%  │")
    
    return {
        'X_train': X_train, 'y_train': y_train,
        'X_val': X_val, 'y_val': y_val,
        'X_test': X_test, 'y_test': y_test,
        'feature_names': available_features
    }


def train_models(data: dict) -> tuple:
    """Entrena y compara modelos usando Train+Validation."""
    print("\n" + "="*70)
    print("🤖 FASE 5: ENTRENAMIENTO DE MODELOS")
    print("="*70)
    
    X_train = data['X_train']
    y_train = data['y_train']
    X_val = data['X_val']
    y_val = data['y_val']
    
    # Inicializar modelo
    model = FlightDelayModel(random_state=RANDOM_STATE)
    
    # Mostrar información
    print(f"\n📊 Balance de clases (Train):")
    print(f"   - Puntuales: {np.sum(y_train==0):,}")
    print(f"   - Retrasados: {np.sum(y_train==1):,}")
    print(f"   - Ratio: {np.sum(y_train==0)/np.sum(y_train==1):.2f}:1")
    
    # Entrenar con datos de entrenamiento
    print(f"\n📈 Entrenando con {len(X_train):,} registros...")
    start_time = time.time()
    
    # Usar train_and_compare con datos de validación externos
    results = model.train_and_compare(X_train, y_train, X_val=X_val, y_val=y_val)
    
    train_time = time.time() - start_time
    print(f"\n⏱️ Tiempo de entrenamiento: {train_time:.1f} segundos ({train_time/60:.1f} min)")
    
    # Evaluar en Validation
    print("\n📊 Evaluación en set de VALIDACIÓN:")
    y_val_pred = model.predict(X_val)
    y_val_proba = model.predict_proba(X_val)
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    val_metrics = {
        'accuracy': accuracy_score(y_val, y_val_pred),
        'precision': precision_score(y_val, y_val_pred),
        'recall': recall_score(y_val, y_val_pred),
        'f1': f1_score(y_val, y_val_pred),
    }
    
    print(f"   ✅ Accuracy:  {val_metrics['accuracy']:.4f}")
    print(f"   ✅ Precision: {val_metrics['precision']:.4f}")
    print(f"   ✅ Recall:    {val_metrics['recall']:.4f}")
    print(f"   ✅ F1-Score:  {val_metrics['f1']:.4f}")
    
    return model, results, val_metrics


def evaluate_on_test(model: FlightDelayModel, data: dict) -> dict:
    """Evaluación final en el set de Test (nunca visto)."""
    print("\n" + "="*70)
    print("📊 FASE 6: EVALUACIÓN FINAL EN TEST SET")
    print("="*70)
    
    X_test = data['X_test']
    y_test = data['y_test']
    
    print(f"\n⚠️ Evaluando en {len(X_test):,} registros NUNCA VISTOS...")
    
    # Optimizar umbral
    model.optimize_threshold(X_test, y_test, 
                             min_recall=MIN_RECALL_TARGET,
                             min_precision=MIN_PRECISION_TARGET)
    
    # Predicciones finales
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        roc_auc_score, average_precision_score, confusion_matrix
    )
    
    test_metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_proba),
        'pr_auc': average_precision_score(y_test, y_proba),
    }
    
    cm = confusion_matrix(y_test, y_pred)
    test_metrics['confusion_matrix'] = cm.tolist()
    test_metrics['true_negatives'] = int(cm[0, 0])
    test_metrics['false_positives'] = int(cm[0, 1])
    test_metrics['false_negatives'] = int(cm[1, 0])
    test_metrics['true_positives'] = int(cm[1, 1])
    
    print(f"\n📊 MÉTRICAS FINALES EN TEST SET:")
    print(f"   ┌────────────────────────────────────────┐")
    print(f"   │ Métrica      │ Valor                   │")
    print(f"   ├────────────────────────────────────────┤")
    print(f"   │ Accuracy     │ {test_metrics['accuracy']:.4f}                  │")
    print(f"   │ Precision    │ {test_metrics['precision']:.4f}                  │")
    print(f"   │ Recall       │ {test_metrics['recall']:.4f}                  │")
    print(f"   │ F1-Score     │ {test_metrics['f1']:.4f}                  │")
    print(f"   │ ROC-AUC      │ {test_metrics['roc_auc']:.4f}                  │")
    print(f"   │ PR-AUC       │ {test_metrics['pr_auc']:.4f}                  │")
    print(f"   └────────────────────────────────────────┘")
    
    print(f"\n📊 Matriz de Confusión:")
    print(f"                     Predicción")
    print(f"                  Puntual  Retrasado")
    print(f"   Real Puntual   {cm[0,0]:>7,}  {cm[0,1]:>7,}")
    print(f"        Retrasado {cm[1,0]:>7,}  {cm[1,1]:>7,}")
    
    return test_metrics


def generate_visualizations(model: FlightDelayModel, data: dict, 
                            train_results: dict, test_metrics: dict) -> None:
    """Genera todas las visualizaciones."""
    print("\n" + "="*70)
    print("📈 FASE 7: GENERACIÓN DE VISUALIZACIONES")
    print("="*70)
    
    # Inicializar evaluador
    evaluator = ModelEvaluator(
        figures_dir=str(FIGURES_DIR),
        metrics_dir=str(METRICS_DIR)
    )
    
    # Obtener importancia de features
    importance_df = model.get_feature_importance()
    
    X_test = data['X_test']
    y_test = data['y_test']
    
    # Generar reporte completo
    evaluator.generate_full_report(model, X_test, y_test, train_results, importance_df)


def save_model(model: FlightDelayModel, fe: FlightFeatureEngineer, 
               data: dict, test_metrics: dict) -> None:
    """Guarda el modelo y artefactos."""
    print("\n" + "="*70)
    print("💾 FASE 8: GUARDADO DEL MODELO")
    print("="*70)
    
    import joblib
    import json
    
    # Crear directorio si no existe
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Guardar modelo principal
    model.save_model(str(MODEL_PATH), str(METADATA_PATH), metrics=test_metrics, metrics_source="test_set_optimized_threshold")
    
    # Guardar feature engineer
    fe_path = MODEL_PATH.parent / 'feature_engineer.joblib'
    joblib.dump(fe, fe_path)
    print(f"✅ Feature engineer guardado en: {fe_path}")
    
    # Guardar información de splits
    splits_info = {
        'sample_size': SAMPLE_SIZE,
        'train_size': len(data['X_train']),
        'validation_size': len(data['X_val']),
        'test_size': len(data['X_test']),
        'train_pct': TRAIN_SIZE * 100,
        'validation_pct': VALIDATION_SIZE * 100,
        'test_pct': TEST_SIZE * 100,
        'feature_names': data['feature_names'],
        'test_metrics': test_metrics,
    }
    
    splits_path = MODEL_PATH.parent / 'training_info.json'
    with open(splits_path, 'w') as f:
        json.dump(splits_info, f, indent=2, default=str)
    print(f"✅ Info de entrenamiento guardada en: {splits_path}")


def main():
    """Ejecuta el pipeline completo de entrenamiento."""
    print("\n" + "="*70)
    print("✈️  FLIGHTONTIME - ENTRENAMIENTO DE MODELO (dataset completo)")
    print("="*70)
    print("📍 Predicción de retrasos de vuelos")
    print("📍 Clasificación binaria: Puntual (0) vs Retrasado (1)")
    print(f"📍 División: {int(TRAIN_SIZE*100)}% Train / {int(VALIDATION_SIZE*100)}% Val / {int(TEST_SIZE*100)}% Test")
    print(f"📍 Features: 17")
    
    total_start = time.time()
    
    try:
        # Entrenamiento out-of-core para dataset completo
        if OUT_OF_CORE and SAMPLE_SIZE is None:
            print("⚠️  OUT_OF_CORE=1: entrenamiento streaming con XGBoost")
            encoders, class_sets = build_label_encoders(DATASET_PATH)
            feature_cols = get_features_for_model()
            result = train_out_of_core_xgboost(encoders, class_sets, feature_cols)
            save_out_of_core_artifacts(result, encoders, feature_cols)
            print("✅ OUT-OF-CORE COMPLETADO")
            return 0

        # 1. Cargar datos (dataset completo)
        df = load_and_explore_data(DATASET_PATH, sample_size=SAMPLE_SIZE)
        
        # 2. Crear variable objetivo
        df = create_target_variable(df, threshold=DELAY_THRESHOLD_MINUTES)
        
        # 3. Feature engineering
        df, fe, feature_cols = feature_engineering(df)
        
        # 4. Dividir datos (Train/Val/Test)
        data = split_data(df, feature_cols)
        
        # 5. Entrenar modelos
        model, train_results, val_metrics = train_models(data)
        
        # 6. Evaluar en Test
        test_metrics = evaluate_on_test(model, data)
        
        # 7. Generar visualizaciones
        generate_visualizations(model, data, train_results, test_metrics)
        
        # 8. Guardar modelo
        save_model(model, fe, data, test_metrics)
        
        total_time = time.time() - total_start
        
        print("\n" + "="*70)
        print("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*70)
        print(f"\n🏆 Modelo final: {model.best_model_name}")
        print(f"⏱️ Tiempo total: {total_time:.1f} segundos ({total_time/60:.1f} min)")
        print(f"📁 Modelo guardado en: {MODEL_PATH}")
        print(f"📊 Visualizaciones en: {FIGURES_DIR}")
        print(f"📋 Métricas en: {METRICS_DIR}")
        
        print(f"\n📊 RESULTADOS FINALES (Test Set):")
        print(f"   - Accuracy:  {test_metrics['accuracy']:.4f}")
        print(f"   - Precision: {test_metrics['precision']:.4f}")
        print(f"   - Recall:    {test_metrics['recall']:.4f}")
        print(f"   - F1-Score:  {test_metrics['f1']:.4f}")
        print(f"   - ROC-AUC:   {test_metrics['roc_auc']:.4f}")
        
    except Exception as e:
        print(f"\n❌ Error durante el entrenamiento: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
