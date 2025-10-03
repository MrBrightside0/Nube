import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class AirQualityPreprocessor:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.X = None
        self.y = None
        self.scaler_X = None
        self.scaler_y = None
        self.train_size = 0.8
        self.X_train = self.X_test = None
        self.y_train = self.y_test = None

    def load_data(self):
        """Load dataset and parse datetime."""
        self.df = pd.read_csv(self.csv_path, parse_dates=['datetime'])
        self.df.sort_values('datetime', inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        print(f"[INFO] Dataset loaded. Rows: {self.df.shape[0]}, Columns: {self.df.shape[1]}")

    def handle_missing(self):
        """Interpolate missing values using time index and fill remaining NaNs."""
        self.df.set_index('datetime', inplace=True)
        self.df.interpolate(method='time', inplace=True)
        self.df.fillna(method='bfill', inplace=True)
        self.df.fillna(method='ffill', inplace=True)
        self.df.reset_index(inplace=True)
        print("[INFO] Missing values handled.")

    def add_time_features(self):
        """Add time-based features and cyclic encoding."""
        self.df['hour'] = self.df['datetime'].dt.hour
        self.df['day_of_week'] = self.df['datetime'].dt.dayofweek
        self.df['month'] = self.df['datetime'].dt.month

        self.df['hour_sin'] = np.sin(2 * np.pi * self.df['hour'] / 24)
        self.df['hour_cos'] = np.cos(2 * np.pi * self.df['hour'] / 24)
        self.df['month_sin'] = np.sin(2 * np.pi * self.df['month'] / 12)
        self.df['month_cos'] = np.cos(2 * np.pi * self.df['month'] / 12)
        print("[INFO] Time features added.")

    def prepare_features_targets(self, pollutant_columns):
        """Separate features and multi-target variables."""
        self.y = self.df[pollutant_columns]
        self.X = self.df.drop(columns=pollutant_columns + ['datetime'])
        print(f"[INFO] Features and targets prepared. Features: {self.X.shape[1]}, Targets: {self.y.shape[1]}")

    def scale_data(self):
        """Scale features and targets."""
        self.scaler_X = StandardScaler()
        self.X = self.scaler_X.fit_transform(self.X)

        self.scaler_y = StandardScaler()
        self.y = self.scaler_y.fit_transform(self.y)
        print("[INFO] Features and targets scaled.")

    def train_test_split_time(self):
        """Split dataset into train/test using temporal split."""
        split_idx = int(len(self.df) * self.train_size)
        self.X_train, self.X_test = self.X[:split_idx], self.X[split_idx:]
        self.y_train, self.y_test = self.y[:split_idx], self.y[split_idx:]
        print(f"[INFO] Train/test split done. Train rows: {self.X_train.shape[0]}, Test rows: {self.X_test.shape[0]}")

    def preprocess(self, pollutant_columns):
        self.load_data()
        self.handle_missing()
        self.add_time_features()
        self.prepare_features_targets(pollutant_columns)
        self.scale_data()
        self.train_test_split_time()
        return self.X_train, self.X_test, self.y_train, self.y_test

if __name__ == "__main__":
    dataset_path = "output/dataset_final.csv"
    pollutants = ['co', 'no', 'no2', 'nox', 'o3', 'pm10', 'pm25', 'so2']

    preprocessor = AirQualityPreprocessor(dataset_path)
    X_train, X_test, y_train, y_test = preprocessor.preprocess(pollutants)

    print(f"[INFO] Preprocessing complete. X_train: {X_train.shape}, y_train: {y_train.shape}")



