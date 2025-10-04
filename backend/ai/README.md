# AI Models Overview

This document explains the workflows inside `backend/ai`, what each script produces, and how those artifacts are consumed by the API.

## Data Preparation (`create_dataset.py`)
- Loads hourly air-quality CSVs (`ai/air_data/`), Meteostat weather sources (`ai/weather_data/`), and engineered features (rolling windows, lagged deltas, calendar variables).
- Normalises station identifiers, merges all sources, and writes the consolidated file to `ai/output/dataset_final.csv`.
- Every downstream step assumes this CSV exists. Regenerate it each time new raw data is ingested.

## Core Training Pipeline (`model.py`)
- Reads `dataset_final.csv`, interpolates short gaps per station, and augments the feature space (sin/cos for hour and month, PM10/PM25 ratio, etc.).
- Trains two model families:
  1. **Gas neural network** (TensorFlow) predicts `co`, `no`, `no2`, `nox`, `o3`, and `so2` simultaneously. Features are standardised and a temporal split (80/20) is used for evaluation. Console logs show `MSE`, `RMSE`, and `R^2` per target.
  2. **Particle regressors** (CatBoost) for `pm10` and `pm25`. Each target trains with the same temporal split, reporting `MSE`, `RMSE`, and `R^2` on the validation fold.
- Outputs are stored under `ai/models/`:
  - `gas_model.keras`, `scaler_X_gases.joblib`, `scaler_y_gases.joblib`, and `gas_model_metadata.json`.
  - `catboost_pm10.cbm`, `catboost_pm10_metadata.json`, and the analogous files for PM2.5.
- Metadata captures the feature columns and fill values required during inference. The API relies on these files when serving `/api/aq/predictions` and the metropolitan summaries.

## Inference Utilities (`inference.py`)
- `predict_gases(df)` and `predict_particle(target, df)` recreate the preprocessing pipeline and load the saved artifacts.
- `build_metropolitan_summary(rows_per_location)` aggregates the latest rows for every station, runs the models, and returns a JSON-ready structure with per-location observations, statistics, and highlights. This powers `/api/aq/metropolitan-summary`.
- `build_metropolitan_forecast(hours, window_hours, pollutants)` computes a baseline projection using rolling averages (not a learned temporal model). The API exposes it via `/api/aq/metropolitan-forecast`.
- Running `python ai/inference.py --rows 5` prints sample predictions for manual inspection.

## OpenAI Assistant (`api/openai_assistant.py`)
- Builds natural-language prompts for either a single station or the metropolitan aggregate and calls OpenAI's Chat Completions API (`gpt-4o-mini`).
- Consumed by the `/api/aq/recommendations` endpoint to deliver actionable guidance for autoridades/ciudadania. Requires `OPENAI_API_KEY` and the `openai` package.

## Prophet Exploratory Scripts (`predict_data.py`)
- Loads raw CSVs for a given location, aggregates to daily granularity, and fits Facebook Prophet to a single pollutant.
- Returns the forecast DataFrame and plots trend/seasonality components. This script is offline exploratory work; the Flask API does not consume Prophet outputs yet.

## Outputs and Next Steps
- `ai/models/` holds the production artifacts; clean or version them before retraining.
- `ai/output/dataset_final.csv` is the canonical table consumed by both training and inference.
- When evaluating model quality, rely on the metrics printed by `model.py` or extend it with explicit reports (MAE, MAPE, cross-validation).
- Upgrading the forecast quality would involve replacing the baseline with a true temporal model (Prophet, CatBoost multi-step, LSTM) and reusing the same response schema exposed by the API.
