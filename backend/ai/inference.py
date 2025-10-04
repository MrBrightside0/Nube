from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple
import argparse

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor, Pool
from tensorflow.keras.models import load_model

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DATASET_PATH = BASE_DIR / "output" / "dataset_final.csv"


def _load_base_dataset() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    dataset = pd.read_csv(DATASET_PATH, parse_dates=["datetime"])
    if "datetime" in dataset.columns:
        dataset = dataset.sort_values(["datetime"]).reset_index(drop=True)
    return dataset


def _ensure_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Return a copy of frame that includes every column in `columns` (filled with NaN)."""
    frame = frame.copy()
    for col in columns:
        if col not in frame.columns:
            frame[col] = np.nan
    return frame[columns]


def load_gas_artifacts() -> Tuple:
    model = load_model(MODELS_DIR / "gas_model.keras")
    scaler_X = joblib.load(MODELS_DIR / "scaler_X_gases.joblib")
    scaler_y = joblib.load(MODELS_DIR / "scaler_y_gases.joblib")
    metadata = json.loads((MODELS_DIR / "gas_model_metadata.json").read_text(encoding="utf-8"))
    return model, scaler_X, scaler_y, metadata


def predict_gases(features: pd.DataFrame) -> pd.DataFrame:
    model, scaler_X, scaler_y, metadata = load_gas_artifacts()
    required = metadata["feature_columns"]

    prepared = _ensure_columns(features, required)
    fills = metadata.get("numeric_fill_values", {})
    for col, value in fills.items():
        if col in prepared.columns:
            prepared[col] = pd.to_numeric(prepared[col], errors="coerce").fillna(value)

    prepared = prepared.astype(np.float32)
    scaled = scaler_X.transform(prepared)
    preds_scaled = model.predict(scaled)
    preds = scaler_y.inverse_transform(preds_scaled)
    return pd.DataFrame(preds, columns=metadata["target_columns"])


def load_particle_artifacts(target: str) -> tuple[CatBoostRegressor, dict]:
    model_path = MODELS_DIR / f"catboost_{target}.cbm"
    metadata_path = MODELS_DIR / f"catboost_{target}_metadata.json"
    if not model_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(f"No artifacts saved for target '{target}'.")

    model = CatBoostRegressor()
    model.load_model(model_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return model, metadata


def predict_particle(target: str, features: pd.DataFrame) -> np.ndarray:
    model, metadata = load_particle_artifacts(target)
    feature_columns = metadata["feature_columns"]
    cat_features = metadata["cat_feature_indices"]
    numeric_fills = metadata.get("numeric_fill_values", {})
    cat_columns = {feature_columns[idx] for idx in cat_features}

    prepared = _ensure_columns(features, feature_columns)
    for col, value in numeric_fills.items():
        if col in prepared.columns:
            prepared[col] = pd.to_numeric(prepared[col], errors="coerce").fillna(value)

    for idx in cat_features:
        col = feature_columns[idx]
        prepared[col] = prepared[col].astype(str).fillna("missing")

    for col in prepared.columns:
        if col not in numeric_fills and col not in cat_columns:
            prepared[col] = prepared[col].fillna(0)

    pool = Pool(prepared, cat_features=cat_features)
    return model.predict(pool)


def _to_iso(value: Any) -> str | None:
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        if value.tzinfo is None:
            return value.isoformat() + "Z"
        return value.isoformat()
    try:
        parsed = pd.to_datetime(value, utc=True)
        return parsed.isoformat()
    except (TypeError, ValueError):
        return None


def _build_stats(series: pd.Series) -> Dict[str, float] | None:
    cleaned = series.dropna()
    if cleaned.empty:
        return None
    return {
        "min": float(cleaned.min()),
        "max": float(cleaned.max()),
        "avg": float(cleaned.mean()),
    }


def build_metropolitan_summary(rows_per_location: int = 1) -> Dict[str, Any]:
    if rows_per_location < 1:
        raise ValueError("rows_per_location must be >= 1")

    dataset = _load_base_dataset()
    if dataset.empty:
        raise ValueError("Dataset is empty")

    dataset = dataset.copy()
    dataset["location_id"] = dataset["location_id"].astype(str)
    if "datetime" in dataset.columns:
        dataset = dataset.sort_values("datetime")

    snapshot = (
        dataset.groupby("location_id", group_keys=False)
        .tail(rows_per_location)
        .reset_index(drop=True)
    )

    if snapshot.empty:
        raise ValueError("Snapshot for metropolitan summary is empty")

    gas_predictions = None
    gas_error = None
    try:
        gas_predictions = predict_gases(snapshot.copy())
    except FileNotFoundError:
        gas_error = "Gas model artifacts not found."

    particle_predictions: Dict[str, Dict[int, float]] = {}
    particle_errors: Dict[str, str] = {}
    for target in ("pm10", "pm25"):
        try:
            preds = predict_particle(target, snapshot.copy())
            particle_predictions[target] = {
                idx: float(value) for idx, value in enumerate(preds)
            }
        except FileNotFoundError:
            particle_errors[target] = f"CatBoost artifacts for {target} not found."

    gas_map: Dict[int, Dict[str, float]] = {}
    if gas_predictions is not None and not gas_predictions.empty:
        for idx, row in gas_predictions.iterrows():
            gas_map[idx] = {k: float(v) for k, v in row.items()}

    locations_output: list[Dict[str, Any]] = []
    particle_values: Dict[str, list[float]] = {"pm10": [], "pm25": []}
    gas_values: Dict[str, list[float]] = {}

    grouped = snapshot.groupby(snapshot["location_id"], sort=False)

    for location_id, group in grouped:
        observations: list[Dict[str, Any]] = []
        last_row = group.iloc[-1]
        lat = last_row.get("lat")
        lon = last_row.get("lon")
        location_entry = {
            "location_id": location_id,
            "location_name": last_row.get("location_name") or location_id,
            "lat": float(lat) if pd.notna(lat) else None,
            "lon": float(lon) if pd.notna(lon) else None,
            "observations": observations,
        }

        for global_idx, row in group.iterrows():
            gases = gas_map.get(global_idx)
            if gases:
                for key, value in gases.items():
                    if pd.notna(value):
                        gas_values.setdefault(key, []).append(float(value))

            particles = {}
            for target in ("pm10", "pm25"):
                value = particle_predictions.get(target, {}).get(global_idx)
                particles[target] = value
                if value is not None:
                    particle_values.setdefault(target, []).append(value)

            observations.append(
                {
                    "datetime": _to_iso(row.get("datetime")),
                    "gases": gases,
                    "particles": particles,
                }
            )

        locations_output.append(location_entry)

    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "rows_per_location": rows_per_location,
        "locations_count": len(locations_output),
        "locations": locations_output,
        "summary": {
            "gases": {},
            "particles": {},
        },
    }

    if gas_predictions is not None and not gas_predictions.empty:
        for column, values in gas_values.items():
            series = pd.Series(values)
            stats = _build_stats(series)
            if stats:
                summary["summary"]["gases"][column] = stats
    if particle_values:
        for column, values in particle_values.items():
            if not values:
                continue
            series = pd.Series(values)
            stats = _build_stats(series)
            if stats:
                summary["summary"]["particles"][column] = stats

    highlights: Dict[str, Any] = {}
    if summary["summary"]["particles"].get("pm10"):
        best = None
        for entry in locations_output:
            latest = entry["observations"][-1]
            value = latest["particles"].get("pm10")
            if value is None:
                continue
            if best is None or value > best["value"]:
                best = {
                    "location_id": entry["location_id"],
                    "location_name": entry["location_name"],
                    "value": value,
                    "datetime": latest["datetime"],
                }
        if best:
            highlights["highest_pm10"] = best

    if summary["summary"]["particles"].get("pm25"):
        best = None
        for entry in locations_output:
            latest = entry["observations"][-1]
            value = latest["particles"].get("pm25")
            if value is None:
                continue
            if best is None or value > best["value"]:
                best = {
                    "location_id": entry["location_id"],
                    "location_name": entry["location_name"],
                    "value": value,
                    "datetime": latest["datetime"],
                }
        if best:
            highlights["highest_pm25"] = best

    if highlights:
        summary["highlights"] = highlights

    errors = {}
    if gas_error:
        errors["gases"] = gas_error
    errors.update(particle_errors)
    if errors:
        summary["errors"] = errors

    return summary


__all__ = [
    "predict_gases",
    "predict_particle",
    "load_gas_artifacts",
    "load_particle_artifacts",
    "build_metropolitan_summary",
]


def _print_dataframe(df: pd.DataFrame, label: str, rows: int) -> None:
    if df.empty:
        print(f"[WARN] {label} result is empty")
        return
    print(f"[INFO] {label} (top {rows} rows):")
    print(df.head(rows).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick smoke test for saved models.")
    parser.add_argument(
        "--rows",
        type=int,
        default=5,
        help="Number of rows from the dataset to use for the demo predictions.",
    )
    args = parser.parse_args()

    try:
        base_dataset = _load_base_dataset()
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(1)

    sample = base_dataset.tail(max(args.rows, 1)).reset_index(drop=True)

    try:
        gas_predictions = predict_gases(sample.copy())
        _print_dataframe(gas_predictions, "Gas predictions", args.rows)
    except FileNotFoundError:
        print("[WARN] Gas model artifacts not found. Run model.py first.")

    for target in ("pm10", "pm25"):
        try:
            preds = predict_particle(target, sample.copy())
            df_preds = pd.DataFrame({target: preds})
            _print_dataframe(df_preds, f"Particle prediction for {target}", args.rows)
        except FileNotFoundError:
            print(f"[WARN] CatBoost artifacts for {target} not found. Run model.py first.")
