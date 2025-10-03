import json

import numpy as np
import pandas as pd
import tensorflow as tf
from catboost import CatBoostRegressor, Pool
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
import joblib

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "output" / "dataset_final.csv"
MODELS_DIR = BASE_DIR / "models"
POLLUTANTS = ["co", "no", "no2", "nox", "o3", "pm10", "pm25", "so2"]
PARTICLE_TARGETS = ["pm10", "pm25"]
GAS_TARGETS = ["co", "no", "no2", "nox", "o3", "so2"]

TRAIN_RATIO = 0.8
EPOCHS = 50
BATCH_SIZE = 64
VALIDATION_SPLIT = 0.2


def interpolate_pollutants(df: pd.DataFrame, group_key: str) -> pd.DataFrame:
    df = df.sort_values([group_key, "datetime"])
    for col in [c for c in POLLUTANTS if c in df.columns]:
        df[col] = df.groupby(group_key)[col].transform(
            lambda s: s.interpolate(limit=6, limit_direction="both")
        )
    return df


def sanitize_numeric(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan)

    feature_cols = [col for col in numeric_cols if col not in POLLUTANTS]
    df[feature_cols] = df[feature_cols].apply(lambda col: col.fillna(col.median()))
    return df

# -----------------------------
# Load and preprocess dataset
# -----------------------------
df = pd.read_csv(DATASET_PATH, parse_dates=["datetime"])
df.sort_values(["datetime", "location_id"], inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"[INFO] Dataset loaded. Rows: {df.shape[0]}, Columns: {df.shape[1]}")

MODELS_DIR.mkdir(parents=True, exist_ok=True)

df["location_id"] = df["location_id"].astype(str)
df = interpolate_pollutants(df, "location_id")

if {"pm10", "pm25"}.issubset(df.columns):
    df["pm_ratio"] = df["pm10"] / df["pm25"].replace(0, np.nan)

df = sanitize_numeric(df)
df_particles = df.copy()

available_targets = [col for col in POLLUTANTS if col in df.columns]
df = df.dropna(subset=available_targets)
df.reset_index(drop=True, inplace=True)

for frame in (df, df_particles):
    frame["hour_sin"] = np.sin(2 * np.pi * frame["hour"] / 24)
    frame["hour_cos"] = np.cos(2 * np.pi * frame["hour"] / 24)
    frame["month_sin"] = np.sin(2 * np.pi * frame["month"] / 12)
    frame["month_cos"] = np.cos(2 * np.pi * frame["month"] / 12)

# -----------------------------
# GAS MODEL - Neural Network
# -----------------------------
i_cols_to_drop = POLLUTANTS + ["datetime", "location_name", "location_id"]
X_gases = df.drop(columns=[col for col in i_cols_to_drop if col in df.columns])
gas_target_cols = [col for col in GAS_TARGETS if col in df.columns]
y_gases = df[gas_target_cols]

X_gases = X_gases.loc[:, X_gases.nunique() > 1]
y_gases = y_gases.loc[:, y_gases.nunique() > 1]

gas_feature_medians: dict[str, float] = {
    col: float(X_gases[col].median()) for col in X_gases.columns
}
X_gases = X_gases.fillna(gas_feature_medians)
y_gases = y_gases.ffill().bfill()

scaler_X_gases = StandardScaler()
X_scaled = scaler_X_gases.fit_transform(X_gases)

scaler_y_gases = StandardScaler()
y_scaled = scaler_y_gases.fit_transform(y_gases)

train_cutoff = df["datetime"].quantile(TRAIN_RATIO)
train_mask = df["datetime"] <= train_cutoff

X_train, X_test = X_scaled[train_mask], X_scaled[~train_mask]
y_train, y_test = y_scaled[train_mask], y_scaled[~train_mask]
print(f"[INFO] Train/Test split for gases done. Train rows: {X_train.shape[0]}, Test rows: {X_test.shape[0]}")

n_features = X_train.shape[1]
n_targets = y_train.shape[1]

