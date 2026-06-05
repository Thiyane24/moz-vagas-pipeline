
# Multi-Source ETL Data Pipeline (Mozambique Job Market)
An automated, scalable end-to-end ETL pipeline that aggregates real-time job market data from multiple Mozambican platforms, standardizes the information, and loads it into an AWS S3 Data Lake.

## Architecture
```
[Web Sources] → Scrape (Parallel) → Transform (Unified) → Load to S3 (Gold Layer)
                  
Orchestrated by GitHub Actions
Containerized with Docker
Tested with Pytest

```
## Pipeline Stages
**1. Scrape (Bronze Layer)**
Simultaneously fetches job listings from multiple sources (e.g., emprego.co.mz, MMO Vagas, VagasMoz). Handles pagination, deduplication, and stores raw data as timestamped Parquet files for full traceability.
**2. Transform (Silver Layer)**
Consolidates diverse source schemas into a unified dataset. Performs data cleaning, handles nulls, removes duplicates, and standardizes formats (lowercase, date normalization) to ensure high data quality.
**3. Load (Gold Layer)**
Uploads the cleaned, analytics-ready data to the AWS S3 Data Lake, structured with **Hive-style partitioning** (year=YYYY/month=MM/day=DD/) for efficient querying via Amazon Athena.

## Project Structure
```
Multi_Source_ETL_Pipeline/
├── pipeline/
│   ├── scrapers/           # Individual source scrapers
│   ├── transform.py        # Schema unification & cleaning
│   └── storage.py          # S3 connection & partitioning logic
├── tests/                  # Unit tests for parsing & storage
├── data/                   # Local raw & processed staging
├── .github/workflows/      # CI/CD and Daily automation
├── Dockerfile              # Container definition
├── docker-compose.yml      # Orchestration
└── main.py                 # Pipeline entry point

```
## Tech Stack
| Tool | Purpose |
|---|---|
| **Python** | Core logic & automation |
| **Pandas** | Unified data transformation |
| **Parquet** | Storage (Schema-safe & compressed) |
| **boto3** | AWS S3 connectivity |
| **Docker** | Environment consistency |
| **GitHub Actions** | Orchestration & Scheduling |


## How to Run
### Run with Docker (Recommended)
Ensures all dependencies and the environment are identical to production:
```bash
# Build and run the entire multi-source pipeline
docker-compose up --build --force-recreate

```
### Automation
The pipeline is scheduled to run daily via **GitHub Actions**. It automatically detects new job listings, processes them, and archives them in the S3 Data Lake, keeping your insights always up-to-date without manual intervention.

## Hire Me
I specialize in building resilient data systems, custom scrapers, and automated ETL pipelines. If you have a data integration challenge, let's talk:
 * Fiverr
 * Upwork
 * Contra