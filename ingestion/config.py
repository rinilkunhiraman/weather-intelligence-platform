
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_DIR = PROJECT_ROOT / "config"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CityConfig(StrictModel):
    city_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    country: str = Field(min_length=1)
    country_code: str = Field(min_length=2, max_length=2)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str

    @model_validator(mode="after")
    def validate_timezone(self):
        try:
            ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"Invalid timezone: {self.timezone}") from exc
        return self


class CitiesConfig(StrictModel):
    cities: list[CityConfig] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_city_ids(self):
        city_ids = [city.city_id for city in self.cities]

        if len(city_ids) != len(set(city_ids)):
            raise ValueError("City IDs must be unique")

        return self


class RequestConfig(StrictModel):
    timezone: str
    temperature_unit: str
    wind_speed_unit: str
    precipitation_unit: str


class EndpointsConfig(StrictModel):
    historical: HttpUrl
    forecast: HttpUrl


class SourceConfig(StrictModel):
    provider: str
    endpoints: EndpointsConfig
    request: RequestConfig


class HistoricalConfig(StrictModel):
    lookback_years: int = Field(gt=0)
    refresh_frequency: str
    end_date_lag_days: int = Field(ge=0)
    hourly_variables: list[str] = Field(min_length=1)


class ForecastConfig(StrictModel):
    horizon_days: int = Field(gt=0)
    refresh_frequency: str
    hourly_variables: list[str] = Field(min_length=1)


class BronzeStorageConfig(StrictModel):
    format: str
    preserve_original_response: bool
    include_request_metadata: bool


class LayerStorageConfig(StrictModel):
    format: str
    timestamp_timezone: str


class StorageConfig(StrictModel):
    bronze: BronzeStorageConfig
    silver: LayerStorageConfig
    gold: LayerStorageConfig



class NumericRangeConfig(StrictModel):
    min: float
    max: float | None = None

    @model_validator(mode="after")
    def validate_range(self):
        if self.max is not None and self.min >= self.max:
            raise ValueError("Minimum must be less than maximum")
        return self


class DataQualityConfig(StrictModel):
    reject_invalid_coordinates: bool
    reject_duplicate_records: bool
    validate_required_fields: bool
    validate_timestamps: bool
    temperature_c: NumericRangeConfig
    relative_humidity_pct: NumericRangeConfig
    precipitation_mm: NumericRangeConfig
    wind_speed_kmh: NumericRangeConfig



class WeatherProjectConfig(StrictModel):
    name: str
    version: str


class WeatherConfig(StrictModel):
    project: WeatherProjectConfig
    source: SourceConfig
    historical: HistoricalConfig
    forecast: ForecastConfig
    storage: StorageConfig
    data_quality: DataQualityConfig


class AppConfig(BaseModel):
    cities: CitiesConfig
    weather: WeatherConfig


def _load_yaml(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    if not isinstance(content, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")

    return content


def load_config(config_dir: Path | None = None) -> AppConfig:
    """Load and validate application configuration from YAML files."""
    directory = config_dir or DEFAULT_CONFIG_DIR

    cities_data = _load_yaml(directory / "cities.yaml")
    weather_data = _load_yaml(directory / "weather.yaml")

    return AppConfig(
        cities=CitiesConfig.model_validate(cities_data),
        weather=WeatherConfig.model_validate(weather_data),
    )
