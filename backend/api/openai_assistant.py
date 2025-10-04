"""Call OpenAI ChatGPT for air quality recommendations based on predictions."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Dict, Optional

from openai import OpenAI

try:
    from .constants import OPENAI_API_KEY
except ImportError:  # pragma: no cover - standalone execution
    from constants import OPENAI_API_KEY  # type: ignore


@dataclass
class PredictionSnapshot:
    location: str
    datetime_iso: Optional[str]
    pm10: Optional[float]
    pm25: Optional[float]
    gases: Dict[str, float]


SYSTEM_PROMPT = (
    "Eres un asistente experto en calidad del aire en la Zona Metropolitana de Monterrey. "
    "Analiza los niveles pronosticados de PM10, PM2.5 y gases criterio y responde en español con: "
    "1) Evaluación de riesgo (bajo, moderado, alto, muy alto) y breve explicación. "
    "2) Recomendaciones de mitigación para autoridades (acciones concretas). "
    "3) Recomendaciones para la población general (hábitos, protección personal)."
)


def build_user_prompt(snapshot: PredictionSnapshot) -> str:
    return (
        "Ubicación: {location}.\n"
        "Fecha y hora (UTC): {datetime}.\n"
        "PM10 pronosticado: {pm10}.\n"
        "PM2.5 pronosticado: {pm25}.\n"
        "Gases (ppm o µg/m³ según corresponda): {gases}.\n"
        "Responde siguiendo el formato solicitado."
    ).format(
        location=snapshot.location,
        datetime=snapshot.datetime_iso or "no especificada",
        pm10=_format(snapshot.pm10, "µg/m³"),
        pm25=_format(snapshot.pm25, "µg/m³"),
        gases=_format_gases(snapshot.gases),
    )


def _format(value: Optional[float], unit: str) -> str:
    if value is None:
        return "sin dato"
    return f"{value:.2f} {unit}"


def _format_gases(gases: Dict[str, float]) -> str:
    if not gases:
        return "sin datos"
    return ", ".join(f"{name.upper()}: {val:.4f}" for name, val in gases.items())


def load_snapshot() -> PredictionSnapshot:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Entrada JSON inválida: {exc}")

    if not isinstance(payload, dict):
        raise SystemExit("Se esperaba un objeto JSON con las predicciones.")

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
    if not OPENAI_API_KEY:
        raise SystemExit("OPENAI_API_KEY no está definido en constants.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.6,
    )
    return completion.choices[0].message.content or ""


def main() -> None:
    snapshot = load_snapshot()
    prompt = build_user_prompt(snapshot)
    answer = request_recommendations(prompt)
    print(json.dumps({"recommendations": answer}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
