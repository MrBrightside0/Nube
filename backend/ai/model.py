import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from catboost import CatBoostRegressor

DATASET_PATH = "output/dataset_final.csv"
POLLUTANTS = ['co', 'no', 'no2', 'nox', 'o3', 'pm10', 'pm25', 'so2']
POLLUTANTS_PM = ['pm10', 'pm25']
POLLUTANTS_GASES = ['co', 'no', 'no2', 'nox', 'o3', 'so2']

LAGS = 3
TRAIN_RATIO = 0.8
EPOCHS = 50
BATCH_SIZE = 64
VALIDATION_SPLIT = 0.2

# -----------------------------
# Load and preprocess dataset
# -----------------------------
df = pd.read_csv(DATASET_PATH, parse_dates=['datetime'])
df.sort_values('datetime', inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"[INFO] Dataset loaded. Rows: {df.shape[0]}, Columns: {df.shape[1]}")

numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].ffill().bfill()
print("[INFO] Missing values handled.")

df['hour'] = df['datetime'].dt.hour
df['day_of_week'] = df['datetime'].dt.dayofweek
df['month'] = df['datetime'].dt.month

df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
print("[INFO] Time features added.")

for col in POLLUTANTS:
    df[col] = df[col].ffill().bfill()
    for lag in range(1, LAGS + 1):
        df[f"{col}_lag{lag}"] = df[col].shift(lag)

lag_cols = [f"{col}_lag{lag}" for col in POLLUTANTS for lag in range(1, LAGS+1)]
df.dropna(subset=lag_cols, inplace=True)
print(f"[INFO] Lag features added. New rows: {df.shape[0]}, Columns: {df.shape[1]}")

# -----------------------------
# GAS MODEL - Neural Network
# -----------------------------
X_gases = df.drop(columns=POLLUTANTS + ['datetime'])
y_gases = df[POLLUTANTS]

X_gases = X_gases.loc[:, X_gases.nunique() > 1]
y_gases = y_gases.loc[:, y_gases.nunique() > 1]

X_gases = X_gases.ffill().bfill()
y_gases = y_gases.ffill().bfill()

scaler_X_gases = StandardScaler()
X_scaled = scaler_X_gases.fit_transform(X_gases)
X_scaled = np.nan_to_num(X_scaled)

scaler_y_gases = StandardScaler()
y_scaled = scaler_y_gases.fit_transform(y_gases)
y_scaled = np.nan_to_num(y_scaled)

split_idx = int(len(df) * TRAIN_RATIO)
X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
y_train, y_test = y_scaled[:split_idx], y_scaled[split_idx:]
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

for i, col in enumerate(POLLUTANTS):
    rmse = np.sqrt(mean_squared_error(y_test_orig[:, i], y_pred[:, i]))
    print(f"[INFO] {col} RMSE: {rmse:.4f}")

# ----------------------------
# PARTICLE MODEL - CatBoost
# -----------------------------
X_pm = df.drop(columns=['datetime'] + POLLUTANTS)
y_pm = df[POLLUTANTS_PM].values

split_idx_pm = int(len(df) * TRAIN_RATIO)
X_train_pm, X_test_pm = X_pm.iloc[:split_idx_pm], X_pm.iloc[split_idx_pm:]
y_train_pm, y_test_pm = y_pm[:split_idx_pm], y_pm[split_idx_pm:]

model_pm = CatBoostRegressor(
    loss_function='MultiRMSE',
    depth=8,
    learning_rate=0.05,
    n_estimators=1500,
    bootstrap_type='Bernoulli',   # <--- agregado
    subsample=0.8,                 # <--- ahora sí válido
    random_state=42,
    verbose=200
)

model_pm.fit(X_train_pm, y_train_pm,
             eval_set=(X_test_pm, y_test_pm),
             use_best_model=True)

y_pred_pm = model_pm.predict(X_test_pm)

mse_pm = mean_squared_error(y_test_pm, y_pred_pm)
r2_pm = r2_score(y_test_pm, y_pred_pm, multioutput='uniform_average')
print(f"[INFO] CatBoost Particles MSE: {mse_pm:.4f}, R2: {r2_pm:.4f}")

for i, col in enumerate(POLLUTANTS_PM):
    rmse = np.sqrt(mean_squared_error(y_test_pm[:, i], y_pred_pm[:, i]))
    print(f"[INFO] {col} RMSE: {rmse:.4f}")

