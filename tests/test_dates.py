
from datetime import date

import pytest

from ingestion.dates import (
    calculate_historical_date_range,
    subtract_years,
)


def test_calculate_historical_date_range() -> None:
    start, end = calculate_historical_date_range(
        lookback_years=3,
        end_date_lag_days=5,
        as_of=date(2026, 11, 11),
    )

    assert start == date(2023, 11, 11)
    assert end == date(2026, 11, 6)


def test_subtract_years_handles_leap_day() -> None:
    result = subtract_years(
        reference_date=date(2024, 2, 29),
        years=1,
    )

    assert result == date(2023, 2, 28)


def test_calculate_historical_date_range_handles_leap_year() -> None:
    start, end = calculate_historical_date_range(
        lookback_years=1,
        end_date_lag_days=0,
        as_of=date(2024, 2, 29),
    )

    assert start == date(2023, 2, 28)
    assert end == date(2024, 2, 29)


def test_rejects_zero_lookback_years() -> None:
    with pytest.raises(ValueError, match="lookback_years"):
        calculate_historical_date_range(
            lookback_years=0,
            end_date_lag_days=5,
            as_of=date(2026, 11, 11),
        )


def test_rejects_negative_end_date_lag() -> None:
    with pytest.raises(ValueError, match="end_date_lag_days"):
        calculate_historical_date_range(
            lookback_years=3,
            end_date_lag_days=-1,
            as_of=date(2026, 11, 11),
        )


def test_rejects_invalid_date_range() -> None:
    with pytest.raises(ValueError, match="start date"):
        calculate_historical_date_range(
            lookback_years=1,
            end_date_lag_days=400,
            as_of=date(2026, 11, 11),
        )
