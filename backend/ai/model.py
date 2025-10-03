from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
from preprocessor import AirQualityPreprocessor
import numpy as np

# Assuming X_train, X_test, y_train, y_test already exist
dataset_path = "output/dataset_final.csv"
pollutants = ['co', 'no', 'no2', 'nox', 'o3', 'pm10', 'pm25', 'so2']

preprocessor = AirQualityPreprocessor(dataset_path)
X_train, X_test, y_train, y_test = preprocessor.preprocess(pollutants)

rf_model = MultiOutputRegressor(RandomForestRegressor(
    n_estimators=500,
    max_depth=None,
    random_state=42,
    min_samples_leaf=2,
    n_jobs=-1
))

rf_model.fit(X_train, y_train)

# Predict
y_pred = rf_model.predict(X_test)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred, multioutput='uniform_average')

print(f"[INFO] Random Forest Multi-Output MSE: {mse:.4f}, R2: {r2:.4f}")

