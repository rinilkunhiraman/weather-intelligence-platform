import calendar
from datetime import UTC, date, datetime, timedelta


def subtract_years(reference_date: date, years: int) -> date:
    """Subtract calendar years while handling leap days."""

    target_year = reference_date.year - years

    last_day_of_month = calendar.monthrange(
        target_year,
        reference_date.month,
    )[1]

    target_day = min(reference_date.day, last_day_of_month)

    return date(
        target_year,
        reference_date.month,
        target_day,
    )


def calculate_historical_date_range(
    *,
    lookback_years: int,
    end_date_lag_days: int,
    as_of: date | None = None,
) -> tuple[date, date]:
    """Calculate the inclusive historical data date range."""

    if lookback_years <= 0:
        raise ValueError("lookback_years must be greater than zero.")

    if end_date_lag_days < 0:
        raise ValueError("end_date_lag_days cannot be negative.")

    reference_date = as_of or datetime.now(UTC).date()

    start_date = subtract_years(reference_date, lookback_years)

    end_date = reference_date - timedelta(
        days=end_date_lag_days
    )

    if start_date > end_date:
        raise ValueError(
            "Historical start date cannot be after end date."
        )

    return start_date, end_date
