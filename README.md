# Weather Intelligence Platform

An end-to-end data engineering project that collects, stores, transforms, and analyses weather data across multiple cities using modern data engineering tools.

The project is being developed incrementally, starting with a reliable Python-based ingestion pipeline and evolving into a complete analytical data platform.

## Project Overview

The platform collects historical weather observations and forecast snapshots from [Open-Meteo](https://open-meteo.com/), initially covering five cities across India, Europe, and North America.

The long-term objective is to build a reproducible data pipeline with layered storage, data quality checks, analytical transformations, orchestration, and visualisation.

### Cities

| City | Country |
|---|---|
| Kozhikode | India |
| Bengaluru | India |
| Mumbai | India |
| London | United Kingdom |
| New York | United States |

## Architecture

The target architecture follows a medallion-style data model:

```text
                 Open-Meteo API
                        |
                        v
                Python Ingestion
                        |
                        v
                  Bronze Layer
                  Raw JSON Data
                        |
                        v
                  Silver Layer
             Cleaned and Standardised
                  Parquet Data
                        |
                        v
                   Gold Layer
               Analytical Datasets
                        |
                        v
              PostgreSQL / Analytics
                        |
                        v
                    Metabase

          Apache Airflow: Orchestration
          dbt Core: Data Transformations
```

*Note: The architecture represents the intended end state. Implementation is ongoing.*

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | API integration and ingestion |
| Open-Meteo | Weather data source |
| Pydantic | Configuration validation |
| Requests | HTTP client and retry handling |
| YAML | Externalised project configuration |
| JSON | Raw Bronze storage |
| Parquet | Planned Silver and Gold storage |
| PostgreSQL | Planned analytical database |
| Apache Airflow | Planned workflow orchestration |
| dbt Core | Planned data transformations |
| Metabase | Planned analytics and dashboards |
| Docker Compose | Planned local infrastructure |

## Current Implementation

### Completed

- [x] Configurable city definitions using YAML
- [x] Weather source and ingestion configuration
- [x] Pydantic configuration validation
- [x] Open-Meteo HTTP client
- [x] Request timeouts and retry handling
- [x] Raw API response persistence in the Bronze layer
- [x] Ingestion metadata, including timestamps and requested/resolved coordinates
- [x] Seven-day hourly forecast ingestion for five cities
- [x] Per-city failure handling
- [x] Automated unit and pipeline tests

### Current ingestion results

The live forecast pipeline has successfully retrieved:

- 5 cities
- 168 hourly forecast records per city
- 840 hourly records in total
- 11 forecast variables per city

All raw responses are stored separately to preserve forecast snapshots.

### In Progress / Planned

- [ ] Three-year historical weather ingestion
- [ ] Silver-layer normalisation and Parquet storage
- [ ] Data quality validation
- [ ] PostgreSQL integration
- [ ] Gold-layer analytical models
- [ ] dbt transformations and tests
- [ ] Apache Airflow orchestration
- [ ] Metabase dashboards
- [ ] Forecast accuracy evaluation

## Repository Structure

```text
weather-intelligence-platform/
├── airflow/
│   └── dags/
├── config/
│   ├── cities.yaml
│   └── weather.yaml
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── dbt/
├── docker/
├── docs/
├── ingestion/
│   ├── api_client.py
│   ├── bronze.py
│   ├── config.py
│   └── pipeline.py
├── scripts/
│   └── ingest_forecast.py
├── tests/
│   ├── test_api_client.py
│   ├── test_bronze.py
│   ├── test_config.py
│   └── test_pipeline.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12 or later
- Git
- Internet access to reach the Open-Meteo API

### 1. Clone the repository

```bash
git clone https://github.com/rinilkunhiraman/weather-intelligence-platform.git
cd weather-intelligence-platform
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the project

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 4. Run the tests

```bash
python -m pytest -v
```

### 5. Run code quality checks

```bash
ruff check .
```

### 6. Run forecast ingestion

```bash
python -m scripts.ingest_forecast
```

The pipeline retrieves hourly forecasts for all configured cities and stores the raw API responses in the local Bronze data directory.

## Configuration

Project settings are maintained in:

- `config/cities.yaml` — city identifiers, coordinates, countries, and time zones.
- `config/weather.yaml` — API endpoints, weather variables, forecast horizon, storage formats, and data quality settings.

The current forecast pipeline uses the free Open-Meteo API endpoint and does not require an API key.

## Data Storage Strategy

The platform uses a layered storage approach.

**Bronze**
- Original API responses in JSON format.
- Ingestion timestamps and request metadata.
- Requested and API-resolved coordinates.
- Separate snapshots for each forecast ingestion.

**Silver**
- Planned standardised and validated weather records.
- UTC timestamps and Parquet storage.

**Gold**
- Planned daily aggregates, monthly trends, city comparisons, and forecast evaluation datasets.

Generated weather data is excluded from Git to keep the repository focused on source code and reproducible project configuration.

## Testing

The project uses:

- **pytest** for automated testing.
- **Ruff** for linting and code quality.

The current test suite covers configuration validation, API client behaviour, Bronze storage, and ingestion pipeline orchestration.

## Data Source and Attribution

Weather data is provided by [Open-Meteo](https://open-meteo.com/).

Refer to the provider's [documentation](https://open-meteo.com/en/docs) and [terms](https://open-meteo.com/en/terms) for API usage, attribution, and licensing requirements.

## Project Status

This is an actively developed portfolio project focused on practical data engineering principles, including reproducible ingestion, data quality, layered storage, orchestration, and analytical modelling.

Implementation status will be updated as each milestone is completed.

---

**Built as a hands-on data engineering project.**
