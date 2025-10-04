"""Helper to request air-quality advice from OpenAI based on model predictions.

This script expects a JSON object via stdin with the following structure:

{
  "location": "Monterrey Centro",
  "datetime": "2025-01-01T12:00:00Z",
  "pm10": 72.4,
  "pm25": 28.1,
  "gases": {
    "co": 0.42,
    "no2": 0.019,
    "o3": 0.021
  }
}

It requires ``OPENAI_API_KEY`` in the environment and produces a JSON response
with recommendations for authorities and citizens.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, Optional

from openai import OpenAI


@dataclass
class PredictionSnapshot:
    location: str
    datetime_iso: Optional[str]
    pm10: Optional[float]
    pm25: Optional[float]
    gases: Dict[str, float]


SYSTEM_PROMPT = (
    "Eres un asistente especializado en calidad del aire. Recibes predicciones "
    "de PM10, PM2.5 y gases criterio y debes evaluar si representan riesgo para la salud, "
    "proponer acciones para reducir la contaminación y dar recomendaciones a la población."
)


def build_user_prompt(snapshot: PredictionSnapshot) -> str:
    return (
        "Ubicación: {location}.\n"
        "Fecha y hora (UTC): {datetime}.\n"
        "PM10 pronosticado: {pm10}.\n"
        "PM2.5 pronosticado: {pm25}.\n"
        "Gases: {gases}.\n"
        "Analiza y responde con: (1) evaluación del riesgo, (2) recomendaciones para autoridades, "
        "(3) recomendaciones para ciudadanía."
    ).format(
        location=snapshot.location,
        datetime=snapshot.datetime_iso or "desconocida",
        pm10=_format_value(snapshot.pm10, "µg/m³"),
        pm25=_format_value(snapshot.pm25, "µg/m³"),
        gases=_format_gases(snapshot.gases),
    )


def _format_value(value: Optional[float], unit: str) -> str:
    if value is None:
        return "sin dato"
    return f"{value:.2f} {unit}"


def _format_gases(gases: Dict[str, float]) -> str:
    if not gases:
        return "sin datos"
    return ", ".join(f"{name.upper()}: {value:.4f}" for name, value in gases.items())


def load_snapshot() -> PredictionSnapshot:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Entrada JSON inválida: {exc}")

    if not isinstance(payload, dict):
        raise SystemExit("La entrada debe ser un objeto JSON con las predicciones.")

    return PredictionSnapshot(
        location=payload.get("location", "Ubicación desconocida"),
        datetime_iso=payload.get("datetime"),
        pm10=_safe_float(payload.get("pm10")),
        pm25=_safe_float(payload.get("pm25")),
        gases={k: _safe_float(v) for k, v in payload.get("gases", {}).items() if _safe_float(v) is not None},
    )


def _safe_float(value) -> Optional[float]:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def request_recommendations(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY no está definido en el entorno.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
    )
    return response.choices[0].message.content or ""


def main() -> None:
    snapshot = load_snapshot()
    prompt = build_user_prompt(snapshot)
    answer = request_recommendations(prompt)
    print(json.dumps({"recommendations": answer}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
