from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import osmnx as ox
import pandas as pd

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrafficConfig:
    """Configuration parameters for the synthetic traffic generator."""

    city: str = "Monterrey, Mexico"
    start: datetime = datetime(2025, 1, 1)
    end: datetime = datetime(2025, 1, 2)
    output_path: Path = Path("monterrey_traffic_estimated.csv.gz")


ROAD_VOLUMES = {
    "motorway": 15_000,
    "primary": 5_000,
    "secondary": 2_000,
    "residential": 200,
}

HOUR_FACTORS = {
    (0, 5): 0.2,
    (6, 8): 1.0,
    (9, 15): 0.5,
    (16, 19): 1.0,
    (20, 23): 0.3,
}


def _hour_factor(hour: int) -> float:
    return next(value for window, value in HOUR_FACTORS.items() if window[0] <= hour <= window[1])


def _prepare_edges(city: str) -> pd.DataFrame:
    LOGGER.info("Downloading street network for %s", city)
    graph = ox.graph_from_place(city, network_type="drive")
    edges = ox.graph_to_gdfs(graph, nodes=False, edges=True)
    edges = edges[["name", "highway", "length", "lanes"]].fillna("desconocido")
    edges["highway"] = edges["highway"].apply(lambda val: val[0] if isinstance(val, list) else val)
    return edges.reset_index(drop=True)


def generate_traffic_dataset(config: TrafficConfig = TrafficConfig()) -> Path:
    """Generate a synthetic hourly traffic dataset based on OSM road segments."""

    edges = _prepare_edges(config.city)
    hours = pd.date_range(config.start, config.end, freq="h", inclusive="left")

    LOGGER.info(
        "Generating synthetic traffic for %s hours (%s to %s)",
        len(hours),
        config.start,
        config.end,
    )
    records = []

    for ts in hours:
        factor = _hour_factor(ts.hour)
        jitter = np.random.normal(1.0, 0.1, size=len(edges))
        base = edges["highway"].map(lambda highway: ROAD_VOLUMES.get(highway, 500))
        traffic = np.maximum(0, (base * factor * jitter).astype(int))

        chunk = edges.copy()
        chunk["datetime"] = ts
        chunk["estimated_traffic"] = traffic
        records.append(chunk)

    df = pd.concat(records, ignore_index=True)
    output_path = config.output_path
    df.to_csv(output_path, index=False, compression="gzip")
    LOGGER.info("Traffic dataset saved to %s", output_path)
    return output_path


__all__ = ["TrafficConfig", "generate_traffic_dataset"]
