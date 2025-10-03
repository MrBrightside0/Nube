from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

import requests
import xml.etree.ElementTree as ET

from .constants import OPENAQ_KEY, SENSORS_DICT
from .requests_service import get_request

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://api.openaq.org/v3"
BUCKET_URL = "https://openaq-data-archive.s3.amazonaws.com"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "ai" / "air_data"


class OpenAQClient:
    """Tiny wrapper around the OpenAQ v3 API."""

    def __init__(self, base_url: str = BASE_URL, api_key: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or OPENAQ_KEY
        if not self.api_key:
            raise ValueError(
                "OPENAQ_KEY environment variable is not set. Provide a valid API key to query OpenAQ."
            )

    def _request(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        url = f"{self.base_url}{path}"
        headers = {"X-API-Key": self.api_key}
        return get_request(url, params=params, headers=headers)

    def get_location(self, location_id: int) -> dict[str, Any]:
        return self._request(f"/locations/{location_id}")

    def list_locations(
        self,
        city: str | None = None,
        country: str | None = "MX",
        parameters: Iterable[str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if city:
            params["city"] = city
        if country:
            params["country"] = country
        if parameters:
            params["parameters[]"] = list(parameters)
        return self._request("/locations", params=params)

    def location_details(self, location_id: int) -> dict[str, Any]:
        return self._request(f"/locations/{location_id}")

    def location_latest(
        self,
        location_id: int,
        parameters: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if parameters:
            params["parameters[]"] = list(parameters)
        return self._request(f"/locations/{location_id}/latest", params=params)

    def measurements(
        self,
        location_id: int,
        parameter: str,
        date_from: datetime | str | None = None,
        date_to: datetime | str | None = None,
        limit: int = 1000,
        page: int = 1,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "location_id": location_id,
            "parameter": parameter,
            "limit": limit,
            "page": page,
        }
        if date_from:
            params["date_from"] = _format_dt(date_from)
        if date_to:
            params["date_to"] = _format_dt(date_to)
        return self._request("/measurements", params=params)


def _format_dt(value: datetime | str) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def list_monterrey_sensors(client: OpenAQClient | None = None) -> dict[str, Any]:
    client = client or OpenAQClient()
    return {
        name: client.get_location(sensor_id)
        for name, sensor_id in SENSORS_DICT.items()
    }


def download_historical_data(
    location: str,
    start_year: int = 2020,
    end_year: int = 2025,
    output_dir: Path | None = None,
) -> None:
    """Stream gzip historical files for a location into ai/air_data/<location>."""

    if location not in SENSORS_DICT:
        raise ValueError(f"Unknown location '{location}'. Available: {list(SENSORS_DICT)}")

    target_dir = (output_dir or DEFAULT_OUTPUT_DIR) / location
    target_dir.mkdir(parents=True, exist_ok=True)

    location_id = SENSORS_DICT[location]

    for year in range(start_year, end_year + 1):
        prefix = f"records/csv.gz/locationid={location_id}/year={year}/"
        url = f"{BUCKET_URL}?list-type=2&prefix={prefix}"
        LOGGER.info("Listing OpenAQ archives for %s %s", location, year)
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        files = [node.find("s3:Key", ns).text for node in root.findall("s3:Contents", ns)]

        for key in files:
            file_url = f"{BUCKET_URL}/{key}"
            filename = target_dir / Path(key).name

            if filename.exists():
                LOGGER.debug("Skipping %s, already exists", filename)
                continue

            LOGGER.info("Downloading %s → %s", file_url, filename)
            with requests.get(file_url, stream=True, timeout=60) as download:
                download.raise_for_status()
                with open(filename, "wb") as fout:
                    for chunk in download.iter_content(chunk_size=8192):
                        fout.write(chunk)


def download_all_sensors_historical_data(
    start_year: int = 2021,
    end_year: int = 2023,
    output_dir: Path | None = None,
) -> None:
    for location in SENSORS_DICT:
        download_historical_data(location, start_year=start_year, end_year=end_year, output_dir=output_dir)


__all__ = [
    "OpenAQClient",
    "list_monterrey_sensors",
    "download_historical_data",
    "download_all_sensors_historical_data",
]
