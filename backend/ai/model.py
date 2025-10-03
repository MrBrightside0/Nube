import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# -----------------------------
# Configuration
# -----------------------------
DATASET_PATH = "output/dataset_final.csv"
POLLUTANTS = ['co', 'no', 'no2', 'nox', 'o3', 'pm10', 'pm25', 'so2']
LAGS = 3
TRAIN_RATIO = 0.8
EPOCHS = 50
BATCH_SIZE = 64
VALIDATION_SPLIT = 0.2

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv(DATASET_PATH, parse_dates=['datetime'])
df.sort_values('datetime', inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"[INFO] Dataset loaded. Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# -----------------------------
# Handle missing values
# -----------------------------
numeric_cols = df.select_dtypes(include=[np.number]).columns
df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
print("[INFO] Missing values handled.")

# -----------------------------
# Add time features
# -----------------------------
df['hour'] = df['datetime'].dt.hour
df['day_of_week'] = df['datetime'].dt.dayofweek
df['month'] = df['datetime'].dt.month

df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
print("[INFO] Time features added.")

# -----------------------------
# Add lag features safely
# -----------------------------
for col in POLLUTANTS:
    df[col] = df[col].fillna(method='ffill').fillna(method='bfill')
    for lag in range(1, LAGS + 1):
        df[f"{col}_lag{lag}"] = df[col].shift(lag)

lag_cols = [f"{col}_lag{lag}" for col in POLLUTANTS for lag in range(1, LAGS+1)]
df.dropna(subset=lag_cols, inplace=True)
print(f"[INFO] Lag features added. New rows: {df.shape[0]}, Columns: {df.shape[1]}")

# -----------------------------
# Prepare features and targets
# -----------------------------
X = df.drop(columns=POLLUTANTS + ['datetime'])
y = df[POLLUTANTS]

# Remove zero-variance columns
X = X.loc[:, X.nunique() > 1]
y = y.loc[:, y.nunique() > 1]

# Fill any remaining NaNs
X = X.fillna(method='ffill').fillna(method='bfill')
y = y.fillna(method='ffill').fillna(method='bfill')

# Scale features and targets
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
X_scaled = np.nan_to_num(X_scaled)

scaler_y = StandardScaler()
y_scaled = scaler_y.fit_transform(y)
y_scaled = np.nan_to_num(y_scaled)

# Temporal train/test split
split_idx = int(len(df) * TRAIN_RATIO)
X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
y_train, y_test = y_scaled[:split_idx], y_scaled[split_idx:]
print(f"[INFO] Train/Test split done. Train rows: {X_train.shape[0]}, Test rows: {X_test.shape[0]}")

# -----------------------------
# Build Neural Network
# -----------------------------
n_features = X_train.shape[1]
n_targets = y_train.shape[1]

model = Sequential([
    Dense(128, input_dim=n_features, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(n_targets)
])

model.compile(optimizer='adam', loss='mse', metrics=['mse'])
model.summary()

# -----------------------------
# Train the model
# -----------------------------
history = model.fit(
    X_train, y_train,
    validation_split=VALIDATION_SPLIT,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=1
)

# -----------------------------
# Evaluate
# -----------------------------
y_pred_scaled = model.predict(X_test)
y_pred_scaled = np.nan_to_num(y_pred_scaled)  # ensure no NaNs

y_pred = scaler_y.inverse_transform(y_pred_scaled)
y_test_orig = scaler_y.inverse_transform(y_test)

mse = mean_squared_error(y_test_orig, y_pred)
r2 = r2_score(y_test_orig, y_pred, multioutput='uniform_average')
print(f"[INFO] Neural Network MSE: {mse:.4f}, R2: {r2:.4f}")

# Per-pollutant RMSE
for i, col in enumerate(POLLUTANTS):
    rmse = np.sqrt(mean_squared_error(y_test_orig[:, i], y_pred[:, i]))
    print(f"[INFO] {col} RMSE: {rmse:.4f}")

