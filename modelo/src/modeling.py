"""
FlightOnTime - Modelado
=======================
Módulo para entrenamiento y comparación de modelos de clasificación.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import joblib
import json
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    precision_recall_curve, roc_curve, classification_report
)
import xgboost as xgb
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

import warnings
warnings.filterwarnings('ignore')


class FlightDelayModel:
    """
    Clase para entrenar y gestionar modelos de predicción de retrasos.
    """
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models: Dict[str, Any] = {}
        self.best_model = None
        self.best_model_name: str = ""
        self.best_threshold: float = 0.5
        self.feature_names: List[str] = []
        self.metrics_history: Dict[str, Dict] = {}
        self.class_balance_ratio: float = 1.0
        
    def get_model_instances(self, class_weight_ratio: float = 1.0) -> Dict[str, Any]:
        """
        Retorna instancias de los modelos a comparar.
        """
        models = {
            'LogisticRegression': LogisticRegression(
                random_state=self.random_state,
                max_iter=1000,
                class_weight='balanced',
                solver='lbfgs'
            ),
            'RandomForest': RandomForestClassifier(
                random_state=self.random_state,
                n_estimators=100,
                max_depth=10,
                class_weight='balanced',
                n_jobs=-1
            ),
            'XGBoost': XGBClassifier(
                random_state=self.random_state,
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=class_weight_ratio,
                n_jobs=-1,
                eval_metric='logloss',
                use_label_encoder=False
            ),
            'LightGBM': LGBMClassifier(
                random_state=self.random_state,
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                class_weight='balanced',
                n_jobs=-1,
                verbose=-1
            )
        }
        return models
    
    def calculate_class_balance(self, y: np.ndarray) -> float:
        """
        Calcula el ratio de desbalance de clases para XGBoost.
        """
        neg_count = np.sum(y == 0)
        pos_count = np.sum(y == 1)
        return neg_count / pos_count if pos_count > 0 else 1.0
    
    def train_and_compare(self, X: pd.DataFrame, y: np.ndarray,
                          test_size: float = 0.2,
                          X_val: pd.DataFrame = None, y_val: np.ndarray = None) -> Dict[str, Dict]:
        """
        Entrena y compara todos los modelos.
        
        Args:
            X: Features de entrenamiento
            y: Target de entrenamiento
            test_size: Tamaño del split de validación (ignorado si se pasa X_val/y_val)
            X_val: Features de validación externa (opcional)
            y_val: Target de validación externa (opcional)
        
        Retorna métricas de cada modelo.
        """
        self.feature_names = X.columns.tolist()
        self.class_balance_ratio = self.calculate_class_balance(y)
        
        print(f"📊 Balance de clases: {np.sum(y==0)} puntuales vs {np.sum(y==1)} retrasados")
        print(f"📊 Ratio de desbalance: {self.class_balance_ratio:.2f}")
        
        # Usar datos de validación externos si se proporcionan
        if X_val is not None and y_val is not None:
            X_train, y_train = X, y
            X_test, y_test = X_val, y_val
            print(f"\n📈 Datos de entrenamiento: {len(X_train):,} registros")
            print(f"📈 Datos de validación: {len(X_test):,} registros (externos)")
        else:
            # División tradicional (stratified)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.random_state, stratify=y
            )
            print(f"\n📈 Datos de entrenamiento: {len(X_train):,} registros")
            print(f"📈 Datos de prueba: {len(X_test):,} registros")
        
        # Obtener modelos
        models = self.get_model_instances(self.class_balance_ratio)
        
        results = {}
        
        for name, model in models.items():
            print(f"\n🔄 Entrenando {name}...")
            
            try:
                # Entrenar
                model.fit(X_train, y_train)
                self.models[name] = model
                
                # Predecir
                y_pred = model.predict(X_test)
                y_proba = model.predict_proba(X_test)[:, 1]
                
                # Calcular métricas
                metrics = self._calculate_metrics(y_test, y_pred, y_proba)
                results[name] = metrics
                
                print(f"   ✅ Accuracy: {metrics['accuracy']:.4f}")
                print(f"   ✅ F1-Score: {metrics['f1']:.4f}")
                print(f"   ✅ Recall: {metrics['recall']:.4f}")
                print(f"   ✅ Precision: {metrics['precision']:.4f}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                results[name] = {'error': str(e)}
        
        self.metrics_history = results
        
        # Seleccionar mejor modelo
        self._select_best_model(results)
        
        return results
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                          y_proba: np.ndarray) -> Dict[str, float]:
        """
        Calcula todas las métricas de evaluación.
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_proba),
            'pr_auc': average_precision_score(y_true, y_proba),
        }
        
        # Matriz de confusión
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        metrics['true_negatives'] = int(cm[0, 0])
        metrics['false_positives'] = int(cm[0, 1])
        metrics['false_negatives'] = int(cm[1, 0])
        metrics['true_positives'] = int(cm[1, 1])
        
        return metrics
    
    def _select_best_model(self, results: Dict[str, Dict], 
                           primary_metric: str = 'f1') -> None:
        """
        Selecciona el mejor modelo basado en la métrica principal.
        """
        best_score = -1
        best_name = ""
        
        for name, metrics in results.items():
            if 'error' not in metrics:
                score = metrics.get(primary_metric, 0)
                if score > best_score:
                    best_score = score
                    best_name = name
        
        if best_name:
            self.best_model = self.models[best_name]
            self.best_model_name = best_name
            print(f"\n🏆 Mejor modelo: {best_name} ({primary_metric}={best_score:.4f})")
    
    def optimize_threshold(self, X: pd.DataFrame, y: np.ndarray,
                          min_recall: float = 0.4,
                          min_precision: float = 0.35) -> float:
        """
        Optimiza el umbral de decisión para balancear precision y recall.
        """
        if self.best_model is None:
            raise ValueError("No hay modelo entrenado. Llama train_and_compare primero.")
        
        y_proba = self.best_model.predict_proba(X)[:, 1]
        
        # Calcular precision-recall para diferentes umbrales
        precision_vals, recall_vals, thresholds = precision_recall_curve(y, y_proba)
        
        # Encontrar umbral óptimo que cumpla restricciones
        best_threshold = 0.5
        best_f1 = 0
        
        for i, threshold in enumerate(thresholds):
            if precision_vals[i] >= min_precision and recall_vals[i] >= min_recall:
                f1 = 2 * (precision_vals[i] * recall_vals[i]) / (precision_vals[i] + recall_vals[i] + 1e-10)
                if f1 > best_f1:
                    best_f1 = f1
                    best_threshold = threshold
        
        self.best_threshold = best_threshold
        print(f"\n🎯 Umbral optimizado: {best_threshold:.4f}")
        
        # Recalcular métricas con nuevo umbral
        y_pred_opt = (y_proba >= best_threshold).astype(int)
        print(f"   Precision con umbral optimizado: {precision_score(y, y_pred_opt):.4f}")
        print(f"   Recall con umbral optimizado: {recall_score(y, y_pred_opt):.4f}")
        
        return best_threshold
    
    def predict(self, X: pd.DataFrame, threshold: Optional[float] = None) -> np.ndarray:
        """
        Realiza predicción binaria.
        """
        if self.best_model is None:
            raise ValueError("No hay modelo entrenado.")
        
        threshold = threshold or self.best_threshold
        proba = self.predict_proba(X)
        return (proba >= threshold).astype(int)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Realiza predicción de probabilidad.
        """
        if self.best_model is None:
            raise ValueError("No hay modelo entrenado.")
        
        return self.best_model.predict_proba(X)[:, 1]
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Retorna la importancia de features del mejor modelo.
        """
        if self.best_model is None:
            raise ValueError("No hay modelo entrenado.")
        
        if hasattr(self.best_model, 'feature_importances_'):
            importance = self.best_model.feature_importances_
        elif hasattr(self.best_model, 'coef_'):
            importance = np.abs(self.best_model.coef_[0])
        else:
            return pd.DataFrame()
        
        df_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return df_importance
    
    def save_model(self, model_path: str, metadata_path: str,
                  metrics: Optional[Dict[str, float]] = None,
                  metrics_source: str = "validation") -> None:
        """
        Guarda el modelo y metadata.
        """
        if self.best_model is None:
            raise ValueError("No hay modelo para guardar.")
        
        # Guardar modelo
        joblib.dump(self.best_model, model_path)
        print(f"✅ Modelo guardado en: {model_path}")
        
        # Guardar metadata
        metrics_payload = metrics if metrics is not None else self.metrics_history.get(self.best_model_name, {})
        metadata = {
            'model_name': self.best_model_name,
            'threshold': self.best_threshold,
            'feature_names': self.feature_names,
            'class_balance_ratio': self.class_balance_ratio,
            'metrics': metrics_payload,
            'metrics_source': metrics_source,
            'trained_at': datetime.now().isoformat(),
            'random_state': self.random_state
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"✅ Metadata guardada en: {metadata_path}")
    
    @classmethod
    def load_model(cls, model_path: str, metadata_path: str) -> 'FlightDelayModel':
        """
        Carga un modelo guardado.
        """
        instance = cls()
        
        # Cargar modelo
        instance.best_model = joblib.load(model_path)
        
        # Cargar metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        instance.best_model_name = metadata['model_name']
        instance.best_threshold = metadata['threshold']
        instance.feature_names = metadata['feature_names']
        instance.class_balance_ratio = metadata.get('class_balance_ratio', 1.0)
        
        return instance


