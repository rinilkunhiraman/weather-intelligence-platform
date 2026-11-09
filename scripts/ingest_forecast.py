
from ingestion.api_client import OpenMeteoClient
from ingestion.bronze import BronzeStorage
from ingestion.config import PROJECT_ROOT, load_config
from ingestion.pipeline import run_forecast_ingestion


def main() -> None:
    config = load_config()

    client = OpenMeteoClient(config.weather.source)

    storage = BronzeStorage(
        base_dir=PROJECT_ROOT / "data" / "bronze"
    )

    try:
        results = run_forecast_ingestion(
            config=config,
            client=client,
            storage=storage,
        )
    finally:
        client.session.close()

    successful = sum(result.success for result in results)
    failed = len(results) - successful

    print("\n" + "=" * 50)
    print("FORECAST INGESTION SUMMARY")
    print("=" * 50)

    for result in results:
        status = "SUCCESS" if result.success else "FAILED"
        print(f"{status}: {result.city_name}")

        if result.output_path:
            print(f"  File: {result.output_path}")

        if result.error:
            print(f"  Error: {result.error}")

    print("\nTotal cities:", len(results))
    print("Successful:", successful)
    print("Failed:", failed)

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
