
from pathlib import Path

import pytest
from pydantic import ValidationError

from ingestion.config import (
    CitiesConfig,
    CityConfig,
    load_config,
)


def test_load_config_successfully():
    config = load_config()

    assert len(config.cities.cities) == 5
    assert config.weather.historical.lookback_years == 3
    assert config.weather.forecast.horizon_days == 7


def test_duplicate_city_ids_are_rejected():
    city = CityConfig(
        city_id="kozhikode_in",
        name="Kozhikode",
        country="India",
        country_code="IN",
        latitude=11.2588,
        longitude=75.7804,
        timezone="Asia/Kolkata",
    )

    with pytest.raises(ValidationError):
        CitiesConfig(cities=[city, city])


def test_invalid_latitude_is_rejected():
    with pytest.raises(ValidationError):
        CityConfig(
            city_id="invalid_city",
            name="Invalid City",
            country="India",
            country_code="IN",
            latitude=100,
            longitude=75.7804,
            timezone="Asia/Kolkata",
        )


def test_invalid_timezone_is_rejected():
    with pytest.raises(ValidationError):
        CityConfig(
            city_id="invalid_city",
            name="Invalid City",
            country="India",
            country_code="IN",
            latitude=11.2588,
            longitude=75.7804,
            timezone="Invalid/Timezone",
        )


def test_missing_configuration_file_is_rejected(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_config(config_dir=tmp_path)
