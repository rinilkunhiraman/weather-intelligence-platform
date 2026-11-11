
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ingestion.api_client import OpenMeteoAPIError, OpenMeteoClient
from ingestion.bronze import BronzeStorage
from ingestion.config import AppConfig
from ingestion.dates import calculate_historical_date_range


@dataclass
class CityIngestionResult:
    """Result of a weather ingestion attempt for one city."""

    city_id: str
    city_name: str
    success: bool
    output_path: Path | None = None
    error: str | None = None


def run_forecast_ingestion(
    config: AppConfig,
    client: OpenMeteoClient,
    storage: BronzeStorage,
) -> list[CityIngestionResult]:
    """Retrieve and persist forecasts for all configured cities."""

    source_config = config.weather.source
    forecast_config = config.weather.forecast

    results: list[CityIngestionResult] = []

    for city in config.cities.cities:
        print(f"\nProcessing {city.name}, {city.country}...")

        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "hourly": ",".join(forecast_config.hourly_variables),
            "timezone": source_config.request.timezone,
            "forecast_days": forecast_config.horizon_days,
            "temperature_unit": source_config.request.temperature_unit,
            "wind_speed_unit": source_config.request.wind_speed_unit,
            "precipitation_unit": source_config.request.precipitation_unit,
        }

        try:
            response = client.get_forecast(params)

            output_path = storage.save_response(
                dataset_type="forecast",
                city_id=city.city_id,
                city_name=city.name,
                endpoint=client.forecast_url,
                request_parameters=params,
                response=response,
                requested_location={
                    "latitude": city.latitude,
                    "longitude": city.longitude,
                },
            )

            result = CityIngestionResult(
                city_id=city.city_id,
                city_name=city.name,
                success=True,
                output_path=output_path,
            )

            print(
                f"SUCCESS: {city.name} "
                f"({len(response['hourly']['time'])} hourly records)"
            )

        except OpenMeteoAPIError as exc:
            result = CityIngestionResult(
                city_id=city.city_id,
                city_name=city.name,
                success=False,
                error=str(exc),
            )

            print(f"FAILED: {city.name} - {exc}")

        results.append(result)

    return results


def run_historical_ingestion(
    config: AppConfig,
    client: OpenMeteoClient,
    storage: BronzeStorage,
    *,
    as_of: date | None = None,
) -> list[CityIngestionResult]:
    """Retrieve and persist historical weather data for all cities."""

    source_config = config.weather.source
    historical_config = config.weather.historical

    start_date, end_date = calculate_historical_date_range(
        lookback_years=historical_config.lookback_years,
        end_date_lag_days=historical_config.end_date_lag_days,
        as_of=as_of,
    )

    print(f"\nHistorical date range: {start_date} to {end_date}")

    results: list[CityIngestionResult] = []

    for city in config.cities.cities:
        print(f"\nProcessing {city.name}, {city.country}...")

        params = {
            "latitude": city.latitude,
            "longitude": city.longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": ",".join(historical_config.hourly_variables),
            "timezone": source_config.request.timezone,
            "temperature_unit": source_config.request.temperature_unit,
            "wind_speed_unit": source_config.request.wind_speed_unit,
            "precipitation_unit": source_config.request.precipitation_unit,
        }

        try:
            response = client.get_historical(params)

            output_path = storage.save_response(
                dataset_type="historical",
                city_id=city.city_id,
                city_name=city.name,
                endpoint=client.historical_url,
                request_parameters=params,
                response=response,
                requested_location={
                    "latitude": city.latitude,
                    "longitude": city.longitude,
                },
            )

            result = CityIngestionResult(
                city_id=city.city_id,
                city_name=city.name,
                success=True,
                output_path=output_path,
            )

            record_count = len(response["hourly"]["time"])

            print(
                f"SUCCESS: {city.name} "
                f"({record_count} hourly records)"
            )

        except OpenMeteoAPIError as exc:
            result = CityIngestionResult(
                city_id=city.city_id,
                city_name=city.name,
                success=False,
                error=str(exc),
            )

            print(f"FAILED: {city.name} - {exc}")

        results.append(result)

    return results
