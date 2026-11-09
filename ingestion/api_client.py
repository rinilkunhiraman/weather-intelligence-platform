
from collections.abc import Mapping
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ingestion.config import SourceConfig


class OpenMeteoAPIError(Exception):
    """Raised when an Open-Meteo API request fails."""


class OpenMeteoClient:
    """HTTP client for the Open-Meteo historical and forecast APIs."""

    def __init__(
        self,
        source_config: SourceConfig,
        timeout: tuple[float, float] = (10, 30),
        session: requests.Session | None = None,
    ) -> None:
        self.historical_url = str(source_config.endpoints.historical)
        self.forecast_url = str(source_config.endpoints.forecast)
        self.timeout = timeout

        self.session = session or self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        """Create an HTTP session with retry handling."""
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(["GET"]),
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _get(
        self,
        url: str,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Send a GET request and return the parsed JSON response."""
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            payload = response.json()

            if not isinstance(payload, dict):
                raise OpenMeteoAPIError(
                    "Expected a JSON object from Open-Meteo."
                )

            return payload

        except requests.exceptions.RequestException as exc:
            raise OpenMeteoAPIError(
                f"Open-Meteo request failed: {exc}"
            ) from exc

        except ValueError as exc:
            raise OpenMeteoAPIError(
                "Open-Meteo returned invalid JSON."
            ) from exc

    def get_historical(
        self,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Retrieve historical weather data."""
        return self._get(self.historical_url, params)

    def get_forecast(
        self,
        params: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Retrieve forecast weather data."""
        return self._get(self.forecast_url, params)
