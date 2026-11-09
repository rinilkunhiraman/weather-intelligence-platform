
from unittest.mock import Mock, call

import pytest

from ingestion.api_client import OpenMeteoAPIError
from ingestion.config import load_config
from ingestion.pipeline import run_forecast_ingestion


@pytest.fixture
def config():
    return load_config()


@pytest.fixture
def mock_client():
    client = Mock()
    client.forecast_url = "https://api.open-meteo.com/v1/forecast"
    client.get_forecast.return_value = {
        "latitude": 11.28,
        "longitude": 75.82,
        "hourly": {
            "time": ["2026-11-04T00:00"],
            "temperature_2m": [24.4],
        },
    }
    return client


@pytest.fixture
def mock_storage():
    return Mock()


def test_all_cities_ingest_successfully(
    config, mock_client, mock_storage
):
    results = run_forecast_ingestion(
        config=config,
        client=mock_client,
        storage=mock_storage,
    )

    assert len(results) == 5
    assert all(result.success for result in results)

    assert mock_client.get_forecast.call_count == 5
    assert mock_storage.save_response.call_count == 5


def test_pipeline_continues_when_one_city_api_request_fails(
    config, mock_client, mock_storage
):
    mock_client.get_forecast.side_effect = [
        OpenMeteoAPIError("API unavailable"),
        {
            "latitude": 12.97,
            "longitude": 77.59,
            "hourly": {"time": ["2026-11-04T00:00"]},
        },
        {
            "latitude": 19.07,
            "longitude": 72.87,
            "hourly": {"time": ["2026-11-04T00:00"]},
        },
        {
            "latitude": 51.50,
            "longitude": -0.12,
            "hourly": {"time": ["2026-11-04T00:00"]},
        },
        {
            "latitude": 40.71,
            "longitude": -74.00,
            "hourly": {"time": ["2026-11-04T00:00"]},
        },
    ]

    results = run_forecast_ingestion(
        config=config,
        client=mock_client,
        storage=mock_storage,
    )

    assert len(results) == 5
    assert results[0].success is False
    assert results[0].error == "API unavailable"

    assert all(result.success for result in results[1:])

    assert mock_client.get_forecast.call_count == 5
    assert mock_storage.save_response.call_count == 4


def test_requested_coordinates_are_passed_to_storage(
    config, mock_client, mock_storage
):
    run_forecast_ingestion(
        config=config,
        client=mock_client,
        storage=mock_storage,
    )

    first_city = config.cities.cities[0]

    first_call = mock_storage.save_response.call_args_list[0]

    assert first_call == call(
        dataset_type="forecast",
        city_id=first_city.city_id,
        city_name=first_city.name,
        endpoint=mock_client.forecast_url,
        request_parameters=first_call.kwargs["request_parameters"],
        response=mock_client.get_forecast.return_value,
        requested_location={
            "latitude": first_city.latitude,
            "longitude": first_city.longitude,
        },
    )


def test_unexpected_storage_error_propagates(
    config, mock_client, mock_storage
):
    mock_storage.save_response.side_effect = OSError(
        "Disk write failed"
    )

    with pytest.raises(OSError, match="Disk write failed"):
        run_forecast_ingestion(
            config=config,
            client=mock_client,
            storage=mock_storage,
        )
