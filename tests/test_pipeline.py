
from datetime import date
from unittest.mock import Mock, call

import pytest

from ingestion.api_client import OpenMeteoAPIError
from ingestion.config import load_config
from ingestion.pipeline import run_forecast_ingestion, run_historical_ingestion


@pytest.fixture
def config():
    return load_config()


@pytest.fixture
def mock_client():
    client = Mock()

    client.forecast_url = "https://api.open-meteo.com/v1/forecast"
    client.historical_url = "https://archive-api.open-meteo.com/v1/archive"

    mock_response = {
        "hourly": {
            "time": [
                "2026-11-06T00:00",
                "2026-11-06T01:00",
            ]
        }
    }

    client.get_forecast.return_value = mock_response
    client.get_historical.return_value = mock_response

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

def test_all_cities_historical_ingestion_succeed(
    config,
    mock_client,
    mock_storage,
):
    results = run_historical_ingestion(
        config,
        mock_client,
        mock_storage,
        as_of=date(2026, 11, 11),
    )

    assert len(results) == 5
    assert all(result.success for result in results)

    assert mock_client.get_historical.call_count == 5
    assert mock_storage.save_response.call_count == 5

    for api_call in mock_client.get_historical.call_args_list:
        params = api_call.args[0]

        assert params["start_date"] == "2023-11-11"
        assert params["end_date"] == "2026-11-06"
        assert params["timezone"] == "UTC"


def test_historical_ingestion_continues_after_api_failure(
    config,
    mock_client,
    mock_storage,
):
    from ingestion.api_client import OpenMeteoAPIError

    mock_client.get_historical.side_effect = [
        OpenMeteoAPIError("API unavailable"),
        {"hourly": {"time": ["2026-11-06T00:00"]}},
        {"hourly": {"time": ["2026-11-06T00:00"]}},
        {"hourly": {"time": ["2026-11-06T00:00"]}},
        {"hourly": {"time": ["2026-11-06T00:00"]}},
    ]

    results = run_historical_ingestion(
        config,
        mock_client,
        mock_storage,
        as_of=date(2026, 11, 11),
    )

    assert len(results) == 5
    assert sum(result.success for result in results) == 4
    assert sum(not result.success for result in results) == 1

    assert mock_client.get_historical.call_count == 5
    assert mock_storage.save_response.call_count == 4


def test_historical_ingestion_uses_requested_coordinates(
    config,
    mock_client,
    mock_storage,
):
    run_historical_ingestion(
        config,
        mock_client,
        mock_storage,
        as_of=date(2026, 11, 11),
    )

    first_city = config.cities.cities[0]

    first_call = mock_storage.save_response.call_args_list[0]
    assert first_call.kwargs["dataset_type"] == "historical"
    assert first_call.kwargs["city_id"] == first_city.city_id
    assert first_call.kwargs["endpoint"] == mock_client.historical_url
    assert first_call.kwargs["requested_location"] == {
        "latitude": first_city.latitude,
        "longitude": first_city.longitude,
    }


def test_historical_ingestion_propagates_storage_errors(
    config,
    mock_client,
    mock_storage,
):
    mock_storage.save_response.side_effect = OSError("Disk full")

    with pytest.raises(OSError, match="Disk full"):
        run_historical_ingestion(
            config,
            mock_client,
            mock_storage,
            as_of=date(2026, 11, 11),
        )
