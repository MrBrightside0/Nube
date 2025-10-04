from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from flask import Blueprint, jsonify, request

blueprint = Blueprint("api", __name__)


@blueprint.route("/health", methods=["GET"])
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


def _parse_float(name: str, default: float | None = None) -> float | None:
    value = request.args.get(name, type=float)
    return value if value is not None else default


@blueprint.route("/aq/latest", methods=["GET"])
def aq_latest() -> tuple:
    lat = _parse_float("lat")
    lon = _parse_float("lon")
    pollutant = request.args.get("pollutant", default="pm25")

    now = datetime.utcnow()
    base = (lat or 25.67) + (lon or -100.31)
    payload: dict[str, Any] = {
        "aqi": max(10, min(200, int(abs(base) * 3.2) % 201)),
        "pm25": round(abs(base) % 35 + 5, 1),
        "no2": round(abs(base) % 70 + 10, 1),
        "wind": round((abs(base) % 5) + 1.5, 1),
        "sources": ["TEMPO", "MODEL"],
        "pollutant": pollutant,
    }
    payload["pm10"] = round(abs(base) % 50 + 15, 1)
    return jsonify(payload), 200


@blueprint.route("/aq/trends", methods=["GET"])
def aq_trends() -> tuple:
    lat = _parse_float("lat")
    lon = _parse_float("lon")
    days = request.args.get("days", default=7, type=int)

    now = datetime.utcnow()
    series = []
    for idx in range(days):
        ts = now - timedelta(days=days - idx - 1)
        factor = (idx + 1) * 0.8
        series.append(
            {
                "ts": ts.isoformat() + "Z",
                "pm25": round(12 + factor, 1),
                "no2": round(20 + factor * 1.6, 1),
            }
        )

    response = {"series": series, "correlation": 0.63}
    return jsonify(response), 200


@blueprint.route("/ai/predict", methods=["GET"])
def ai_predict() -> tuple:
    lat = _parse_float("lat")
    lon = _parse_float("lon")
    pollutant = request.args.get("pollutant", default="pm25")
    days = request.args.get("days", default=30, type=int)

    today = datetime.utcnow().date()
    predictions = []
    for offset in range(days):
        ds = today + timedelta(days=offset)
        predictions.append({"ds": ds.isoformat(), "yhat": round(15 + offset * 0.4, 1)})

    response = {"pollutant": pollutant, "predictions": predictions}
    return jsonify(response), 200


@blueprint.route("/ai/seasonal", methods=["GET"])
def ai_seasonal() -> tuple:
    lat = _parse_float("lat")
    lon = _parse_float("lon")
    pollutant = request.args.get("pollutant", default="pm25")

    today = datetime.utcnow().date()
    trend = []
    for offset in range(12):
        ds = today - timedelta(weeks=offset)
        trend.append({"ts": ds.isoformat(), "value": round(10 + offset * 0.7, 1)})

    response = {"pollutant": pollutant, "trend": list(reversed(trend))}
    return jsonify(response), 200


@blueprint.route("/alerts/subscribe", methods=["POST"])
def alerts_subscribe() -> tuple:
    payload = request.get_json(silent=True) or {}
    contact = payload.get("contact")
    preferences = payload.get("preferences", {})

    if not contact or "type" not in preferences or "city" not in preferences:
        return jsonify({"error": "contact and preferences.type/city are required"}), 400

    response = {
        "message": "Subscription registered",
        "contact": contact,
        "preferences": preferences,
    }
    return jsonify(response), 201
