# emprego.co.mz ETL Pipeline

An automated end-to-end ETL pipeline that scrapes job listings from emprego.co.mz, transforms and cleans the data, and loads it to an AWS S3 bucket. The pipeline runs daily via GitHub Actions and is fully containerized with Docker.

---

## Architecture

```
emprego.co.mz  →  Scrape  →  Transform  →  Load to S3 Bucket
                  
Orchestrated by GitHub Actions
Containerized with Docker
Tested with Pytest
```

---

## Pipeline Stages

**1. Scrape**
Fetches job listings from emprego.co.mz with pagination support. Detects and stops when the site loops back to page 1. Deduplicates by job URL and saves the raw data as a timestamped Parquet file.

**2. Transform**
Reads the most recent raw Parquet file, handles null values, removes duplicate rows, and standardizes all text fields to lowercase. Saves the cleaned data to the processed layer.

**3. Load**
Uploads the most recent processed Parquet file to an AWS S3 bucket under the `processed/` prefix.

---

## Project Structure

```
emprego.co.mz_ETL_Pipeline/
├── pipeline/
│   ├── scraper.py          
│   ├── transform.py        
│   └── storage.py          
├── tests/
│   ├── __init__.py
│   ├── conftest.py         
│   └── unit_tests.py       
├── data/
│   ├── raw/                
│   └── processed/          
├── .github/
│   └── workflows/
│       └── pipeline.yml    
├── .env.example           
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── main.py             
├── requirements.txt
└── README.md
```

---

## Data Schema

| Column   | Description                              |
|----------|------------------------------------------|
| titulo   | Full job listing title                   |
| link     | URL to the job posting                   |
| role     | Job role extracted from the listing      |
| empresa  | Company name                             |
| location | City or region extracted from the title  |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- AWS account with an S3 bucket and IAM credentials

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
AWS_REGION=your_region
AWS_BUCKET_NAME=your_bucket_name
```

### Run Locally

```bash
pip install -r requirements.txt
python main.py
```

### Run with Docker

```bash
docker-compose up --build
```

---

## Testing

```bash
pytest tests/unit_tests.py -v
```

Three unit tests cover the scraper parsing logic and the S3 storage connection guard.

---

## Automation

The pipeline is scheduled to run daily at 06:00 UTC via GitHub Actions. AWS credentials are stored as GitHub Secrets and Variables. To trigger a manual run, go to **Actions → ETL Pipeline Diário → Run workflow**.

---

## Hire Me

If you need a custom data pipeline, web scraper, or ETL solution, I am available for freelance work:

- [Fiverr](https://www.fiverr.com/s/P2zEpZP)
- [Upwork](https://www.upwork.com/services/product/development-it-a-custom-etl-data-pipeline-to-automate-your-data-integration-workflows-2057619530106098904?ref=project_share)
- [Contra](https://contra.com/thiyane_xavier_jk3d916z?referralExperimentNid=DEFAULT_REFERRAL_PROGRAM&referrerUsername=thiyane_xavier_jk3d916z)

---

## Tech Stack

| Tool            | Purpose                        |
|-----------------|--------------------------------|
| Python          | Core language                  |
| BeautifulSoup4  | HTML parsing                   |
| Pandas          | Data transformation            |
| Parquet         | Storage format                 |
| boto3           | AWS S3 integration             |
| Docker          | Containerization               |
| GitHub Actions  | Scheduling and orchestration   |
| Pytest          | Unit testing                   |