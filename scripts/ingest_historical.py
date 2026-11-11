
from ingestion.api_client import OpenMeteoClient
from ingestion.bronze import BronzeStorage
from ingestion.config import PROJECT_ROOT, load_config
from ingestion.pipeline import run_historical_ingestion


def main() -> None:
    """Run historical weather ingestion for all configured cities."""

    config = load_config()

    client = OpenMeteoClient(config.weather.source)
    storage = BronzeStorage(
    base_dir=PROJECT_ROOT / "data" / "bronze"
)

    try:
        results = run_historical_ingestion(
            config=config,
            client=client,
            storage=storage,
        )
    finally:
        client.session.close()

    successful = sum(result.success for result in results)
    failed = len(results) - successful

    print("\nHistorical ingestion summary")
    print("----------------------------")
    print(f"Total cities: {len(results)}")
    print(f"Successful:   {successful}")
    print(f"Failed:       {failed}")

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
