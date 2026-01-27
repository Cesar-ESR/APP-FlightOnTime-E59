# FlightOnTime - Diccionario de Datos

Este diccionario describe las variables del dataset de vuelos y las features utilizadas en el modelo.

**Actualizado:** 2026-01-13

---

## 📊 Resumen del Dataset

| Métrica             | Valor      |
| ------------------- | ---------- |
| Total de registros  | 35,668,549 |
| Columnas originales | 18         |
| Features del modelo | 17         |
| Tasa de retrasos    | ~18.9%     |

---

## ✅ Features Utilizadas en el Modelo (17 total)

### 🕐 Temporales (6 features)

| Variable              | Tipo | Descripción                                             | Ejemplo |
| --------------------- | ---- | ------------------------------------------------------- | ------- |
| `year`                | int  | Año del vuelo (captura cambios estructurales 2020-2024) | 2024    |
| `month`               | int  | Mes del año (1-12)                                      | 7       |
| `day_of_week`         | int  | Día de la semana (1=Lun, 7=Dom)                         | 5       |
| `day_of_month`        | int  | Día del mes (1-31) - opcional                           | 15      |
| `dep_hour`            | int  | Hora programada de salida (0-23) - interpretable        | 14      |
| `sched_minute_of_day` | int  | Minuto del día (0-1439) - más granular                  | 870     |

### ✈️ Operación (3 features encoded)

| Variable            | Tipo   | Descripción                  | Ejemplo |
| ------------------- | ------ | ---------------------------- | ------- |
| `op_unique_carrier` | string | Código de aerolínea          | "AA"    |
| `origin`            | string | Aeropuerto de origen (IATA)  | "JFK"   |
| `dest`              | string | Aeropuerto de destino (IATA) | "LAX"   |

> **Nota:** Estas variables se codifican con LabelEncoder → `_encoded`

### 📏 Distancia (1 feature)

| Variable   | Tipo  | Descripción                  | Ejemplo |
| ---------- | ----- | ---------------------------- | ------- |
| `distance` | float | Distancia del vuelo (millas) | 2475.0  |

### 🌦️ Clima (5 features) - **Gran valor agregado**

| Variable               | Tipo  | Descripción                                         | Ejemplo |
| ---------------------- | ----- | --------------------------------------------------- | ------- |
| `temp`                 | float | Temperatura (°C)                                    | 25.5    |
| `wind_spd`             | float | Velocidad del viento (km/h)                         | 15.3    |
| `precip_1h`            | float | Precipitación última hora (mm). **-1 → 0**          | 0.0     |
| `climate_severity_idx` | float | Índice de severidad climática                       | 0.35    |
| `dist_met_km`          | float | Distancia a estación meteorológica (km) - confianza | 12.5    |

### 🗺️ Geográficas (2 features)

| Variable    | Tipo  | Descripción             | Ejemplo  |
| ----------- | ----- | ----------------------- | -------- |
| `latitude`  | float | Latitud del aeropuerto  | 40.6413  |
| `longitude` | float | Longitud del aeropuerto | -73.7781 |

---

## ❌ Features EXCLUIDAS (Evitar Leakage)

| Variable           | Razón de Exclusión                             |
| ------------------ | ---------------------------------------------- |
| `DEP_DEL15`        | **Target** - Es la variable objetivo           |
| `DEP_DELAY`        | **Leakage** - Contiene la respuesta en minutos |
| `STATION_KEY`      | Llave técnica, no aporta valor predictivo      |
| `FL_DATE`          | Alta cardinalidad, usar componentes separados  |
| `ORIGIN_CITY_NAME` | Redundante con `origin`                        |
| `DEST_CITY_NAME`   | Redundante con `dest`                          |

---

## 🎯 Variable Objetivo

| Variable     | Tipo | Descripción                                         |
| ------------ | ---- | --------------------------------------------------- |
| `is_delayed` | int  | Vuelo retrasado: **0 = Puntual**, **1 = Retrasado** |

**Definición de retraso:** Un vuelo se considera retrasado si `DEP_DELAY >= 15` minutos.

---

## 📈 Importancia de Features (XGBoost)

| Rank | Feature                     | Importancia |
| ---- | --------------------------- | ----------- |
| 1    | `sched_minute_of_day`       | 27.91%      |
| 2    | `year`                      | 12.06%      |
| 3    | `climate_severity_idx`      | 8.53%       |
| 4    | `op_unique_carrier_encoded` | 7.70%       |
| 5    | `month`                     | 6.42%       |
| 6    | `temp`                      | 5.77%       |
| 7    | `dep_hour`                  | 4.33%       |
| 8    | `day_of_week`               | 3.89%       |
| 9    | `longitude`                 | 3.73%       |
| 10   | `precip_1h`                 | 3.60%       |

---

## 🔌 Contrato de Integración con Backend

### Entrada del API (POST /predict)

```json
{
    "aerolinea": "AA",
    "origen": "JFK",
    "destino": "LAX",
    "fecha_partida": "2025-03-15T14:30:00",
    "distancia_km": 3983
}
```

### Mapeo Entrada → Features del Modelo

| Campo API       | Feature del Modelo                                                                |
| --------------- | --------------------------------------------------------------------------------- |
| `aerolinea`     | `op_unique_carrier_encoded`                                                       |
| `origen`        | `origin_encoded`                                                                  |
| `destino`       | `dest_encoded`                                                                    |
| `fecha_partida` | `year`, `month`, `day_of_month`, `day_of_week`, `dep_hour`, `sched_minute_of_day` |
| `distancia_km`  | `distance`                                                                        |

### Salida del API

```json
{
    "prevision": "Retrasado",
    "probabilidad": 0.78
}
```

---

## 📊 Métricas del Modelo Actual

| Métrica       | Valor   |
| ------------- | ------- |
| Modelo        | XGBoost |
| Accuracy      | 0.7232  |
| Precision     | 0.3501  |
| Recall        | 0.5430  |
| F1-Score      | 0.4257  |
| ROC-AUC       | 0.7194  |
| Umbral ??ptimo | 0.5591  |
