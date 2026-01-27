"""
FlightOnTime - Optimizador de Umbral
=====================================
Script para analizar y optimizar el umbral de decisión del modelo
para maximizar recall, precision o encontrar el mejor balance.

Uso:
    python optimize_threshold.py

Autor: FlightOnTime Team
Fecha: 2026-01-13
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import joblib
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

# Configuración
MODEL_PATH = Path("models/model.joblib")
METADATA_PATH = Path("models/metadata.json")
FEATURE_ENGINEER_PATH = Path("models/feature_engineer.joblib")
TRAINING_INFO_PATH = Path("models/training_info.json")
DATASET_PATH = Path("0.0. DATASET ORIGINAL/dataset_prepared.parquet")

# Configuración de visualización
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 10)


class ThresholdOptimizer:
    """Optimizador de umbral para el modelo de predicción."""
    
    def __init__(self):
        """Inicializa el optimizador."""
        print("🔄 Cargando modelo y datos...")
        
        # Cargar modelo
        self.model = joblib.load(MODEL_PATH)
        
        # Cargar feature engineer
        self.feature_engineer = joblib.load(FEATURE_ENGINEER_PATH)
        
        # Cargar metadata
        with open(METADATA_PATH, 'r') as f:
            self.metadata = json.load(f)
        
        # Cargar training info
        with open(TRAINING_INFO_PATH, 'r') as f:
            self.training_info = json.load(f)
        
        self.current_threshold = float(self.metadata['threshold'])
        self.features = self.metadata['feature_names']
        
        print(f"✅ Umbral actual: {self.current_threshold:.4f}")
        print(f"✅ Features: {len(self.features)}")
    
    def load_test_data(self, sample_size=None):
        """
        Carga datos de test para optimización.
        
        Args:
            sample_size (int): Tamaño de muestra (None = usar todos los datos de test)
        """
        print("\n📊 Cargando datos de test...")
        
        # Cargar dataset completo
        df = pd.read_parquet(DATASET_PATH)
        
        # Tomar muestra primero si es necesario (antes de split para ser más rápido)
        if sample_size and len(df) > sample_size * 10:
            # Muestra estratificada del dataset completo
            from sklearn.model_selection import train_test_split
            df, _ = train_test_split(
                df,
                train_size=sample_size * 10,  # 10x para asegurar suficientes datos después del split
                random_state=42,
                stratify=df['DEP_DEL15'] if 'DEP_DEL15' in df.columns else None
            )
        
        print(f"✅ Dataset cargado: {len(df):,} registros")
        
        # Procesar con feature engineer
        print("🔧 Procesando features...")
        
        # Normalizar nombres de columnas
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
        df = df.rename(columns=cols_to_rename)
        
        # Limpiar precipitación
        if 'precip_1h' in df.columns:
            df['precip_1h'] = df['precip_1h'].replace(-1, 0)
        
        # Codificar categóricas
        categorical_cols = ['op_unique_carrier', 'origin', 'dest']
        for col in categorical_cols:
            if col in df.columns:
                df = self.feature_engineer.transform_categorical(df)
                break
        
        # Extraer target
        y = df['DEP_DEL15'].values if 'DEP_DEL15' in df.columns else df['is_delayed'].values
        
        # Dividir en train/test (solo necesitamos test)
        from sklearn.model_selection import train_test_split
        X_temp, X_test, y_temp, y_test = train_test_split(
            df,
            y,
            test_size=0.15,  # 15% como en el entrenamiento
            random_state=42,
            stratify=y
        )
        
        # Si sample_size es específico, tomar muestra del test set
        if sample_size and len(X_test) > sample_size:
            X_test = X_test.sample(n=sample_size, random_state=42)
            y_test = X_test['DEP_DEL15'].values if 'DEP_DEL15' in X_test.columns else X_test['is_delayed'].values
        
        print(f"✅ Test set preparado: {len(X_test):,} registros")
        
        # Seleccionar solo las features del modelo
        X_test_features = X_test[self.features]
        
        return X_test_features, y_test
    
    def analyze_thresholds(self, X_test, y_test, thresholds=None):
        """
        Analiza diferentes umbrales y sus métricas.
        
        Args:
            X_test: Features de test
            y_test: Labels de test
            thresholds: Lista de umbrales a probar (None = automático)
        
        Returns:
            pd.DataFrame: Resultados por umbral
        """
        print("\n🔍 Analizando umbrales...")
        
        # Obtener probabilidades
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Umbrales a probar
        if thresholds is None:
            thresholds = np.arange(0.1, 0.95, 0.01)
        
        results = []
        
        for threshold in thresholds:
            y_pred = (y_proba >= threshold).astype(int)
            
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            # Matriz de confusión
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel()
            
            # Métricas adicionales
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
            fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
            
            results.append({
                'threshold': threshold,
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'specificity': specificity,
                'false_positive_rate': fpr,
                'false_negative_rate': fnr,
                'true_positives': tp,
                'false_positives': fp,
                'true_negatives': tn,
                'false_negatives': fn
            })
        
        df_results = pd.DataFrame(results)
        print(f"✅ {len(df_results)} umbrales analizados")
        
        return df_results
    
    def find_optimal_thresholds(self, df_results):
        """
        Encuentra los umbrales óptimos según diferentes criterios.
        
        Args:
            df_results: DataFrame con resultados de umbrales
        
        Returns:
            dict: Umbrales óptimos por criterio
        """
        optimal = {}
        
        # Máximo F1-Score
        idx_max_f1 = df_results['f1'].idxmax()
        optimal['max_f1'] = {
            'threshold': df_results.loc[idx_max_f1, 'threshold'],
            'precision': df_results.loc[idx_max_f1, 'precision'],
            'recall': df_results.loc[idx_max_f1, 'recall'],
            'f1': df_results.loc[idx_max_f1, 'f1']
        }
        
        # Máximo Recall (detectar más retrasos)
        idx_max_recall = df_results['recall'].idxmax()
        optimal['max_recall'] = {
            'threshold': df_results.loc[idx_max_recall, 'threshold'],
            'precision': df_results.loc[idx_max_recall, 'precision'],
            'recall': df_results.loc[idx_max_recall, 'recall'],
            'f1': df_results.loc[idx_max_recall, 'f1']
        }
        
        # Máxima Precision (menos falsas alarmas)
        # Con recall mínimo de 0.3
        df_high_recall = df_results[df_results['recall'] >= 0.3]
        if len(df_high_recall) > 0:
            idx_max_precision = df_high_recall['precision'].idxmax()
            optimal['max_precision'] = {
                'threshold': df_high_recall.loc[idx_max_precision, 'threshold'],
                'precision': df_high_recall.loc[idx_max_precision, 'precision'],
                'recall': df_high_recall.loc[idx_max_precision, 'recall'],
                'f1': df_high_recall.loc[idx_max_precision, 'f1']
            }
        
        # Balance 50/50 entre Precision y Recall
        df_results['balance'] = abs(df_results['precision'] - df_results['recall'])
        idx_balanced = df_results['balance'].idxmin()
        optimal['balanced'] = {
            'threshold': df_results.loc[idx_balanced, 'threshold'],
            'precision': df_results.loc[idx_balanced, 'precision'],
            'recall': df_results.loc[idx_balanced, 'recall'],
            'f1': df_results.loc[idx_balanced, 'f1']
        }
        
        # Objetivo: Recall >= 60%, máxima Precision
        df_high_recall_60 = df_results[df_results['recall'] >= 0.60]
        if len(df_high_recall_60) > 0:
            idx_recall_60 = df_high_recall_60['precision'].idxmax()
            optimal['recall_60_plus'] = {
                'threshold': df_high_recall_60.loc[idx_recall_60, 'threshold'],
                'precision': df_high_recall_60.loc[idx_recall_60, 'precision'],
                'recall': df_high_recall_60.loc[idx_recall_60, 'recall'],
                'f1': df_high_recall_60.loc[idx_recall_60, 'f1']
            }
        
        return optimal
    
    def visualize_thresholds(self, df_results, optimal_thresholds):
        """Genera visualizaciones del análisis de umbrales."""
        print("\n📊 Generando visualizaciones...")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Precision, Recall y F1 vs Threshold
        ax1 = axes[0, 0]
        ax1.plot(df_results['threshold'], df_results['precision'], 
                label='Precision', linewidth=2, color='blue')
        ax1.plot(df_results['threshold'], df_results['recall'], 
                label='Recall', linewidth=2, color='green')
        ax1.plot(df_results['threshold'], df_results['f1'], 
                label='F1-Score', linewidth=2, color='red')
        
        # Marcar umbrales óptimos
        for name, opt in optimal_thresholds.items():
            ax1.axvline(opt['threshold'], linestyle='--', alpha=0.3)
        
        # Umbral actual
        ax1.axvline(self.current_threshold, color='black', 
                   linestyle='--', linewidth=2, label=f'Actual ({self.current_threshold:.3f})')
        
        ax1.set_xlabel('Threshold', fontsize=12)
        ax1.set_ylabel('Score', fontsize=12)
        ax1.set_title('Métricas vs Threshold', fontsize=14, fontweight='bold')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # 2. FPR y FNR vs Threshold
        ax2 = axes[0, 1]
        ax2.plot(df_results['threshold'], df_results['false_positive_rate'], 
                label='False Positive Rate', linewidth=2, color='orange')
        ax2.plot(df_results['threshold'], df_results['false_negative_rate'], 
                label='False Negative Rate', linewidth=2, color='purple')
        ax2.axvline(self.current_threshold, color='black', 
                   linestyle='--', linewidth=2, label=f'Actual ({self.current_threshold:.3f})')
        ax2.set_xlabel('Threshold', fontsize=12)
        ax2.set_ylabel('Rate', fontsize=12)
        ax2.set_title('Tasas de Error vs Threshold', fontsize=14, fontweight='bold')
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        # 3. Precision-Recall Trade-off
        ax3 = axes[1, 0]
        ax3.plot(df_results['recall'], df_results['precision'], 
                linewidth=2, color='darkblue')
        
        # Marcar puntos óptimos
        for name, opt in optimal_thresholds.items():
            ax3.plot(opt['recall'], opt['precision'], 'o', 
                    markersize=10, label=f"{name}: {opt['threshold']:.3f}")
        
        ax3.set_xlabel('Recall', fontsize=12)
        ax3.set_ylabel('Precision', fontsize=12)
        ax3.set_title('Precision-Recall Trade-off', fontsize=14, fontweight='bold')
        ax3.legend(loc='best', fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # 4. Tabla de umbrales recomendados
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        table_data = []
        for name, opt in optimal_thresholds.items():
            table_data.append([
                name.replace('_', ' ').title(),
                f"{opt['threshold']:.4f}",
                f"{opt['precision']:.3f}",
                f"{opt['recall']:.3f}",
                f"{opt['f1']:.3f}"
            ])
        
        table = ax4.table(
            cellText=table_data,
            colLabels=['Estrategia', 'Threshold', 'Precision', 'Recall', 'F1'],
            cellLoc='center',
            loc='center',
            colWidths=[0.25, 0.15, 0.15, 0.15, 0.15]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Estilo de la tabla
        for i in range(len(table_data) + 1):
            for j in range(5):
                cell = table[(i, j)]
                if i == 0:
                    cell.set_facecolor('#4472C4')
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor('#E7E6E6' if i % 2 == 0 else 'white')
        
        ax4.set_title('Umbrales Recomendados', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Guardar
        output_path = Path("outputs/figures/threshold_optimization.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Gráfico guardado: {output_path}")
        
        plt.close()
    
    def print_recommendations(self, optimal_thresholds):
        """Imprime recomendaciones de umbrales."""
        print("\n" + "="*70)
        print("🎯 UMBRALES RECOMENDADOS")
        print("="*70)
        
        print(f"\n📊 Umbral actual del modelo: {self.current_threshold:.4f}")
        
        for name, opt in optimal_thresholds.items():
            print(f"\n{'─'*70}")
            print(f"🔹 {name.replace('_', ' ').upper()}")
            print(f"{'─'*70}")
            print(f"   Threshold:  {opt['threshold']:.4f}")
            print(f"   Precision:  {opt['precision']:.3f} ({opt['precision']*100:.1f}%)")
            print(f"   Recall:     {opt['recall']:.3f} ({opt['recall']*100:.1f}%)")
            print(f"   F1-Score:   {opt['f1']:.3f}")
            
            # Interpretación
            if 'max_recall' in name:
                print(f"   💡 Mejor para: Maximizar detección de retrasos")
            elif 'max_precision' in name:
                print(f"   💡 Mejor para: Minimizar falsas alarmas")
            elif 'balanced' in name:
                print(f"   💡 Mejor para: Balance entre precision y recall")
            elif 'max_f1' in name:
                print(f"   💡 Mejor para: Mejor métrica general (recomendado)")
            elif 'recall_60' in name:
                print(f"   💡 Mejor para: Detectar 60%+ de retrasos con máxima precisión")
    
    def save_recommendations(self, optimal_thresholds, df_results):
        """Guarda las recomendaciones en un archivo JSON."""
        output = {
            'current_threshold': self.current_threshold,
            'analysis_date': pd.Timestamp.now().isoformat(),
            'optimal_thresholds': optimal_thresholds,
            'all_thresholds': df_results.to_dict(orient='records')
        }
        
        output_path = Path("outputs/metrics/threshold_optimization.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✅ Recomendaciones guardadas: {output_path}")


def main():
    """Función principal."""
    print("="*70)
    print("🎯 OPTIMIZADOR DE UMBRAL - FLIGHTONTIME")
    print("="*70)
    
    try:
        # Inicializar optimizador
        optimizer = ThresholdOptimizer()
        
        # Preguntar tamaño de muestra
        print("\n📝 ¿Cuántos registros usar para optimización?")
        print("   (Usar menos registros es más rápido pero menos preciso)")
        print("   Opciones:")
        print("   1. 100,000 registros (rápido, ~1 min)")
        print("   2. 500,000 registros (medio, ~3 min)")
        print("   3. 2,250,000 registros - Test completo (lento, ~8 min)")
        
        opcion = input("\nSeleccione (1-3) [1]: ").strip() or "1"
        
        sample_sizes = {
            '1': 100_000,
            '2': 500_000,
            '3': None  # Todos
        }
        
        sample_size = sample_sizes.get(opcion, 100_000)
        
        # Cargar datos
        X_test, y_test = optimizer.load_test_data(sample_size)
        
        # Analizar umbrales
        df_results = optimizer.analyze_thresholds(X_test, y_test)
        
        # Encontrar óptimos
        optimal_thresholds = optimizer.find_optimal_thresholds(df_results)
        
        # Imprimir recomendaciones
        optimizer.print_recommendations(optimal_thresholds)
        
        # Visualizar
        optimizer.visualize_thresholds(df_results, optimal_thresholds)
        
        # Guardar
        optimizer.save_recommendations(optimal_thresholds, df_results)
        
        print("\n" + "="*70)
        print("✅ OPTIMIZACIÓN COMPLETADA")
        print("="*70)
        print("\n📊 Salidas generadas:")
        print("   - outputs/figures/threshold_optimization.png")
        print("   - outputs/metrics/threshold_optimization.json")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Optimización cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
