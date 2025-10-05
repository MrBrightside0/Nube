import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def seasonal_analysis_api(lat: float, lon: float, days: int = 7):
    """
    Intenta generar tendencia real usando modelos (Prophet, etc.).
    Si no hay modelo, genera datos simulados.
    """
    print(f"📈 Generando análisis estacional para lat={lat}, lon={lon}")

    try:
        # 🔹 Aquí iría tu modelo Prophet / histórico real
        # Simulación: subida y bajada tipo sinusoidal
        base = np.linspace(20, 60, days) + np.sin(np.arange(days) / 2) * 10
        pm25 = np.clip(base + np.random.randn(days) * 2, 10, 70)
        no2 = np.clip(pm25 * 0.75 + np.random.randn(days) * 1.5, 5, 60)

        corr = np.corrcoef(pm25, no2)[0, 1]

        trend = [
            {"ts": f"Day {i+1}", "pm25": float(pm25[i]), "no2": float(no2[i])}
            for i in range(days)
        ]

        return {"trend": trend, "correlation": round(float(corr), 3)}

    except Exception as e:
        print(f"⚠️ Error en seasonal_analysis_api: {e}")
        return {"trend": [], "correlation": 0.0}
