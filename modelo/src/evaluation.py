"""
FlightOnTime - Evaluación
=========================
Módulo para evaluación de modelos con visualizaciones y reportes.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve, average_precision_score
)

# Configuración de estilo
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


class ModelEvaluator:
    """
    Clase para evaluar y visualizar resultados de modelos.
    """
    
    def __init__(self, figures_dir: str, metrics_dir: str):
        self.figures_dir = Path(figures_dir)
        self.metrics_dir = Path(metrics_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray,
                              model_name: str, save: bool = True) -> None:
        """
        Genera visualización de matriz de confusión.
        """
        cm = confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Puntual', 'Retrasado'],
            yticklabels=['Puntual', 'Retrasado'],
            ax=ax
        )
        ax.set_xlabel('Predicción', fontsize=12)
        ax.set_ylabel('Real', fontsize=12)
        ax.set_title(f'Matriz de Confusión - {model_name}', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            path = self.figures_dir / f'confusion_matrix_{model_name.lower().replace(" ", "_")}.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            print(f"✅ Guardado: {path}")
        
        plt.close()
    
    def plot_roc_curve(self, y_true: np.ndarray, y_proba: np.ndarray,
                       model_name: str, save: bool = True) -> float:
        """
        Genera curva ROC.
        """
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Aleatorio')
        ax.fill_between(fpr, tpr, alpha=0.3, color='darkorange')
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('Tasa de Falsos Positivos', fontsize=12)
        ax.set_ylabel('Tasa de Verdaderos Positivos', fontsize=12)
        ax.set_title(f'Curva ROC - {model_name}', fontsize=14)
        ax.legend(loc='lower right')
        
        plt.tight_layout()
        
        if save:
            path = self.figures_dir / f'roc_curve_{model_name.lower().replace(" ", "_")}.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            print(f"✅ Guardado: {path}")
        
        plt.close()
        return roc_auc
    
    def plot_precision_recall_curve(self, y_true: np.ndarray, y_proba: np.ndarray,
                                     model_name: str, save: bool = True) -> float:
        """
        Genera curva Precision-Recall.
        """
        precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
        pr_auc = average_precision_score(y_true, y_proba)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(recall, precision, color='green', lw=2, 
                label=f'PR (AUC = {pr_auc:.3f})')
        
        # Línea base (proporción de positivos)
        baseline = np.sum(y_true) / len(y_true)
        ax.axhline(y=baseline, color='gray', linestyle='--', 
                   label=f'Baseline = {baseline:.3f}')
        
        ax.fill_between(recall, precision, alpha=0.3, color='green')
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title(f'Curva Precision-Recall - {model_name}', fontsize=14)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        
        if save:
            path = self.figures_dir / f'pr_curve_{model_name.lower().replace(" ", "_")}.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            print(f"✅ Guardado: {path}")
        
        plt.close()
        return pr_auc
    
    def plot_feature_importance(self, importance_df: pd.DataFrame,
                                model_name: str, top_n: int = 15,
                                save: bool = True) -> None:
        """
        Genera gráfico de importancia de features.
        """
        df_top = importance_df.head(top_n)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df_top)))
        
        bars = ax.barh(df_top['feature'], df_top['importance'], color=colors)
        ax.set_xlabel('Importancia', fontsize=12)
        ax.set_ylabel('Feature', fontsize=12)
        ax.set_title(f'Top {top_n} Features Más Importantes - {model_name}', fontsize=14)
        ax.invert_yaxis()
        
        # Añadir valores
        for bar, val in zip(bars, df_top['importance']):
            ax.text(val + 0.001, bar.get_y() + bar.get_height()/2, 
                   f'{val:.4f}', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            path = self.figures_dir / f'feature_importance_{model_name.lower().replace(" ", "_")}.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            print(f"✅ Guardado: {path}")
        
        plt.close()
    
    def plot_threshold_analysis(self, y_true: np.ndarray, y_proba: np.ndarray,
                                model_name: str, save: bool = True) -> None:
        """
        Analiza el impacto del umbral de decisión.
        """
        thresholds = np.arange(0.1, 0.9, 0.05)
        precisions = []
        recalls = []
        f1s = []
        
        for t in thresholds:
            y_pred = (y_proba >= t).astype(int)
            
            tp = np.sum((y_pred == 1) & (y_true == 1))
            fp = np.sum((y_pred == 1) & (y_true == 0))
            fn = np.sum((y_pred == 0) & (y_true == 1))
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            precisions.append(precision)
            recalls.append(recall)
            f1s.append(f1)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(thresholds, precisions, 'b-', lw=2, label='Precision')
        ax.plot(thresholds, recalls, 'g-', lw=2, label='Recall')
        ax.plot(thresholds, f1s, 'r--', lw=2, label='F1-Score')
        
        # Marcar umbral óptimo (max F1)
        best_idx = np.argmax(f1s)
        best_threshold = thresholds[best_idx]
        ax.axvline(x=best_threshold, color='gray', linestyle=':', 
                   label=f'Umbral óptimo = {best_threshold:.2f}')
        
        ax.set_xlabel('Umbral de Decisión', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(f'Análisis de Umbral - {model_name}', fontsize=14)
        ax.legend(loc='center right')
        ax.set_xlim([0.1, 0.9])
        ax.set_ylim([0, 1])
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            path = self.figures_dir / f'threshold_analysis_{model_name.lower().replace(" ", "_")}.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            print(f"✅ Guardado: {path}")
        
        plt.close()
    
    def plot_models_comparison(self, results: Dict[str, Dict],
                               save: bool = True) -> None:
        """
        Compara métricas de todos los modelos.
        """
        metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        
        models = []
        data = {m: [] for m in metrics_to_plot}
        
        for name, metrics in results.items():
            if 'error' not in metrics:
                models.append(name)
                for m in metrics_to_plot:
                    data[m].append(metrics.get(m, 0))
        
        if not models:
            print("⚠️ No hay modelos para comparar")
            return
        
        x = np.arange(len(models))
        width = 0.15
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(metrics_to_plot)))
        
        for i, (metric, color) in enumerate(zip(metrics_to_plot, colors)):
            offset = (i - len(metrics_to_plot)/2) * width
            bars = ax.bar(x + offset, data[metric], width, label=metric.upper(), color=color)
            
            # Añadir valores
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.2f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8, rotation=45)
        
        ax.set_xlabel('Modelo', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Comparación de Modelos', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.set_ylim([0, 1.15])
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save:
            path = self.figures_dir / 'models_comparison.png'
            plt.savefig(path, dpi=150, bbox_inches='tight')
            print(f"✅ Guardado: {path}")
        
        plt.close()
    
    def save_metrics_report(self, results: Dict[str, Dict], 
                            best_model_name: str) -> None:
        """
        Guarda reporte de métricas en formato JSON y Markdown.
        """
        # JSON
        json_path = self.metrics_dir / 'evaluation_results.json'
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"✅ Guardado: {json_path}")
        
        # Markdown
        md_path = self.metrics_dir / 'evaluation_report.md'
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 Reporte de Evaluación de Modelos\n\n")
            f.write(f"**Mejor Modelo:** {best_model_name}\n\n")
            
            f.write("## Comparación de Modelos\n\n")
            f.write("| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |\n")
            f.write("|--------|----------|-----------|--------|----|---------|\n")
            
            for name, metrics in results.items():
                if 'error' not in metrics:
                    f.write(f"| {name} | {metrics['accuracy']:.4f} | ")
                    f.write(f"{metrics['precision']:.4f} | {metrics['recall']:.4f} | ")
                    f.write(f"{metrics['f1']:.4f} | {metrics['roc_auc']:.4f} |\n")
            
            f.write(f"\n## Modelo Seleccionado: {best_model_name}\n\n")
            
            if best_model_name in results:
                m = results[best_model_name]
                f.write("### Métricas Detalladas\n\n")
                f.write(f"- **Accuracy:** {m['accuracy']:.4f}\n")
                f.write(f"- **Precision:** {m['precision']:.4f}\n")
                f.write(f"- **Recall:** {m['recall']:.4f}\n")
                f.write(f"- **F1-Score:** {m['f1']:.4f}\n")
                f.write(f"- **ROC-AUC:** {m['roc_auc']:.4f}\n")
                f.write(f"- **PR-AUC:** {m['pr_auc']:.4f}\n\n")
                
                if 'confusion_matrix' in m:
                    cm = m['confusion_matrix']
                    f.write("### Matriz de Confusión\n\n")
                    f.write("```\n")
                    f.write(f"                  Predicción\n")
                    f.write(f"                  Puntual  Retrasado\n")
                    f.write(f"Real  Puntual    {cm[0][0]:7d}  {cm[0][1]:7d}\n")
                    f.write(f"      Retrasado  {cm[1][0]:7d}  {cm[1][1]:7d}\n")
                    f.write("```\n\n")
                
                f.write("### Interpretación\n\n")
                f.write(f"- **Verdaderos Negativos (Puntuales correctos):** {m['true_negatives']:,}\n")
                f.write(f"- **Falsos Positivos (Alertas falsas):** {m['false_positives']:,}\n")
                f.write(f"- **Falsos Negativos (Retrasos no detectados):** {m['false_negatives']:,}\n")
                f.write(f"- **Verdaderos Positivos (Retrasos detectados):** {m['true_positives']:,}\n")
        
        print(f"✅ Guardado: {md_path}")
    
    def generate_full_report(self, model, X_test: pd.DataFrame, y_test: np.ndarray,
                             results: Dict[str, Dict], importance_df: pd.DataFrame) -> None:
        """
        Genera reporte completo con todas las visualizaciones.
        """
        model_name = model.best_model_name
        y_proba = model.predict_proba(X_test)
        y_pred = model.predict(X_test)
        
        print("\n📊 Generando visualizaciones...")
        
        # Matriz de confusión
        self.plot_confusion_matrix(y_test, y_pred, model_name)
        
        # Curva ROC
        self.plot_roc_curve(y_test, y_proba, model_name)
        
        # Curva PR
        self.plot_precision_recall_curve(y_test, y_proba, model_name)
        
        # Importancia de features
        if not importance_df.empty:
            self.plot_feature_importance(importance_df, model_name)
        
        # Análisis de umbral
        self.plot_threshold_analysis(y_test, y_proba, model_name)
        
        # Comparación de modelos
        self.plot_models_comparison(results)
        
        # Reporte de métricas
        self.save_metrics_report(results, model_name)
        
        print("\n✅ Reporte completo generado")
