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
class RecommendationContext:
    scope: str  # "station" or "metropolitan"
    location: Optional[str]
    datetime_iso: Optional[str]
    pm10: Optional[float]
    pm25: Optional[float]
    gases: Dict[str, float]
    particles: Dict[str, float]
    aggregates: Optional[Dict[str, Dict[str, float]]] = None
    highlights: Optional[Dict[str, Dict[str, float]]] = None


SYSTEM_PROMPT = (
    "Eres un asistente experto en calidad del aire en la Zona Metropolitana de Monterrey. "
    "Recibirás pronósticos para una estación específica o para el agregado metropolitano. "
    "Responde en español con los puntos: "
    "1) Evaluación de riesgo (bajo, moderado, alto, muy alto) y breve explicación. "
    "2) Recomendaciones de mitigación para autoridades (acciones concretas). "
    "3) Recomendaciones para la población general (hábitos, protección personal)."
)


def build_user_prompt(context: RecommendationContext) -> str:
    scope = context.scope.lower()
    lines = [
        f"Alcance: {'estacion especifica' if scope == 'station' else 'area metropolitana completa'}.",
    ]

    if scope == "station":
        lines.extend(
            [
                f"Estacion: {context.location or 'desconocida'}.",
                f"Fecha y hora (UTC): {context.datetime_iso or 'no especificada'}.",
                f"PM10 pronosticado: {_format(context.pm10, 'ug/m3')}.",
                f"PM2.5 pronosticado: {_format(context.pm25, 'ug/m3')}.",
                f"Gases criterio (ppm o ug/m3): {_format_gases(context.gases)}.",
            ]
        )
    else:
        particles = context.aggregates.get("particles") if context.aggregates else {}
        gases = context.aggregates.get("gases") if context.aggregates else {}

        lines.append("Promedios recientes (ultimas horas por estacion):")
        if particles:
            descriptions = []
            for name, stats in particles.items():
                if not isinstance(stats, dict):
                    continue
                avg_text = _format(stats.get("avg"), "ug/m3")
                max_text = _format(stats.get("max"), "ug/m3")
                descriptions.append(f"{name.upper()}: media {avg_text}, maximo {max_text}")
            if descriptions:
                lines.append(" - Partículas: " + "; ".join(descriptions) + ".")
        if gases:
            descriptions = []
            for name, stats in gases.items():
                if not isinstance(stats, dict):
                    continue
                avg_value = stats.get("avg", stats.get("overall_avg"))
                descriptions.append(f"{name.upper()}: {_format(avg_value, '')}")
            if descriptions:
                lines.append(" - Gases: " + "; ".join(descriptions) + ".")

        if context.highlights:
            highlight_lines = []
            for name, info in context.highlights.items():
                value = info.get("value")
                location = info.get("location_name") or info.get("location_id")
                timestamp = info.get("timestamp") or info.get("datetime")
                if value is not None and location:
                    highlight_lines.append(
                        f"{name.upper()}: pico {value:.2f} ug/m3 en {location} ({timestamp})."
                    )
            if highlight_lines:
                lines.append("Picos destacados:" + " ".join(highlight_lines))

        if context.particles:
            lines.append(
                "PM10 estimado base: "
                f"{_format(context.particles.get('pm10'), 'ug/m3')} | "
                "PM2.5 estimado base: "
                f"{_format(context.particles.get('pm25'), 'ug/m3')}"
            )

    lines.append("Responde siguiendo el formato solicitado.")
    return "\n".join(lines)


def _format(value: Optional[float], unit: str) -> str:
    if value is None:
        return "sin dato"
    suffix = f" {unit}" if unit else ""
    return f"{value:.2f}{suffix}"


def _format_gases(gases: Dict[str, float]) -> str:
    if not gases:
        return "sin datos"
    return ", ".join(f"{name.upper()}: {val:.4f}" for name, val in gases.items())


def load_snapshot() -> RecommendationContext:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Entrada JSON inválida: {exc}")

    if not isinstance(payload, dict):
        raise SystemExit("Se esperaba un objeto JSON con las predicciones.")

    return RecommendationContext(
        scope=str(payload.get("scope", "station")),
        location=payload.get("location"),
        datetime_iso=payload.get("datetime"),
        pm10=_safe_float(payload.get("pm10")),
        pm25=_safe_float(payload.get("pm25")),
        gases={k: _safe_float(v) for k, v in payload.get("gases", {}).items() if _safe_float(v) is not None},
        particles={k: _safe_float(v) for k, v in payload.get("particles", {}).items() if _safe_float(v) is not None},
        aggregates=payload.get("aggregates"),
        highlights=payload.get("highlights"),
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
