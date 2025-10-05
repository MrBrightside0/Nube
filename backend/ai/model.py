#!/usr/bin/env python3
"""
Modelo de red neuronal para predicción de contaminación del aire.
Entrena sobre dataset_final.csv generado desde datos NASA TEMPO + MERRA-2.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence

import torch
from torch import Tensor, nn
from torch.utils.data import DataLoader, TensorDataset
from torch.optim import Optimizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np


# ============================================
# CONFIGURACIÓN
# ============================================

@dataclass
class ModelConfig:
    """Hiperparámetros del modelo."""
    input_dim: int
    hidden_dims: Sequence[int] = (128, 64)
    output_dim: int = 1
    dropout: float = 0.2
    lr: float = 1e-3
    epochs: int = 50
    batch_size: int = 64
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


# ============================================
# MODELO
# ============================================

class NeuralNetwork(nn.Module):
    """Red neuronal feed-forward para contaminación del aire."""

    def __init__(self, config: ModelConfig):
        super().__init__()
        self.config = config
        self.model = self._build_layers()

    def _build_layers(self) -> nn.Sequential:
        dims = [self.config.input_dim, *self.config.hidden_dims, self.config.output_dim]
        layers: list[nn.Module] = []
        for i in range(len(dims) - 1):
            layers.append(nn.Linear(dims[i], dims[i + 1]))
            if i < len(dims) - 2:
                layers.append(nn.ReLU())
                layers.append(nn.Dropout(self.config.dropout))
        return nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        return self.model(x)


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def load_dataset(csv_path: str, target: str = "NO2_tropo"):
    """Carga el dataset, selecciona features relevantes y normaliza."""
    df = pd.read_csv(csv_path)

    feature_cols = [
        "T2M", "QV2M", "wind_speed", "wind_dir", "PS",
        "sin_hour", "cos_hour", "PM25_est", "PM10_est"
    ]
    df = df.dropna(subset=[target, *feature_cols])

    X = df[feature_cols].values
    y = df[[target]].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    train_ds = TensorDataset(torch.tensor(X_train, dtype=torch.float32),
                             torch.tensor(y_train, dtype=torch.float32))
    test_ds = TensorDataset(torch.tensor(X_test, dtype=torch.float32),
                            torch.tensor(y_test, dtype=torch.float32))

    return train_ds, test_ds, scaler


def create_optimizer(model: nn.Module, lr: float = 1e-3) -> Optimizer:
    return torch.optim.Adam(model.parameters(), lr=lr)


def train_model(model: nn.Module, train_loader, test_loader, config: ModelConfig):
    """Entrena el modelo y evalúa cada epoch."""
    criterion = nn.MSELoss()
    optimizer = create_optimizer(model, config.lr)

    model.to(config.device)
    for epoch in range(1, config.epochs + 1):
        model.train()
        train_loss = 0.0
        for Xb, yb in train_loader:
            Xb, yb = Xb.to(config.device), yb.to(config.device)
            optimizer.zero_grad()
            preds = model(Xb)
            loss = criterion(preds, yb)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # Evaluación
        model.eval()
        test_loss = 0.0
        with torch.no_grad():
            for Xb, yb in test_loader:
                Xb, yb = Xb.to(config.device), yb.to(config.device)
                preds = model(Xb)
                test_loss += criterion(preds, yb).item()

        print(
            f"Epoch {epoch:03d} | "
            f"Train Loss: {train_loss/len(train_loader):.6f} | "
            f"Test Loss: {test_loss/len(test_loader):.6f}"
        )


# ============================================
# MAIN DE ENTRENAMIENTO
# ============================================

def main():
    data_path = "data/dataset_final.csv"
    target = "NO2_tropo"  # Puedes cambiarlo a "PM25_est" o "PM10_est"

    print(f"[INFO] Cargando dataset desde {data_path}")
    train_ds, test_ds, scaler = load_dataset(data_path, target=target)

    train_loader = DataLoader(train_ds, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=64, shuffle=False)

    config = ModelConfig(input_dim=train_ds.tensors[0].shape[1], output_dim=1, epochs=60)
    model = NeuralNetwork(config)

    print(f"[INFO] Entrenando modelo para predecir: {target}")
    train_model(model, train_loader, test_loader, config)

    # Guardar modelo y escalador
    torch.save(model.state_dict(), f"model_{target}.pt")
    np.save("scaler_mean.npy", scaler.mean_)
    np.save("scaler_scale.npy", scaler.scale_)
    print(f"[OK] Modelo guardado como model_{target}.pt")


if __name__ == "__main__":
    main()

