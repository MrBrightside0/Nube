from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Blueprint, jsonify, request

from ai import inference
from .constants import SENSORS_DICT, WEATHER_STATIONS_DICT
from .openaq_connection import OpenAQClient
from .weather_api_connection import OpenWeatherClient, OneCallNotAvailableError

api_bp = Blueprint("api", __name__)

ALERTS_PATH = Path(__file__).resolve().parent / "cache" / "alerts.json"


def _load_unique_locations() -> pd.DataFrame:
    dataset = inference._load_base_dataset()
    columns = ["location_id", "location_name", "lat", "lon"]
    existing = [col for col in columns if col in dataset.columns]
    unique = dataset[existing].drop_duplicates("location_id")
    unique["location_id"] = unique["location_id"].astype(str)
    return unique


@lru_cache(maxsize=1)
def _locations_index() -> pd.DataFrame:
    return _load_unique_locations()


def _nearest_location(lat: float, lon: float) -> dict[str, Any] | None:
    locations = _locations_index()
    if {"lat", "lon"}.issubset(locations.columns):
        deltas = locations[["lat", "lon"]] - [lat, lon]
        idx = (deltas**2).sum(axis=1).idxmin()
        return locations.loc[idx].to_dict()
    return None


def _resolve_location(location_id: str | None, lat: float | None, lon: float | None) -> dict[str, Any] | None:
    locations = _locations_index()

    if location_id:
        match = locations[locations["location_id"] == str(location_id)]
        if not match.empty:
            return match.iloc[0].to_dict()
        return None

    if lat is not None and lon is not None:
        return _nearest_location(lat, lon)

    return None


def _compute_pm25_aqi(pm25: float | None) -> float | None:
    if pm25 is None:
        return None

    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]

    for c_low, c_high, aqi_low, aqi_high in breakpoints:
        if c_low <= pm25 <= c_high:
            return ((aqi_high - aqi_low) / (c_high - c_low)) * (pm25 - c_low) + aqi_low

    return 500.0


def _get_dataset_for_location(location_id: str, days: int | None = None) -> pd.DataFrame:
    dataset = inference._load_base_dataset()
    df = dataset[dataset["location_id"].astype(str) == location_id].copy()
    if days is not None and "datetime" in df.columns:
        cutoff = df["datetime"].max() - pd.Timedelta(days=days)
        df = df[df["datetime"] >= cutoff]
    return df


