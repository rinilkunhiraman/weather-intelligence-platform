
import json

import pytest

from ingestion.bronze import BronzeStorage


@pytest.fixture
def sample_response() -> dict:
    return {
        "latitude": 11.25,
        "longitude": 75.82,
        "timezone": "GMT",
        "hourly_units": {
            "temperature_2m": "°C",
        },
        "hourly": {
            "time": ["2026-11-04T00:00"],
            "temperature_2m": [24.4],
        },
    }


def test_save_forecast_response(tmp_path, sample_response,):
    storage = BronzeStorage(base_dir=tmp_path)

    output_path = storage.save_response(
        dataset_type="forecast",
        city_id="kozhikode_in",
        city_name="Kozhikode",
        endpoint="https://api.open-meteo.com/v1/forecast",
        request_parameters={"forecast_days": 1},
        response=sample_response,
        requested_location={
    "latitude": 11.2588,
    "longitude": 75.7804,
},
    )

    assert output_path.exists()
    assert output_path.suffix == ".json"

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["metadata"]["provider"] == "open_meteo"
    assert payload["metadata"]["dataset_type"] == "forecast"
    assert payload["metadata"]["city_id"] == "kozhikode_in"
    assert payload["metadata"]["city_name"] == "Kozhikode"
    assert payload["metadata"]["requested_location"] == {
    "latitude": 11.2588,
    "longitude": 75.7804,
}
    assert payload["metadata"]["resolved_location"] == {
    "latitude": 11.25,
    "longitude": 75.82,
}
    assert payload["data"] == sample_response


def test_each_ingestion_creates_a_separate_file(tmp_path, sample_response):
    storage = BronzeStorage(base_dir=tmp_path)

    arguments = {
        "dataset_type": "forecast",
        "city_id": "kozhikode_in",
        "city_name": "Kozhikode",
        "endpoint": "https://api.open-meteo.com/v1/forecast",
        "request_parameters": {"forecast_days": 1},
        "response": sample_response,
        "requested_location": {
        "latitude": 11.2588,
        "longitude": 75.7804,
    },
    }

    first_path = storage.save_response(**arguments)
    second_path = storage.save_response(**arguments)

    assert first_path != second_path
    assert first_path.exists()
    assert second_path.exists()


def test_invalid_dataset_type_is_rejected(tmp_path, sample_response):
    storage = BronzeStorage(base_dir=tmp_path)

    with pytest.raises(ValueError, match="dataset_type"):
        storage.save_response(
            dataset_type="current",
            city_id="kozhikode_in",
            city_name="Kozhikode",
            endpoint="https://example.com",
            request_parameters={},
            response=sample_response,
            requested_location={
            "latitude": 11.2588,
            "longitude": 75.7804,
        },
        )
