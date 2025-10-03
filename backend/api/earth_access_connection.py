from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Mapping

import requests

try:
    from .constants import EARTH_ACCESS_KEY
except ImportError:  # pragma: no cover - standalone execution fallback
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parent))
    from constants import EARTH_ACCESS_KEY  # type: ignore

LOGGER = logging.getLogger(__name__)

CMR_GRANULES_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
CMR_COLLECTIONS_URL = "https://cmr.earthdata.nasa.gov/search/collections.json"


class EarthAccessError(RuntimeError):
    """Raised when the NASA CMR API rejects the request."""


class EarthAccessClient:
    """Minimal wrapper around the NASA Earthdata CMR API using an application key."""

    def __init__(self, access_key: str | None = None) -> None:
        token = access_key or EARTH_ACCESS_KEY
        if not token:
            raise ValueError(
                "EARTH_ACCESS_KEY is not set. Provide a valid Earthdata application key in the environment."
            )
        self.session = requests.Session()
        self.session.headers.update({"Authorization": token})

    def _get(self, url: str, params: Mapping[str, Any]) -> dict[str, Any]:
        response = self.session.get(url, params=params, timeout=30)
        if response.ok:
            return response.json()
        raise EarthAccessError(
            f"Earthdata request failed ({response.status_code}): {response.text[:200]}"
        )

    def search_collections(
        self,
        short_name: str | None = None,
        provider: str | None = None,
        keyword: str | None = None,
        page_size: int = 25,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page_size": page_size}
        if short_name:
            params["short_name"] = short_name
        if provider:
            params["provider"] = provider
        if keyword:
            params["keyword"] = keyword
        return self._get(CMR_COLLECTIONS_URL, params=params)

    def search_granules(
        self,
        collection_concept_id: str,
        temporal: str | None = None,
        bounding_box: str | None = None,
        page_size: int = 100,
        page_num: int = 1,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "collection_concept_id": collection_concept_id,
            "page_size": page_size,
            "page_num": page_num,
        }
        if temporal:
            params["temporal"] = temporal
        if bounding_box:
            params["bounding_box"] = bounding_box
        return self._get(CMR_GRANULES_URL, params=params)

    def download_granule(self, url: str, output_path: Path) -> Path:
        LOGGER.info("Downloading granule %s", url)
        with self.session.get(url, stream=True, timeout=60) as response:
            if not response.ok:
                raise EarthAccessError(
                    f"Failed to download granule ({response.status_code}): {response.text[:200]}"
                )
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as fh:
                for chunk in response.iter_content(chunk_size=8192):
                    fh.write(chunk)
        return output_path


__all__ = ["EarthAccessClient", "EarthAccessError"]


if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Earthdata CMR helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collections = subparsers.add_parser("collections", help="Search collections")
    collections.add_argument("--short-name")
    collections.add_argument("--provider")
    collections.add_argument("--keyword")
    collections.add_argument("--page-size", type=int, default=10)

    granules = subparsers.add_parser("granules", help="Search granules")
    granules.add_argument("collection_concept_id")
    granules.add_argument("--temporal")
    granules.add_argument("--bounding-box")
    granules.add_argument("--page-size", type=int, default=10)
    granules.add_argument("--page", type=int, default=1)

    download = subparsers.add_parser("download", help="Download a granule")
    download.add_argument("url", help="Direct HTTPS URL to the granule file")
    download.add_argument("output", type=Path, help="Where to save the file")

    args = parser.parse_args()

    try:
        client = EarthAccessClient()
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "collections":
            data = client.search_collections(
                short_name=args.short_name,
                provider=args.provider,
                keyword=args.keyword,
                page_size=args.page_size,
            )
            print(json.dumps(data, indent=2))
        elif args.command == "granules":
            data = client.search_granules(
                collection_concept_id=args.collection_concept_id,
                temporal=args.temporal,
                bounding_box=args.bounding_box,
                page_size=args.page_size,
                page_num=args.page,
            )
            print(json.dumps(data, indent=2))
        elif args.command == "download":
            output = client.download_granule(args.url, args.output)
            print(f"[INFO] Granule saved to {output}")
    except EarthAccessError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
