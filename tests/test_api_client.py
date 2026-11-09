
from unittest.mock import Mock

import pytest
import requests

from ingestion.api_client import OpenMeteoAPIError, OpenMeteoClient
from ingestion.config import load_config


@pytest.fixture
def client():
    config = load_config()
    session = Mock(spec=requests.Session)

    return OpenMeteoClient(
        source_config=config.weather.source,
        session=session,
    )


def test_historical_request_success(client):
    expected_data = {"hourly": {"temperature_2m": [28.5]}}

    response = Mock()
    response.json.return_value = expected_data
    client.session.get.return_value = response

    params = {"latitude": 11.2588, "longitude": 75.7804}

    result = client.get_historical(params)

    assert result == expected_data

    client.session.get.assert_called_once_with(
        client.historical_url,
        params=params,
        timeout=(10, 30),
    )


def test_forecast_request_success(client):
    expected_data = {"hourly": {"temperature_2m": [29.0]}}

    response = Mock()
    response.json.return_value = expected_data
    client.session.get.return_value = response

    params = {"latitude": 12.9716, "longitude": 77.5946}

    result = client.get_forecast(params)

    assert result == expected_data

    client.session.get.assert_called_once_with(
        client.forecast_url,
        params=params,
        timeout=(10, 30),
    )


def test_http_error_is_handled(client):
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError(
        "503 Service Unavailable"
    )

    client.session.get.return_value = response

    with pytest.raises(OpenMeteoAPIError, match="request failed"):
        client.get_forecast({"latitude": 11.2588, "longitude": 75.7804})


def test_invalid_json_is_handled(client):
    response = Mock()
    response.json.side_effect = ValueError("Invalid JSON")

    client.session.get.return_value = response

    with pytest.raises(OpenMeteoAPIError, match="invalid JSON"):
        client.get_historical({"latitude": 11.2588, "longitude": 75.7804})


def test_non_object_json_is_rejected(client):
    response = Mock()
    response.json.return_value = [1, 2, 3]

    client.session.get.return_value = response

    with pytest.raises(OpenMeteoAPIError, match="Expected a JSON object"):
        client.get_forecast({"latitude": 11.2588, "longitude": 75.7804})
