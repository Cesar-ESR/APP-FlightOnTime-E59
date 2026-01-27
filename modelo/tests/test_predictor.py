import unittest
from pathlib import Path

from predict import FlightDelayPredictor


MODEL_PATH = Path("models/model.joblib")
METADATA_PATH = Path("models/metadata.json")
FEATURE_ENGINEER_PATH = Path("models/feature_engineer.joblib")


@unittest.skipUnless(
    MODEL_PATH.exists() and METADATA_PATH.exists() and FEATURE_ENGINEER_PATH.exists(),
    "Model artifacts not available for prediction test.",
)
class TestFlightDelayPredictor(unittest.TestCase):
    def test_predict_returns_expected_keys(self):
        predictor = FlightDelayPredictor()
        flight_data = {
            "year": 2024,
            "month": 3,
            "day_of_month": 15,
            "day_of_week": 5,
            "dep_hour": 14,
            "sched_minute_of_day": 870,
            "op_unique_carrier": "AA",
            "origin": "JFK",
            "dest": "LAX",
            "distance": 2475.0,
            "temp": 25.5,
            "wind_spd": 15.3,
            "precip_1h": 0.0,
            "climate_severity_idx": 0.35,
            "dist_met_km": 12.5,
            "latitude": 40.6413,
            "longitude": -73.7781,
        }

        result = predictor.predict(flight_data)

        self.assertIn("prevision", result)
        self.assertIn("probabilidad", result)
        self.assertIn("umbral_usado", result)
        self.assertIn("confianza", result)
        self.assertIn("prob_puntual", result)
        self.assertIn("prob_retrasado", result)

    def test_predict_returns_valid_probabilities(self):
        predictor = FlightDelayPredictor()
        flight_data = {
            "year": 2024,
            "month": 3,
            "day_of_month": 15,
            "day_of_week": 5,
            "dep_hour": 14,
            "sched_minute_of_day": 870,
            "op_unique_carrier": "AA",
            "origin": "JFK",
            "dest": "LAX",
            "distance": 2475.0,
            "temp": 25.5,
            "wind_spd": 15.3,
            "precip_1h": 0.0,
            "climate_severity_idx": 0.35,
            "dist_met_km": 12.5,
            "latitude": 40.6413,
            "longitude": -73.7781,
        }

        result = predictor.predict(flight_data)

        self.assertIn(result["prevision"], {"Retrasado", "Puntual"})
        self.assertGreaterEqual(result["probabilidad"], 0.0)
        self.assertLessEqual(result["probabilidad"], 1.0)
        self.assertGreaterEqual(result["prob_puntual"], 0.0)
        self.assertLessEqual(result["prob_puntual"], 1.0)
        self.assertGreaterEqual(result["prob_retrasado"], 0.0)
        self.assertLessEqual(result["prob_retrasado"], 1.0)
        self.assertAlmostEqual(
            result["prob_puntual"] + result["prob_retrasado"], 1.0, places=6
        )


if __name__ == "__main__":
    unittest.main()
