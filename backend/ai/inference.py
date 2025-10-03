from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple
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


__all__ = [
    "predict_gases",
    "predict_particle",
    "load_gas_artifacts",
    "load_particle_artifacts",
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