def _load_alerts() -> list[dict[str, Any]]:
    if ALERTS_PATH.exists():
        try:
            return json.loads(ALERTS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save_alert(entry: dict[str, Any]) -> None:
    alerts = _load_alerts()
    alerts.append(entry)
    ALERTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ALERTS_PATH.write_text(json.dumps(alerts, indent=2), encoding="utf-8")


@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@api_bp.route("/aq/latest", methods=["GET"])
def get_latest():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    location_id = request.args.get("location_id")

    location = _resolve_location(location_id, lat, lon)
    if location is None:
        return (
            jsonify(
                {
                    "error": "location_not_found",
                    "message": "Provide a valid location_id or lat/lon pair within Monterrey's monitoring network.",
                    "available_location_ids": sorted(_locations_index()["location_id"].unique().tolist()),
                }
            ),
            404,
        )

    openaq_id = int(float(location["location_id"]))
    if openaq_id not in SENSORS_DICT.values():
        return (
            jsonify(
                {
                    "error": "unsupported_location",
                    "message": "The requested location_id is not part of the configured OpenAQ stations.",
                    "allowed_ids": sorted(str(v) for v in SENSORS_DICT.values()),
                }
            ),
            400,
        )

    aq_client = OpenAQClient()

    details_payload = aq_client.location_details(openaq_id)
    detail_results = details_payload.get("results", [])
    detail = detail_results[0] if detail_results else {}

    sensor_map: dict[int, dict[str, Any]] = {}
    for sensor in detail.get("sensors", []):
        sensor_id = sensor.get("id")
        if sensor_id is None:
            continue
        parameter = None
        unit = None
        if isinstance(sensor.get("parameter"), dict):
            parameter = sensor["parameter"].get("name")
            unit = sensor["parameter"].get("units")
        sensor_map[int(sensor_id)] = {
            "parameter": parameter,
            "unit": unit or sensor.get("unit"),
        }

    latest_payload = aq_client.location_latest(location_id=openaq_id)
    results = latest_payload.get("results", [])

    measurement_map: dict[str, dict[str, Any]] = {}
    for entry in results:
        sensor_id = entry.get("sensorsId")
        meta = sensor_map.get(int(sensor_id)) if sensor_id is not None else None
        parameter = meta.get("parameter") if meta else None
        if not parameter:
            continue

        measurement_map[parameter] = {
            "value": entry.get("value"),
            "unit": meta.get("unit"),
            "last_updated": (entry.get("datetime") or {}).get("utc"),
            "quality": entry.get("quality"),
            "sensor_id": sensor_id,
        }

    pm25_value = measurement_map.get("pm25", {}).get("value")
    no2_value = measurement_map.get("no2", {}).get("value")

    try:
        ow_client = OpenWeatherClient()
        try:
            weather_payload = ow_client.one_call(
                lat=location.get("lat"), lon=location.get("lon"), exclude=("minutely", "alerts")
            )
            current = weather_payload.get("current", {})
            weather: dict[str, Any] = {
                "temperature": current.get("temp"),
                "humidity": current.get("humidity"),
                "pressure": current.get("pressure"),
                "wind_speed": current.get("wind_speed"),
                "description": current.get("weather", [{}])[0].get("description"),
            }
        except OneCallNotAvailableError:
            fallback = ow_client.current_weather(lat=location.get("lat"), lon=location.get("lon"))
            weather = {
                "temperature": fallback.get("main", {}).get("temp"),
                "humidity": fallback.get("main", {}).get("humidity"),
                "pressure": fallback.get("main", {}).get("pressure"),
                "wind_speed": fallback.get("wind", {}).get("speed"),
                "description": (fallback.get("weather", [{}])[0] or {}).get("description"),
            }
    except Exception as exc:  # noqa: BLE001
        weather = {"error": str(exc)}

    response = {
        "location": {
            "id": location.get("location_id"),
            "name": location.get("location_name"),
            "lat": location.get("lat"),
            "lon": location.get("lon"),
        },
        "measurements": measurement_map,
        "aqi": _compute_pm25_aqi(pm25_value),
        "weather": weather,
        "sources": {
            "openaq": {
                "id": detail.get("id") or openaq_id,
                "name": detail.get("name"),
                "city": detail.get("city") or detail.get("locality"),
                "coordinates": detail.get("coordinates"),
                "datetime_first": detail.get("datetimeFirst"),
                "datetime_last": detail.get("datetimeLast"),
            }
        },
    }

    return jsonify(response)


@api_bp.route("/aq/predictions", methods=["GET"])
def get_predictions():
    rows = request.args.get("rows", default=1, type=int)
    include_particles = request.args.get("include_particles", default="true").lower() not in {"false", "0", "no"}
    location_id = request.args.get("location_id")

    rows = max(rows, 1)

    try:
        base_dataset = inference._load_base_dataset()
    except FileNotFoundError:
        return (
            jsonify({"error": "Dataset not found. Run the ETL pipeline to generate output/dataset_final.csv."}),
            500,
        )

    if location_id:
        filtered = base_dataset[base_dataset["location_id"].astype(str) == str(location_id)]
        if filtered.empty:
            return (
                jsonify(
                    {
                        "error": f"No data found for location_id={location_id}.",
                        "available_location_ids": sorted(
                            base_dataset["location_id"].astype(str).unique().tolist()
                        ),
                    }
                ),
                404,
            )
        sample = filtered.tail(rows).reset_index(drop=True)
    else:
        sample = base_dataset.tail(rows).reset_index(drop=True)

    inputs_df = sample.copy()
    if "datetime" in inputs_df:
        inputs_df["datetime"] = inputs_df["datetime"].astype(str)

    response: dict[str, Any] = {
        "rows": rows,
        "inputs": json.loads(inputs_df.to_json(orient="records")) if not inputs_df.empty else [],
    }

    try:
        gas_predictions = inference.predict_gases(sample.copy())
        response["gases"] = json.loads(gas_predictions.to_json(orient="records"))
    except FileNotFoundError:
        response["gases_error"] = "Gas model artifacts not found. Train the gas model first."

    if include_particles:
        particle_results: dict[str, Any] = {}
        particle_errors: dict[str, str] = {}
        for target in ("pm10", "pm25"):
            try:
                preds = inference.predict_particle(target, sample.copy())
                particle_results[target] = [float(value) for value in preds.tolist()]
            except FileNotFoundError:
                particle_results[target] = None
                particle_errors[target] = f"CatBoost artifacts for {target} not found."

        response["particles"] = particle_results
        if particle_errors:
            response["particle_errors"] = particle_errors

    return jsonify(response)


@api_bp.route("/aq/trends", methods=["GET"])
def get_trends():
    days = request.args.get("days", default=7, type=int)
    location_id = request.args.get("location_id")

    if not location_id:
        return (
            jsonify({"error": "missing_location_id", "message": "Provide ?location_id=<sensor_id>"}),
            400,
        )

    days = max(days, 1)

    df = _get_dataset_for_location(str(location_id), days=days)
    if df.empty:
        return (
            jsonify({"error": "location_not_found", "message": "No data available for that location."}),
            404,
        )

    df = df.sort_values("datetime")
    series: dict[str, Any] = {}
    for pollutant in ("pm25", "no2"):
        if pollutant in df.columns:
            series[pollutant] = df[["datetime", pollutant]].dropna().to_dict(orient="records")

    corr_value: float | None = None
    if {"pm25", "no2"}.issubset(df.columns):
        corr_df = df[["pm25", "no2"]].dropna()
        if not corr_df.empty:
            corr_value = float(corr_df["pm25"].corr(corr_df["no2"]))

    return jsonify(
        {
            "location_id": str(location_id),
            "days": days,
            "series": series,
            "correlation_pm25_no2": corr_value,
        }
    )


@api_bp.route("/aq/forecast", methods=["GET"])
def get_forecast():
    location_id = request.args.get("location_id")
    pollutant = request.args.get("pollutant", default="pm25")
    hours = request.args.get("h", default=24, type=int)

    if not location_id:
        return (
            jsonify({"error": "missing_location_id", "message": "Provide ?location_id=<sensor_id>"}),
            400,
        )

    hours = max(1, min(hours, 168))

    df = _get_dataset_for_location(str(location_id))
    if pollutant not in df.columns:
        return (
            jsonify({"error": "invalid_pollutant", "message": f"Pollutant '{pollutant}' not present."}),
            400,
        )

    df = df.sort_values("datetime")
    history = df[["datetime", pollutant]].dropna()
    if history.empty:
        return (
            jsonify({"error": "no_data", "message": "No historical values available."}),
            404,
        )

    baseline = history.tail(24)
    yhat = baseline[pollutant].mean()
    std = baseline[pollutant].std(ddof=0) if baseline.shape[0] > 1 else 0.0
    last_ts = baseline["datetime"].max()

    predictions = []
    for step in range(1, hours + 1):
        ts = (last_ts + pd.Timedelta(hours=step)).isoformat()
        predictions.append(
            {
                "timestamp": ts,
                "yhat": float(yhat),
                "pi_low": float(max(0.0, yhat - 1.28 * std)),
                "pi_high": float(yhat + 1.28 * std),
            }
        )

    return jsonify(
        {
            "location_id": str(location_id),
            "pollutant": pollutant,
            "hours": hours,
            "model": "naive_mean",
            "predictions": predictions,
        }
    )


@api_bp.route("/aq/sources", methods=["GET"])
def get_sources():
    locations = _locations_index()
    air_quality = [
        {
            "location_id": row.location_id,
            "location_name": row.location_name,
            "lat": row.lat,
            "lon": row.lon,
            "openaq_id": SENSORS_DICT.get(row.location_name, row.location_id),
        }
        for row in locations.itertuples()
    ]

    weather = [
        {
            "station_id": station_id,
            "name": info["name"],
            "lat": info["lat"],
            "lon": info["lon"],
        }
        for station_id, info in WEATHER_STATIONS_DICT.items()
    ]

    return jsonify({"air_quality": air_quality, "weather": weather})


@api_bp.route("/alerts/subscribe", methods=["POST"])
def subscribe_alerts():
    payload = request.get_json(silent=True)
    if not payload or "contact" not in payload:
        return (
            jsonify({"error": "invalid_payload", "message": "Payload must include 'contact'."}),
            400,
        )

    entry = {
        "contact": payload.get("contact"),
        "preferences": payload.get("preferences", {}),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _save_alert(entry)

    return jsonify({"success": True, "stored": entry})
