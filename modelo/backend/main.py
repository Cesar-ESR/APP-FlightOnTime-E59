"""FastAPI service for FlightOnTime predictions."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
MODEL_PATH = ROOT_DIR / "models" / "model.joblib"
METADATA_PATH = ROOT_DIR / "models" / "metadata.json"
FEATURE_ENGINEER_PATH = ROOT_DIR / "models" / "feature_engineer.joblib"


class PredictionRequest(BaseModel):
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    day_of_month: int = Field(..., ge=1, le=31)
    day_of_week: int = Field(..., ge=1, le=7)
    dep_hour: int = Field(..., ge=0, le=23)
    dep_minute: int = Field(0, ge=0, le=59)
    sched_minute_of_day: int | None = Field(default=None, ge=0, le=1440)
    op_unique_carrier: str = Field(..., min_length=2, max_length=3)
    origin: str = Field(..., min_length=3, max_length=3)
    dest: str = Field(..., min_length=3, max_length=3)
    distance: float = Field(..., ge=0)
    temp: float = Field(...)
    wind_spd: float = Field(..., ge=0)
    precip_1h: float = Field(..., ge=0)
    climate_severity_idx: float = Field(..., ge=0)
    dist_met_km: float = Field(..., ge=0)
    latitude: float = Field(...)
    longitude: float = Field(...)


class PredictionResponse(BaseModel):
    prevision: str
    probabilidad: float
    confianza: str
    detalles: dict[str, Any]


@dataclass
class ModelService:
    model: Any
    metadata: dict[str, Any]
    feature_engineer: Any

    @property
    def threshold(self) -> float:
        return float(self.metadata["threshold"])

    @property
    def features(self) -> list[str]:
        return list(self.metadata["feature_names"])

    def prepare_input(self, payload: PredictionRequest) -> pd.DataFrame:
        sched_minute = payload.sched_minute_of_day
        if sched_minute is None:
            sched_minute = payload.dep_hour * 60 + payload.dep_minute

        flight_data = payload.model_dump()
        flight_data["sched_minute_of_day"] = sched_minute

        df = pd.DataFrame([flight_data])

        if hasattr(self.feature_engineer, "transform_categorical"):
            df = self.feature_engineer.transform_categorical(df)

        missing = [feature for feature in self.features if feature not in df.columns]
        if missing:
            raise ValueError(f"Faltan features requeridas: {', '.join(missing)}")

        return df[self.features]

    def predict(self, payload: PredictionRequest) -> PredictionResponse:
        features = self.prepare_input(payload)
        proba = float(self.model.predict_proba(features)[0, 1])
        prediction = 1 if proba >= self.threshold else 0
        label = "Retrasado" if prediction == 1 else "Puntual"
        confidence = (
            "Alta" if abs(proba - 0.5) > 0.3 else "Media" if abs(proba - 0.5) > 0.15 else "Baja"
        )

        return PredictionResponse(
            prevision=label,
            probabilidad=proba,
            confianza=confidence,
            detalles={
                "umbral_usado": self.threshold,
                "probabilidad_puntual": 1 - proba,
                "probabilidad_retrasado": proba,
            },
        )


def load_service() -> ModelService:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modelo no encontrado en {MODEL_PATH}")
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadatos no encontrados en {METADATA_PATH}")
    if not FEATURE_ENGINEER_PATH.exists():
        raise FileNotFoundError(f"Feature engineer no encontrado en {FEATURE_ENGINEER_PATH}")

    model = joblib.load(MODEL_PATH)
    with METADATA_PATH.open("r", encoding="utf-8") as file:
        metadata = json.load(file)
    feature_engineer = joblib.load(FEATURE_ENGINEER_PATH)

    return ModelService(model=model, metadata=metadata, feature_engineer=feature_engineer)


app = FastAPI(title="FlightOnTime API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    try:
        app.state.service = load_service()
    except Exception as exc:  # pragma: no cover - startup guard
        app.state.service_error = str(exc)


@app.get("/health")
async def health_check() -> dict[str, Any]:
    service = getattr(app.state, "service", None)
    return {
        "status": "ok" if service else "error",
        "model_loaded": service is not None,
        "error": getattr(app.state, "service_error", None),
    }


@app.get("/model-info")
async def model_info() -> dict[str, Any]:
    service = getattr(app.state, "service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    return {
        "model_name": service.metadata.get("model_name"),
        "threshold": service.threshold,
        "trained_at": service.metadata.get("trained_at"),
        "metrics": service.metadata.get("metrics", {}),
        "features": service.features,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(payload: PredictionRequest) -> PredictionResponse:
    service = getattr(app.state, "service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="Modelo no disponible")
    try:
        return service.predict(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guard for unexpected errors
        raise HTTPException(status_code=500, detail="Error en la predicción") from exc
