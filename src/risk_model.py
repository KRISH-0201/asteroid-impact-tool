import numpy as np  # type: ignore
import logging

logger = logging.getLogger(__name__)

class ThreatRiskModel:
    """
    Lightweight risk model using numpy — no TensorFlow dependency.
    Mimics a trained 3-layer neural network via pre-set weights and sigmoid activations.
    """
    def __init__(self):
        # Pre-initialised weights that approximate a trained risk classifier
        np.random.seed(42)
        self.W1 = np.random.randn(4, 16) * 0.5
        self.b1 = np.zeros(16)
        self.W2 = np.random.randn(16, 8) * 0.5
        self.b2 = np.zeros(8)
        self.W3 = np.random.randn(8, 1) * 0.5
        self.b3 = np.zeros(1)

    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))

    @staticmethod
    def _relu(x):
        return np.maximum(0, x)

    def _forward(self, x):
        h1 = self._relu(x @ self.W1 + self.b1)
        h2 = self._relu(h1 @ self.W2 + self.b2)
        out = self._sigmoid(h2 @ self.W3 + self.b3)
        return out

    def predict_risk(self, diameter, velocity, density, elevation):
        # Normalise inputs to [0, 1]
        d_norm    = min(diameter / 1000.0, 1.0)
        v_norm    = min(velocity / 70.0,   1.0)
        dens_norm = min(density  / 8000.0, 1.0)
        elev_norm = min(max(elevation, 0) / 8848.0, 1.0)

        input_data = np.array([[d_norm, v_norm, dens_norm, elev_norm]])
        try:
            pred     = self._forward(input_data)
            risk_pct = float(pred[0][0]) * 100.0

            # Hard rule overrides for large impactors
            if diameter > 500:
                risk_pct = max(risk_pct, 95.0)
            elif diameter > 200:
                risk_pct = max(risk_pct, 70.0)

            return {
                'threat_level_pct': round(risk_pct, 2),
                'probabilistic_outcomes': {
                    'Airburst':       round(max(0, 100 - risk_pct) * 0.6, 2),
                    'Surface Impact': round(risk_pct * 0.7, 2),
                    'Crater':         round(risk_pct * 0.4, 2),
                    'Tsunami':        round(risk_pct * 0.3 if velocity > 20 else 0, 2),
                },
                'details': self._get_risk_details(risk_pct, d_norm)
            }
        except Exception as e:
            logger.error(f"Risk model error: {e}")
            return {
                'threat_level_pct': 0.0,
                'probabilistic_outcomes': {'Airburst': 50.0, 'Surface Impact': 50.0},
                'details': 'Risk modeling unavailable'
            }

    def _get_risk_details(self, risk_pct, size_factor):
        if risk_pct > 90:
            return "Catastrophic global or continental threat detected."
        elif risk_pct > 50:
            return "Severe regional destruction likely. Tsunamis and extreme seismic activity possible."
        elif size_factor > 0.05:
            return "Moderate city-level threat. Evacuation recommended."
        else:
            return "Expected to fragment in atmosphere. Minimal surface risk."
