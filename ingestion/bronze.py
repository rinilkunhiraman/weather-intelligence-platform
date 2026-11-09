
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class BronzeStorage:
    """Persist raw API responses with ingestion metadata."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def save_response(
    self,
    *,
    dataset_type: str,
    city_id: str,
    city_name: str,
    endpoint: str,
    request_parameters: dict[str, Any],
    response: dict[str, Any],
    requested_location: dict[str, float],
    ) -> Path:
        """Save a raw API response and return its file path."""

        if dataset_type not in {"historical", "forecast"}:
            raise ValueError(
                "dataset_type must be 'historical' or 'forecast'."
            )

        ingested_at = datetime.now(UTC)
        ingestion_date = ingested_at.strftime("%Y-%m-%d")
        ingestion_id = uuid4().hex

        output_dir = (
            self.base_dir
            / "provider=open_meteo"
            / f"dataset_type={dataset_type}"
            / f"city_id={city_id}"
            / f"ingestion_date={ingestion_date}"
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{ingestion_id}.json"

        payload = {
            "metadata": {
                "provider": "open_meteo",
                "dataset_type": dataset_type,
                "city_id": city_id,
                "city_name": city_name,
                "ingested_at": ingested_at.isoformat(),
                "endpoint": endpoint,
                "request_parameters": request_parameters,
                "requested_location": requested_location,
                "resolved_location": {
                  "latitude": response["latitude"],
                  "longitude": response["longitude"],
             },
            },
            "data": response,
        }

        # Write to a temporary file first, then atomically replace.
        temporary_path = output_path.with_suffix(".tmp")

        try:
            with temporary_path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2, ensure_ascii=False)

            temporary_path.replace(output_path)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise

        return output_path
