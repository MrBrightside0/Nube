from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable, Mapping

import requests

from .constants import OPENWEATHER_KEY, WEATHER_STATIONS_DICT

LOGGER = logging.getLogger(__name__)

METEOSTAT_URL = "https://data.meteostat.net/hourly/{year}/{station}.csv.gz"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "ai" / "weather_data"


class OneCallNotAvailableError(RuntimeError):
    """Raised when the One Call 3.0 endpoint cannot be used (e.g., missing subscription)."""


class OpenWeatherClient:
    """Wrapper around the OpenWeather endpoints used in the project."""

    ONE_CALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
    CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or OPENWEATHER_KEY
        if not self.api_key:
            raise ValueError("OPENWEATHER_KEY environment variable is not set.")

    def _base_params(self, lat: float, lon: float, units: str = "metric", lang: str = "es") -> dict[str, Any]:
        return {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": units,
            "lang": lang,
        }

    def one_call(
        self,
        lat: float,
        lon: float,
        *,
        exclude: Iterable[str] | None = None,
        units: str = "metric",
        lang: str = "es",
    ) -> Mapping[str, Any]:
        params = self._base_params(lat, lon, units=units, lang=lang)
        if exclude:
            params["exclude"] = ",".join(exclude)

        response = requests.get(self.ONE_CALL_URL, params=params, timeout=30)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:  # pragma: no cover - network error path
            if response.status_code == 401:
                raise OneCallNotAvailableError(
                    "One Call 3.0 rejected the request. Verify your subscription or use fallback endpoints."
                ) from exc
            raise
        return response.json()

    def current_weather(
        self,
        lat: float,
        lon: float,
        *,
        units: str = "metric",
        lang: str = "es",
    ) -> Mapping[str, Any]:
        params = self._base_params(lat, lon, units=units, lang=lang)
        response = requests.get(self.CURRENT_WEATHER_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()


def download_meteostat_hourly(
    start_year: int,
    end_year: int,
    output_dir: Path | None = None,
    station_ids: Iterable[str] | None = None,
) -> None:
    """Download Meteostat hourly CSV.gz files for the configured stations."""

    base_dir = output_dir or DEFAULT_OUTPUT_DIR
    base_dir.mkdir(parents=True, exist_ok=True)

    stations = list(station_ids or WEATHER_STATIONS_DICT.keys())

    for year in range(start_year, end_year + 1):
        for station_id in stations:
            url = METEOSTAT_URL.format(year=year, station=station_id)
            filename = base_dir / f"{station_id}_{year}.csv.gz"

            if filename.exists():
                LOGGER.debug("Skipping Meteostat %s (already exists)", filename)
                continue

            try:
                LOGGER.info("Downloading Meteostat %s → %s", url, filename)
                with requests.get(url, stream=True, timeout=60) as resp:
                    resp.raise_for_status()
                    with open(filename, "wb") as fh:
                        for chunk in resp.iter_content(chunk_size=8192):
                            fh.write(chunk)
            except requests.RequestException as exc:
                LOGGER.warning("Error downloading station=%s year=%s: %s", station_id, year, exc)


__all__ = ["OpenWeatherClient", "OneCallNotAvailableError", "download_meteostat_hourly"]
