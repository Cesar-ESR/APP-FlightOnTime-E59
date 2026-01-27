# ✈️ FlightOnTime - Predicción de Retrasos de Vuelos

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-green.svg)](https://xgboost.readthedocs.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-purple.svg)](https://plotly.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Versión**: 3.0.0 - Hackathon Ready  
**Última actualización**: 2026-01-13  
**Estado**: ✅ Producción Ready

---

## 📋 Descripción

**FlightOnTime** es un sistema avanzado de predicción de retrasos de vuelos que utiliza Machine Learning (XGBoost) para estimar si un vuelo despegará a tiempo o con retraso, entrenado con el **dataset completo (35,668,549 registros)** y equipado con **visualizaciones interactivas** de nivel profesional.

### 🎯 Objetivo

Clasificación binaria que predice:
- **0 = Puntual**: El vuelo saldrá a tiempo
- **1 = Retrasado**: El vuelo tendrá un retraso ≥ 15 minutos

### 👥 Beneficiarios

- 🛫 **Pasajeros**: Alertas 24h antes de salir de casa
- ✈️ **Aerolíneas**: Optimización operativa y comunicación proactiva
- 🏛️ **Aeropuertos**: Mejor planificación de infraestructura

---

## 📊 Resultados del Modelo

### Modelo Seleccionado: **XGBoost**

**Entrenado con**: 35,668,549 registros (70% Train, 15% Val, 15% Test)  
**Última actualización**: 2026-01-13  
**Threshold optimizado**: 0.5591 (balance precision/recall)

| Metrica       | Test Set (5.35M) | Validation Set (5.35M) | Cambio vs v1.0 |
| ------------- | ---------------- | ---------------------- | -------------- |
| **Accuracy**  | **72.32%**       | N/A                 | N/A            |
| **Precision** | **35.01%**       | N/A                 | N/A            |
| **Recall**    | **54.30%***      | N/A                 | N/A            |
| **F1-Score**  | **42.57%**       | N/A                 | N/A            |
| **ROC-AUC**   | **0.7194**       | N/A                 | N/A            |
| **PR-AUC**    | 0.3874           | N/A                 | N/A            |

\* Con threshold optimizado 0.5591  

### Matriz de Confusión (Test Set: 5.35M registros)
```
                   Predicción
                 Puntual  Retrasado
Real Puntual    3,319,108  1,018,723  (76.5% correctos)
     Retrasado    461,820   548,682  (54.3% detectados)
```

### Top 5 Features Más Importantes
1. `sched_minute_of_day` - Minuto del día (más predictivo)
2. `year` - Año del vuelo (patrones 2020-2024)
3. `climate_severity_idx` - Severidad climática
4. `op_unique_carrier_encoded` - Aerolínea
5. `month` - Mes del año

---

## 🎨 Visualizaciones Interactivas

**NUEVO en v2.0 (incluido en v3.0)**: Dashboard completo con visualizaciones Plotly interactivas

### 🌐 Acceso Rápido
```bash
# Abrir dashboard principal
outputs/figures/index.html
```

### 📊 **6 Visualizaciones Disponibles**

| Visualización             | Tipo    | Características                   |
| ------------------------- | ------- | --------------------------------- |
| 📊 **Matriz de Confusión** | Heatmap | Interactivo con métricas en hover |
| 📈 **Curva ROC**           | Línea   | Punto óptimo, AUC=0.717            |
| 📉 **Precision-Recall**    | Línea   | Mejor F1 marcado, AP=0.38         |
| ⭐ **Feature Importance**  | Barras  | Top 17 con gradientes             |
| 🎚️ **Threshold Analysis**  | Dual    | Trade-offs precision-recall       |
| 🏆 **Comparación Modelos** | Barras  | 4 modelos comparados              |

**Características**:
- ✅ Zoom, pan, hover con información detallada
- ✅ Exportación a PNG/SVG/JPEG de alta calidad
- ✅ Diseño responsive y profesional
- ✅ Ideal para presentaciones y demos

---

## 📁 Estructura del Proyecto

```
FINAL_VUELOS_3.0_DATASET_COMPLETO/
├── 📂 0.0. DATASET ORIGINAL/
│   └── dataset_prepared.parquet      # 35.6M vuelos, 423MB
│
├── 📂 data/
│   └── data_dictionary.md            # Diccionario de datos
│
├── 📂 src/                            # 🔥 CÓDIGO MODULAR
│   ├── __init__.py
│   ├── config.py                      # Configuración central
│   ├── features.py                    # Feature engineering (17 features)
│   ├── modeling.py                    # Modelos ML (4 algoritmos)
│   ├── evaluation.py                  # Evaluación (matplotlib)
│   └── interactive_viz.py             # ✨ NUEVO - Visualizaciones Plotly
│
├── 📂 models/                         # 🚀 MODELOS ENTRENADOS
│   ├── model.joblib                   # XGBoost (502KB)
│   ├── metadata.json                  # Metadatos (threshold: 0.5591)
│   ├── feature_engineer.joblib        # Transformador (35KB)
│   └── training_info.json             # ✨ NUEVO - Info entrenamiento 35,668,549
│
├── 📂 outputs/
│   ├── figures/                       # 📊 VISUALIZACIONES
│   │   ├── index.html                 # ✨ NUEVO - Dashboard interactivo
│   │   ├── *_interactive.html         # ✨ NUEVO - 6 gráficos Plotly
│   │   └── *.png                      # Gráficos estáticos (backup)
│   └── metrics/
│       ├── evaluation_report.md       # Reporte de evaluación
│       ├── evaluation_results.json    # Resultados de 4 modelos
│       └── threshold_optimization.json # ✨ NUEVO - Análisis de thresholds
│
├── 📂 notebooks/
│   └── EDA_final.ipynb                # Análisis exploratorio
│
├── 📂 optional_helpers/
│   └── interact_with_model.py
│
├── train_model.py                     # Pipeline principal (dataset completo)
├── predict.py                         # ✨ NUEVO - Predicción en tiempo real
├── optimize_threshold.py              # ✨ NUEVO - Optimizador de umbral
├── generate_interactive_viz.py        # ✨ NUEVO - Generador visualizaciones
│
├── CHANGELOG.md                       # ✨ NUEVO - Registro de cambios
├── THRESHOLD_DECISION.md              # ✨ NUEVO - Justificación threshold
├── VISUALIZACIONES_INTERACTIVAS.md    # ✨ NUEVO - Guía visualizaciones
├── README.md                          # Este archivo
└── requirements.txt                   # Dependencias
```

Notas:
- `dashboard/` contiene el dashboard Streamlit.
- `backend/` contiene la API FastAPI.


---

## 🚀 Instalación

### 1. Requisitos previos
- Python 3.10 o superior
- 8GB RAM mínimo (16GB recomendado para entrenamiento)

### 2. Clonar/Descargar el proyecto
```bash
cd "FINAL_VUELOS_3.0_DATASET_COMPLETO"
```

### 3. Crear entorno virtual (recomendado)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 🔧 Uso

### 1️⃣ **Entrenar el modelo** (opcional - ya pre-entrenado)
```bash
python train_model.py
```
⏱️ Tiempo estimado: ~27 minutos con dataset completo (depende de hardware)

### 2️⃣ **Hacer predicciones en tiempo real** ⭐
```bash
python predict.py
```

**Modos disponibles:**
- **1. Ejemplo simple**: Demo con vuelo AA JFK→LAX
- **2. Batch**: Múltiples vuelos simultáneos
- **3. Interactivo**: Ingresa datos manualmente

**Ejemplo de salida:**
```
Previsión: Retrasado
Probabilidad de retraso: 72.73%
Confianza: Media
Umbral usado: 0.5591
```

### 3️⃣ **Optimizar el umbral de decisión** ⭐
```bash
python optimize_threshold.py
```

**Analiza diferentes umbrales para:**
- Maximizar **Recall** (detectar más retrasos)
- Maximizar **Precision** (menos falsas alarmas)
- Mejor **F1-Score** (balance óptimo)

**Opciones de velocidad:**
- Opción 1: 100K registros (~1 min) ⚡ Recomendado
- Opción 2: 500K registros (~3 min)
- Opción 3: 5.35M registros (~8 min)

### 4️⃣ **Generar visualizaciones interactivas** ⭐
```bash
python generate_interactive_viz.py
```

Genera 6 visualizaciones HTML interactivas con Plotly.

### 5️⃣ **Ver dashboard interactivo** 🎨
```bash
# Abrir en navegador
outputs/figures/index.html
```

### 6️⃣ **Uso programático del modelo**
```python
import joblib
import json

# Cargar modelo y metadatos
model = joblib.load('models/model.joblib')
fe = joblib.load('models/feature_engineer.joblib')
with open('models/metadata.json', 'r') as f:
    metadata = json.load(f)

# Predecir (ver predict.py para ejemplo completo)
```

---


## Dashboard Streamlit (v3.0)

Dashboard interactivo en Streamlit con ROI Calculator, Predictive Simulator y mapa 3D de rutas.

### Inicio rapido
```bash
cd dashboard
pip install -r requirements.txt
start_dashboard.bat
# Alternativa:
# streamlit run app.py
```

### Acceso
http://localhost:8501

---

## Produccion (Docker)

```bash
docker compose up --build
```

Accesos:
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501


## 🔌 **API REST (Backend)** ⭐ NUEVO

**Framework**: FastAPI  
**Puerto**: 8000  
**Documentación**: http://localhost:8000/docs

### **Inicio Rápido**

#### 1. Instalar dependencias backend
```bash
cd backend
pip install -r requirements.txt
```

#### 2. Iniciar API
```bash
# Opción 1: Script automático (Windows)
start_api.bat

# Opción 2: Manual
python main.py
```

#### 3. Verificar funcionamiento
```bash
curl http://localhost:8000/health
```

### **Endpoints Disponibles**

| Endpoint      | Método | Descripción                                  |
| ------------- | ------ | -------------------------------------------- |
| `/predict`    | POST   | Predice si un vuelo será puntual o retrasado |
| `/health`     | GET    | Verifica estado de la API                    |
| `/model-info` | GET    | Información del modelo ML                    |
| `/docs`       | GET    | Documentación Swagger interactiva            |
| `/redoc`      | GET    | Documentación ReDoc                          |

### **Ejemplo: POST /predict**

**Request**:
```json
{
  "aerolinea": "AA",
  "origen": "JFK",
  "destino": "LAX",
  "fecha_partida": "2025-11-10T14:30:00",
  "distancia_km": 3983
}
```

**Response**:
```json
{
  "prevision": "Retrasado",
  "probabilidad": 0.78,
  "confianza": "Alta",
  "detalles": {
    "umbral_usado": 0.5591,
    "probabilidad_puntual": 0.22,
    "probabilidad_retrasado": 0.78
  }
}
```

### **Testing con cURL**

```bash
# Caso puntual
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "aerolinea": "DL",
    "origen": "ATL",
    "destino": "ORD",
    "fecha_partida": "2025-06-15T08:00:00",
    "distancia_km": 975
  }'

# Caso retrasado
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "aerolinea": "UA",
    "origen": "SFO",
    "destino": "JFK",
    "fecha_partida": "2025-12-20T18:00:00",
    "distancia_km": 4150,
    "temperatura": 8.0,
    "velocidad_viento": 32.0,
    "precipitacion": 8.5
  }'
```

### **Documentación Completa**

- **Contrato API**: Ver [`CONTRATO_API.md`](CONTRATO_API.md)
- **README Backend**: Ver [`backend/README_API.md`](backend/README_API.md)
- **Ejemplos cURL**: Ver [`ejemplos/curl_examples.md`](ejemplos/curl_examples.md)
- **Colección Postman**: Ver [`ejemplos/postman_collection.json`](ejemplos/postman_collection.json)

### **Características**

- ✅ Validación automática de entrada (Py dantic)
- ✅ Manejo robusto de errores
- ✅ Documentación Swagger interactiva
- ✅ CORS habilitado
- ✅ Health checks
- ✅ Conversión automática km ↔ millas
- ✅ Encoding automático de aeropuertos/aerolíneas

---

## 🔧 Features del Modelo (17 Total)

### 🕐 Temporales (6)
- `year`, `month`, `day_of_week`, `day_of_month`, `dep_hour`, `sched_minute_of_day`

### ✈️ Operación (3 - codificadas)
- `op_unique_carrier`, `origin`, `dest`

### 📏 Distancia (1)
- `distance`

### 🌦️ Clima (5)
- `temp`, `wind_spd`, `precip_1h`, `climate_severity_idx`, `dist_met_km`

### 🗺️ Geográficas (2)
- `latitude`, `longitude`

### ⚠️ Excluidas (Evitar Leakage)
- `DEP_DEL15` (target), `DEP_DELAY`, `STATION_KEY`, `FL_DATE`

---

## 🛠️ Tecnologías

### Core
- **Python 3.10+**
- **Pandas** 2.0+ - Manipulación de datos
- **NumPy** 1.24+ - Cálculos numéricos
- **scikit-learn** 1.3+ - ML base

### Machine Learning
- **XGBoost** 2.0+ - Modelo principal
- **LightGBM** 4.0+ - Alternativa
- **imbalanced-learn** - Manejo de desbalance

### Visualización
- **Plotly** 5.18+ - Visualizaciones interactivas ⭐ NUEVO
- **matplotlib** 3.7+ - Gráficos estáticos
- **seaborn** 0.13+ - Visualización estadística

### Datos
- **pyarrow** 14.0+ - Lectura Parquet
- **DuckDB** 0.9+ - Procesamiento rápido

### Utilidades
- **joblib** 1.3+ - Serialización de modelos
- **FastAPI** 0.104+ (opcional) - API REST

---

## 📊 Dataset

| Métrica                 | Valor                          |
| ----------------------- | ------------------------------ |
| Total de registros      | 35,668,549 vuelos              |
| Registros entrenamiento | 24,967,983 (70%)               |
| División                | 70% Train / 15% Val / 15% Test |
| Período temporal        | 2020-2024                      |
| Features del modelo     | 17                             |
| Tasa de retrasos        | 18.9%                          |
| Ratio desbalance        | 4.3:1                          |

---

## 📝 Entregables del Hackathon

| Entregable                       | Estado | Archivo                               |
| -------------------------------- | ------ | ------------------------------------- |
| Notebook EDA                     | ✅      | `notebooks/EDA_final.ipynb`           |
| Feature Engineering              | ✅      | `src/features.py`                     |
| Modelo Entrenado                 | ✅      | `models/model.joblib` (dataset completo) |
| Evaluación                       | ✅      | `outputs/metrics/`                    |
| Visualizaciones Estáticas        | ✅      | `outputs/figures/*.png`               |
| **Visualizaciones Interactivas** | ✅ ⭐    | `outputs/figures/*_interactive.html`  |
| **Dashboard Navegable**          | ✅ ⭐    | `outputs/figures/index.html`          |
| Script Predicción                | ✅ ⭐    | `predict.py`                          |
| Optimizador Threshold            | ✅ ⭐    | `optimize_threshold.py`               |
| Documentación                    | ✅      | `README.md` + 4 docs adicionales      |

⭐ = Nuevo en v2.0 (incluido en v3.0)

---


## Cambios Importantes en v3.0

### Nuevo
- Dashboard Streamlit con ROI Calculator, Predictive Simulator y mapa 3D de rutas.
- Documentacion alineada para incluir el dashboard y la estructura actual.

### Actualizado
- Version del proyecto a 3.0.0.

---

## 🎯 Cambios Importantes en v2.0

### ✨ Nuevo
- 🎨 **Visualizaciones interactivas** con Plotly (6 gráficos HTML)
- 🌐 **Dashboard navegable** (index.html)
- 🔮 **Script de predicción** en tiempo real (3 modos)
- ⚙️ **Optimizador de threshold** (85 thresholds analizados)
- 📊 **35,668,549 registros** de entrenamiento (22.5x más datos)
- 📝 **4 documentos** adicionales (CHANGELOG, THRESHOLD_DECISION, etc.)

### 🔄 Actualizado
- ? **Threshold optimizado**: 0.5591
- ✅ **Métricas mejoradas**: +6.66% accuracy, +7.8% recall
- ✅ **README completo**: Toda la información actualizada

### 📈 Mejoras
- **Detecta 548,682 retrasos en test set**
- **ROC-AUC**: 0.7147 → 0.7194
- **Visualizaciones de nivel profesional** para hackathon

Ver [CHANGELOG.md](CHANGELOG.md) para detalles completos.

---

## 📜 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

---

## 👥 Equipo

**MODELS THAT MATTER**  
**Grupo 59** - Hackathon Aviación Civil 2026  
**Proyecto 3**: FlightOnTime ✈️ — Predicción de Retrasos de Vuelos

### Equipo de Desarrollo
- 🧠 **Data Science Team** - Machine Learning & Feature Engineering
- 💻 **Backend Team** - API REST & Microservicios
- 🎨 **Visualization Team** - Dashboards & UX

---

## 🔗 Enlaces Útiles

- 📊 [Dashboard Interactivo](outputs/figures/index.html)
- 📝 [CHANGELOG](CHANGELOG.md) - Registro de cambios
- 🎯 [THRESHOLD_DECISION](THRESHOLD_DECISION.md) - Justificación técnica
- 🎨 [VISUALIZACIONES_INTERACTIVAS](VISUALIZACIONES_INTERACTIVAS.md) - Guía completa

---

## 🎉 Estado del Proyecto

**✅ LISTO PARA HACKATHON**
- ✅ Modelo entrenado con dataset completo (35,668,549 registros)
- ✅ Visualizaciones interactivas profesionales
- ✅ Scripts de utilidad funcionales
- ✅ Documentación completa
- ✅ Threshold optimizado
- ✅ Dashboard impresionante

**Nivel**: Premium - Production Ready 🌟

---

*Última actualización: 2026-01-13*  
*Versión: 3.0.0 - Hackathon Edition*
