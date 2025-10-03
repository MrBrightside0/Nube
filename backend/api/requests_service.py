from __future__ import annotations

from typing import Any, Mapping

import requests

from .constants import OPENAQ_KEY


class APIRequestError(RuntimeError):
    """Raised when an external API responds with a non-success status code."""

    def __init__(self, url: str, status_code: int, message: str) -> None:
        super().__init__(f"Request to {url} failed with status {status_code}: {message}")
        self.url = url
        self.status_code = status_code
        self.message = message


def _default_headers(extra: Mapping[str, str] | None = None) -> dict[str, str]:
    headers: dict[str, str] = {"Accept": "application/json"}
    if OPENAQ_KEY:
        headers.setdefault("X-API-Key", OPENAQ_KEY)
    if extra:
        headers.update(extra)
    return headers


def get_request(url: str, params: Mapping[str, Any] | None = None, headers: Mapping[str, str] | None = None) -> Any:
    response = requests.get(url, params=params, headers=_default_headers(headers))
    if response.ok:
        return response.json()
    raise APIRequestError(url, response.status_code, response.text)


def post_request(url: str, data: Any, headers: Mapping[str, str] | None = None) -> Any:
    combined_headers = {"Content-Type": "application/json"}
    if headers:
        combined_headers.update(headers)
    response = requests.post(url, json=data, headers=_default_headers(combined_headers))
    if response.ok:
        if response.text:
            return response.json()
        return None
    raise APIRequestError(url, response.status_code, response.text)