model = Sequential([
    Dense(128, input_dim=n_features, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(n_targets)
])

model.compile(optimizer='adam', loss='mse', metrics=['mse'])
model.fit(X_train, y_train,
          validation_split=VALIDATION_SPLIT,
          epochs=EPOCHS,
          batch_size=BATCH_SIZE,
          verbose=1)

y_pred_scaled = model.predict(X_test)
y_pred_scaled = np.nan_to_num(y_pred_scaled)
y_pred = scaler_y_gases.inverse_transform(y_pred_scaled)
y_test_orig = scaler_y_gases.inverse_transform(y_test)

mse = mean_squared_error(y_test_orig, y_pred)
r2 = r2_score(y_test_orig, y_pred, multioutput='uniform_average')
print(f"[INFO] Neural Network Gases MSE: {mse:.4f}, R2: {r2:.4f}")

for i, col in enumerate(gas_target_cols):
    rmse = np.sqrt(mean_squared_error(y_test_orig[:, i], y_pred[:, i]))
    print(f"[INFO] {col} RMSE: {rmse:.4f}")

gas_model_path = MODELS_DIR / "gas_model.keras"
model.save(gas_model_path)

joblib.dump(scaler_X_gases, MODELS_DIR / "scaler_X_gases.joblib")
joblib.dump(scaler_y_gases, MODELS_DIR / "scaler_y_gases.joblib")

gas_metadata = {
    "feature_columns": list(X_gases.columns),
    "target_columns": gas_target_cols,
    "train_cutoff": train_cutoff.isoformat() if hasattr(train_cutoff, "isoformat") else str(train_cutoff),
    "numeric_fill_values": gas_feature_medians,
}

with open(MODELS_DIR / "gas_model_metadata.json", "w", encoding="utf-8") as metadata_file:
    json.dump(gas_metadata, metadata_file, indent=2, ensure_ascii=False)

# ----------------------------
# PARTICLE MODELS - CatBoost
# -----------------------------
exclude_cols = ["datetime", "location_name"] + POLLUTANTS
particle_target_cols = [col for col in PARTICLE_TARGETS if col in df_particles.columns]

for target in particle_target_cols:
    df_target = df_particles.dropna(subset=[target]).copy()
    if df_target.empty:
        print(f"[WARN] Sin datos suficientes para entrenar {target}")
        continue

    feature_drop = [col for col in exclude_cols if col in df_target.columns]
    feature_drop.append(target)

    X_target = df_target.drop(columns=feature_drop, errors="ignore")
    X_target = X_target.loc[:, X_target.nunique(dropna=False) > 1]

    numeric_fill_values: dict[str, float] = {}
    for col in X_target.columns:
        if X_target[col].dtype.kind in "biufc":
            median_val = X_target[col].median()
            if pd.isna(median_val):
                median_val = 0.0
            numeric_fill_values[col] = float(median_val)
            X_target[col] = X_target[col].fillna(median_val)
        else:
            X_target[col] = X_target[col].fillna("missing")
    y_target = df_target[target]

    feature_names = list(X_target.columns)

    cat_features = []
    if "location_id" in X_target.columns:
        cat_features.append(list(X_target.columns).index("location_id"))

    target_cutoff = df_target["datetime"].quantile(TRAIN_RATIO)
    train_mask_target = df_target["datetime"] <= target_cutoff
    X_train_target, X_test_target = X_target[train_mask_target], X_target[~train_mask_target]
    y_train_target, y_test_target = y_target[train_mask_target], y_target[~train_mask_target]

    train_pool = Pool(X_train_target, y_train_target, cat_features=cat_features)
    valid_pool = Pool(X_test_target, y_test_target, cat_features=cat_features)

    model_pm = CatBoostRegressor(
        loss_function="RMSE",
        depth=8,
        learning_rate=0.035,
        n_estimators=2500,
        subsample=0.8,
        bootstrap_type="Bernoulli",
        l2_leaf_reg=4.0,
        random_state=42,
        eval_metric="RMSE",
        verbose=200,
    )

    model_pm.fit(
        train_pool,
        eval_set=valid_pool,
        use_best_model=True,
        early_stopping_rounds=200,
    )

    y_pred_pm = model_pm.predict(valid_pool)

    mse_pm = mean_squared_error(y_test_target, y_pred_pm)
    rmse_pm = np.sqrt(mse_pm)
    r2_pm = r2_score(y_test_target, y_pred_pm)

    print(
        f"[INFO] CatBoost {target.upper()} MSE: {mse_pm:.4f}, RMSE: {rmse_pm:.4f}, R2: {r2_pm:.4f}"
    )

    model_path = MODELS_DIR / f"catboost_{target}.cbm"
    model_pm.save_model(model_path)

    metadata = {
        "target": target,
        "feature_columns": feature_names,
        "cat_feature_indices": cat_features,
        "train_cutoff": target_cutoff.isoformat() if hasattr(target_cutoff, "isoformat") else str(target_cutoff),
        "train_rows": int(train_mask_target.sum()),
        "test_rows": int((~train_mask_target).sum()),
        "numeric_fill_values": numeric_fill_values,
    }

    metadata_path = MODELS_DIR / f"catboost_{target}_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)

    importances = model_pm.get_feature_importance(train_pool, type="FeatureImportance")
    importance_df = pd.DataFrame({"feature": feature_names, "importance": importances})
    importance_df.sort_values("importance", ascending=False, inplace=True)

    importance_path = MODELS_DIR / f"catboost_{target}_feature_importance.csv"
    importance_df.to_csv(importance_path, index=False)

    top_features = importance_df.head(10)
    print("[INFO] Top features for", target, ":")
    for _, row in top_features.iterrows():
        print(f"        {row['feature']}: {row['importance']:.4f}")
