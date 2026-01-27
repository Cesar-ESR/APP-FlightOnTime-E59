"""
FlightOnTime - Visualizaciones Interactivas con Plotly
=======================================================
Módulo para generar visualizaciones interactivas y animadas del modelo.

Autor: FlightOnTime Team
Fecha: 2026-01-13
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff

from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc, precision_recall_curve, average_precision_score
)


class InteractiveVisualizer:
    """Clase para crear visualizaciones interactivas con Plotly."""
    
    def __init__(self, figures_dir: str, metrics_dir: str):
        """Inicializa el visualizador."""
        self.figures_dir = Path(figures_dir)
        self.metrics_dir = Path(metrics_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Tema de colores profesional
        self.colors = {
            'primary': '#2E86DE',
            'success': '#10AC84',
            'danger': '#EE5A6F',
            'warning': '#F79F1F',
            'info': '#54A0FF',
            'dark': '#2C3E50',
            'light': '#ECF0F1'
        }
    
    def plot_confusion_matrix_interactive(self, y_true: np.ndarray, y_pred: np.ndarray,
                                         model_name: str, save: bool = True):
        """
        Genera matriz de confusión interactiva con animación.
        """
        cm = confusion_matrix(y_true, y_pred)
        
        # Crear figura
        fig = go.Figure()
        
        # Heatmap animado
        fig.add_trace(go.Heatmap(
            z=cm,
            x=['Puntual', 'Retrasado'],
            y=['Puntual', 'Retrasado'],
            colorscale=[
                [0, self.colors['success']],
                [0.5, self.colors['warning']],
                [1, self.colors['danger']]
            ],
            text=cm,
            texttemplate='<b>%{text}</b>',
            textfont={"size": 20, "color": "white"},
            hovertemplate='Real: %{y}<br>Predicción: %{x}<br>Cantidad: %{z}<extra></extra>',
            showscale=True,
            colorbar=dict(title="Cantidad", thickness=15)
        ))
        
        # Calcular métricas
        tn, fp, fn, tp = cm.ravel()
        total = tn + fp + fn + tp
        accuracy = (tp + tn) / total
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Título con métricas
        title_text = (
            f'<b>Matriz de Confusión - {model_name}</b><br>'
            f'<sub>Accuracy: {accuracy:.2%} | Precision: {precision:.2%} | '
            f'Recall: {recall:.2%} | F1: {f1:.2%}</sub>'
        )
        
        fig.update_layout(
            title=dict(text=title_text, x=0.5, xanchor='center'),
            xaxis_title='<b>Predicción</b>',
            yaxis_title='<b>Valor Real</b>',
            width=700,
            height=600,
            font=dict(size=14, family='Arial, sans-serif'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hoverlabel=dict(bgcolor="white", font_size=14)
        )
        
        if save:
            output_path = self.figures_dir / f'confusion_matrix_{model_name.lower()}_interactive.html'
            fig.write_html(str(output_path))
            print(f"✅ Matriz de confusión guardada: {output_path}")
        
        return fig
    
    def plot_roc_curve_interactive(self, y_true: np.ndarray, y_proba: np.ndarray,
                                   model_name: str, save: bool = True):
        """
        Genera curva ROC interactiva con animación.
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)
        
        fig = go.Figure()
        
        # Curva ROC con hover detallado
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr,
            mode='lines',
            name=f'ROC curve (AUC = {roc_auc:.4f})',
            line=dict(color=self.colors['primary'], width=3),
            fill='tozeroy',
            fillcolor=f"rgba(46, 134, 222, 0.2)",
            hovertemplate=(
                '<b>Threshold:</b> %{text:.4f}<br>'
                '<b>FPR:</b> %{x:.4f}<br>'
                '<b>TPR:</b> %{y:.4f}<br>'
                '<extra></extra>'
            ),
            text=thresholds
        ))
        
        # Línea de referencia (random classifier)
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='lines',
            name='Random Classifier',
            line=dict(color=self.colors['danger'], width=2, dash='dash'),
            hovertemplate='Random: FPR=%{x:.2f}, TPR=%{y:.2f}<extra></extra>'
        ))
        
        # Punto óptimo (Youden's J statistic)
        j_scores = tpr - fpr
        optimal_idx = np.argmax(j_scores)
        
        fig.add_trace(go.Scatter(
            x=[fpr[optimal_idx]],
            y=[tpr[optimal_idx]],
            mode='markers',
            name=f'Punto Óptimo (threshold={thresholds[optimal_idx]:.4f})',
            marker=dict(color=self.colors['success'], size=15, symbol='star'),
            hovertemplate=(
                f'<b>Punto Óptimo</b><br>'
                f'Threshold: {thresholds[optimal_idx]:.4f}<br>'
                f'FPR: {fpr[optimal_idx]:.4f}<br>'
                f'TPR: {tpr[optimal_idx]:.4f}<br>'
                '<extra></extra>'
            )
        ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>Curva ROC - {model_name}</b><br><sub>AUC = {roc_auc:.4f}</sub>',
                x=0.5,
                xanchor='center'
            ),
            xaxis_title='<b>False Positive Rate (1 - Specificity)</b>',
            yaxis_title='<b>True Positive Rate (Sensitivity/Recall)</b>',
            width=800,
            height=700,
            font=dict(size=14, family='Arial, sans-serif'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest',
            showlegend=True,
            legend=dict(x=0.6, y=0.1, bgcolor='rgba(255,255,255,0.8)')
        )
        
        fig.update_xaxes(range=[-0.05, 1.05], gridcolor='lightgray')
        fig.update_yaxes(range=[-0.05, 1.05], gridcolor='lightgray')
        
        if save:
            output_path = self.figures_dir / f'roc_curve_{model_name.lower()}_interactive.html'
            fig.write_html(str(output_path))
            print(f"✅ Curva ROC guardada: {output_path}")
        
        return fig
    
    def plot_pr_curve_interactive(self, y_true: np.ndarray, y_proba: np.ndarray,
                                  model_name: str, save: bool = True):
        """
        Genera curva Precision-Recall interactiva.
        """
        precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
        pr_auc = average_precision_score(y_true, y_proba)
        
        fig = go.Figure()
        
        # Curva PR
        fig.add_trace(go.Scatter(
            x=recall,
            y=precision,
            mode='lines',
            name=f'PR curve (AP = {pr_auc:.4f})',
            line=dict(color=self.colors['info'], width=3),
            fill='tozeroy',
            fillcolor=f"rgba(84, 160, 255, 0.2)",
            hovertemplate=(
                '<b>Threshold:</b> %{text:.4f}<br>'
                '<b>Recall:</b> %{x:.4f}<br>'
                '<b>Precision:</b> %{y:.4f}<br>'
                '<extra></extra>'
            ),
            text=np.append(thresholds, thresholds[-1])  # Añadir threshold para el último punto
        ))
        
        # Baseline (proporción de positivos)
        baseline = y_true.mean()
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[baseline, baseline],
            mode='lines',
            name=f'Baseline ({baseline:.2%})',
            line=dict(color=self.colors['danger'], width=2, dash='dash'),
            hovertemplate=f'Baseline: {baseline:.2%}<extra></extra>'
        ))
        
        # Punto con mejor F1
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        best_idx = np.argmax(f1_scores)
        
        fig.add_trace(go.Scatter(
            x=[recall[best_idx]],
            y=[precision[best_idx]],
            mode='markers',
            name=f'Mejor F1 ({f1_scores[best_idx]:.4f})',
            marker=dict(color=self.colors['success'], size=15, symbol='star'),
            hovertemplate=(
                f'<b>Mejor F1-Score</b><br>'
                f'F1: {f1_scores[best_idx]:.4f}<br>'
                f'Precision: {precision[best_idx]:.4f}<br>'
                f'Recall: {recall[best_idx]:.4f}<br>'
                '<extra></extra>'
            )
        ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>Curva Precision-Recall - {model_name}</b><br><sub>Average Precision = {pr_auc:.4f}</sub>',
                x=0.5,
                xanchor='center'
            ),
            xaxis_title='<b>Recall (Sensitivity)</b>',
            yaxis_title='<b>Precision (PPV)</b>',
            width=800,
            height=700,
            font=dict(size=14, family='Arial, sans-serif'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest',
            showlegend=True,
            legend=dict(x=0.6, y=0.9, bgcolor='rgba(255,255,255,0.8)')
        )
        
        fig.update_xaxes(range=[-0.05, 1.05], gridcolor='lightgray')
        fig.update_yaxes(range=[-0.05, 1.05], gridcolor='lightgray')
        
        if save:
            output_path = self.figures_dir / f'pr_curve_{model_name.lower()}_interactive.html'
            fig.write_html(str(output_path))
            print(f"✅ Curva PR guardada: {output_path}")
        
        return fig
    
    def plot_feature_importance_interactive(self, importance_df: pd.DataFrame,
                                           model_name: str, top_n: int = 17,
                                           save: bool = True):
        """
        Genera gráfico de importancia de features interactivo con animación.
        """
        # Ordenar y tomar top N
        importance_df = importance_df.nlargest(top_n, 'importance')
        
        # Crear figura con animación
        fig = go.Figure()
        
        # Barras horizontales con gradiente
        colors = px.colors.sequential.Blues_r[:len(importance_df)]
        
        fig.add_trace(go.Bar(
            x=importance_df['importance'],
            y=importance_df['feature'],
            orientation='h',
            marker=dict(
                color=importance_df['importance'],
                colorscale='Blues',
                line=dict(color=self.colors['dark'], width=1.5),
                showscale=True,
                colorbar=dict(title="Importancia", thickness=15)
            ),
            text=importance_df['importance'].apply(lambda x: f'{x:.1%}'),
            textposition='outside',
            textfont=dict(size=12, color=self.colors['dark'], family='Arial Black'),
            hovertemplate=(
                '<b>%{y}</b><br>'
                'Importancia: %{x:.2%}<br>'
                '<extra></extra>'
            )
        ))
        
        fig.update_layout(
            title=dict(
                text=f'<b>Importancia de Features - {model_name}</b><br><sub>Top {len(importance_df)} Features</sub>',
                x=0.5,
                xanchor='center'
            ),
            xaxis_title='<b>Importancia Relativa (%)</b>',
            yaxis_title='',
            width=1000,
            height=600,
            font=dict(size=14, family='Arial, sans-serif'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest',
            showlegend=False
        )
        
        fig.update_xaxes(gridcolor='lightgray', tickformat='.0%')
        fig.update_yaxes(categoryorder='total ascending')
        
        if save:
            output_path = self.figures_dir / f'feature_importance_{model_name.lower()}_interactive.html'
            fig.write_html(str(output_path))
            print(f"✅ Feature importance guardado: {output_path}")
        
        return fig
    
    def plot_threshold_analysis_interactive(self, y_true: np.ndarray, y_proba: np.ndarray,
                                           model_name: str, save: bool = True):
        """
        Genera análisis interactivo del impacto del umbral.
        """
        thresholds = np.arange(0.1, 0.95, 0.01)
        metrics = []
        
        for threshold in thresholds:
            y_pred = (y_proba >= threshold).astype(int)
            cm = confusion_matrix(y_true, y_pred)
            tn, fp, fn, tp = cm.ravel()
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            metrics.append({
                'threshold': threshold,
                'precision': precision,
                'recall': recall,
                'f1': f1
            })
        
        df = pd.DataFrame(metrics)
        
        # Crear subplot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Precision, Recall y F1-Score vs Threshold', 'Trade-off Precision-Recall'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )
        
        # Gráfico 1: Métricas vs Threshold
        fig.add_trace(go.Scatter(
            x=df['threshold'],
            y=df['precision'],
            mode='lines',
            name='Precision',
            line=dict(color=self.colors['primary'], width=3),
            hovertemplate='Threshold: %{x:.3f}<br>Precision: %{y:.3f}<extra></extra>'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['threshold'],
            y=df['recall'],
            mode='lines',
            name='Recall',
            line=dict(color=self.colors['success'], width=3),
            hovertemplate='Threshold: %{x:.3f}<br>Recall: %{y:.3f}<extra></extra>'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['threshold'],
            y=df['f1'],
            mode='lines',
            name='F1-Score',
            line=dict(color=self.colors['danger'], width=3),
            hovertemplate='Threshold: %{x:.3f}<br>F1: %{y:.3f}<extra></extra>'
        ), row=1, col=1)
        
        # Marcar threshold óptimo (max F1)
        best_idx = df['f1'].idxmax()
        best_threshold = df.loc[best_idx, 'threshold']
        
        fig.add_vline(
            x=best_threshold,
            line_dash="dash",
            line_color=self.colors['warning'],
            annotation_text=f"Óptimo: {best_threshold:.3f}",
            annotation_position="top",
            row=1, col=1
        )
        
        # Gráfico 2: Precision vs Recall
        fig.add_trace(go.Scatter(
            x=df['recall'],
            y=df['precision'],
            mode='lines+markers',
            name='Trade-off',
            line=dict(color=self.colors['info'], width=3),
            marker=dict(size=4),
            hovertemplate='Recall: %{x:.3f}<br>Precision: %{y:.3f}<br>Threshold: %{text:.3f}<extra></extra>',
            text=df['threshold']
        ), row=2, col=1)
        
        # Marcar punto óptimo
        fig.add_trace(go.Scatter(
            x=[df.loc[best_idx, 'recall']],
            y=[df.loc[best_idx, 'precision']],
            mode='markers',
            name=f'Óptimo ({best_threshold:.3f})',
            marker=dict(color=self.colors['warning'], size=15, symbol='star'),
            hovertemplate=(
                f'<b>Punto Óptimo</b><br>'
                f'Threshold: {best_threshold:.3f}<br>'
                f'Precision: {df.loc[best_idx, "precision"]:.3f}<br>'
                f'Recall: {df.loc[best_idx, "recall"]:.3f}<br>'
                '<extra></extra>'
            )
        ), row=2, col=1)
        
        fig.update_layout(
            title=dict(
                text=f'<b>Análisis de Threshold - {model_name}</b>',
                x=0.5,
                xanchor='center'
            ),
            width=1000,
            height=900,
            font=dict(size=14, family='Arial, sans-serif'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest',
            showlegend=True,
            legend=dict(x=0.7, y=0.95, bgcolor='rgba(255,255,255,0.8)')
        )
        
        fig.update_xaxes(title_text="<b>Threshold</b>", gridcolor='lightgray', row=1, col=1)
        fig.update_yaxes(title_text="<b>Score</b>", gridcolor='lightgray', row=1, col=1)
        fig.update_xaxes(title_text="<b>Recall</b>", gridcolor='lightgray', row=2, col=1)
        fig.update_yaxes(title_text="<b>Precision</b>", gridcolor='lightgray', row=2, col=1)
        
        if save:
            output_path = self.figures_dir / f'threshold_analysis_{model_name.lower()}_interactive.html'
            fig.write_html(str(output_path))
            print(f"✅ Threshold analysis guardado: {output_path}")
        
        return fig
    
    def plot_models_comparison_interactive(self, results: Dict[str, Dict], save: bool = True):
        """
        Genera comparación interactiva de modelos con animación.
        """
        metrics_df = pd.DataFrame(results).T
        
        # Crear figura con barras agrupadas
        fig = go.Figure()
        
        metrics = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        colors_map = {
            'accuracy': self.colors['primary'],
            'precision': self.colors['success'],
            'recall': self.colors['info'],
            'f1': self.colors['danger'],
            'roc_auc': self.colors['warning']
        }
        
        for metric in metrics:
            fig.add_trace(go.Bar(
                name=metric.replace('_', ' ').upper(),
                x=metrics_df.index,
                y=metrics_df[metric],
                marker_color=colors_map[metric],
                text=metrics_df[metric].apply(lambda x: f'{x:.3f}'),
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate=(
                    f'<b>{metric.upper()}</b><br>'
                    'Modelo: %{x}<br>'
                    'Valor: %{y:.4f}<br>'
                    '<extra></extra>'
                )
            ))
        
        fig.update_layout(
            title=dict(
                text='<b>Comparación de Modelos</b><br><sub>Métricas de Performance</sub>',
                x=0.5,
                xanchor='center'
            ),
            xaxis_title='<b>Modelo</b>',
            yaxis_title='<b>Score</b>',
            width=1100,
            height=700,
            font=dict(size=14, family='Arial, sans-serif'),
            plot_bgcolor='white',
            paper_bgcolor='white',
            barmode='group',
            hovermode='closest',
            showlegend=True,
            legend=dict(x=1.02, y=1, bgcolor='rgba(255,255,255,0.8)')
        )
        
        fig.update_yaxes(range=[0, 1], gridcolor='lightgray', tickformat='.2f')
        fig.update_xaxes(gridcolor='lightgray')
        
        if save:
            output_path = self.figures_dir / 'models_comparison_interactive.html'
            fig.write_html(str(output_path))
            print(f"✅ Models comparison guardado: {output_path}")
        
        return fig
    
    def create_dashboard(self, model, X_test, y_test, results, importance_df, model_name='XGBoost'):
        """
        Crea un dashboard completo con todas las visualizaciones.
        """
        print("\n" + "="*70)
        print("📊 GENERANDO DASHBOARD INTERACTIVO")
        print("="*70)
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        # Generar todas las visualizaciones
        self.plot_confusion_matrix_interactive(y_test, y_pred, model_name)
        self.plot_roc_curve_interactive(y_test, y_proba, model_name)
        self.plot_pr_curve_interactive(y_test, y_proba, model_name)
        self.plot_feature_importance_interactive(importance_df, model_name)
        self.plot_threshold_analysis_interactive(y_test, y_proba, model_name)
        self.plot_models_comparison_interactive(results)
        
        print("\n✅ Dashboard completo generado")
        print(f"📁 Visualizaciones guardadas en: {self.figures_dir}")