class OutOfCoreXGBModel:
    """
    Wrapper para usar un Booster de XGBoost con una interfaz tipo sklearn.
    Se serializa guardando el modelo en bytes para compatibilidad con joblib.
    """

    def __init__(self, booster: Any, feature_names: List[str]):
        self._booster = booster
        self.feature_names = feature_names

    def __getstate__(self) -> Dict[str, Any]:
        return {
            'booster_bytes': self._booster.save_raw(),
            'feature_names': self.feature_names
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.feature_names = state['feature_names']
        self._booster = xgb.Booster()
        self._booster.load_model(state['booster_bytes'])

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            X_data = X[self.feature_names]
        else:
            X_data = X
        dmatrix = xgb.DMatrix(X_data, feature_names=self.feature_names)
        proba = self._booster.predict(dmatrix)
        return np.vstack([1 - proba, proba]).T

    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        proba = self.predict_proba(X)[:, 1]
        return (proba >= threshold).astype(int)


def cross_validate_model(model, X: pd.DataFrame, y: np.ndarray, 
                         cv: int = 5) -> Dict[str, float]:
    """
    Realiza validación cruzada estratificada.
    """
    cv_strategy = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    scores = {
        'accuracy': cross_val_score(model, X, y, cv=cv_strategy, scoring='accuracy'),
        'f1': cross_val_score(model, X, y, cv=cv_strategy, scoring='f1'),
        'precision': cross_val_score(model, X, y, cv=cv_strategy, scoring='precision'),
        'recall': cross_val_score(model, X, y, cv=cv_strategy, scoring='recall'),
        'roc_auc': cross_val_score(model, X, y, cv=cv_strategy, scoring='roc_auc'),
    }
    
    return {k: {'mean': v.mean(), 'std': v.std()} for k, v in scores.items()}
