# Weather API Assignment

This project is a FastAPI-based Weather API designed to handle weather and crop yield data. It ingests raw data, calculates statistics, and exposes RESTful endpoints for data access. The application uses PostgreSQL for data storage and supports seamless deployments to platforms like Railway or AWS.

---

## Table of Contents

1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Directory Structure](#directory-structure)
4. [Setup and Installation](#setup-and-installation)
5. [Environment Variables](#environment-variables)
6. [Endpoints](#endpoints)
7. [Deployment](#deployment)
8. [Future Improvements](#future-improvements)

---

## Features

- **Data Ingestion**:
  - Supports uploading raw weather and crop yield data files.
  - Deduplicates data during ingestion.
  - Logs ETL process steps and results.

- **Data Analysis**:
  - Calculates statistics (e.g., average temperatures, total precipitation) from the ingested weather data.
  - Stores results in the database for optimized querying.

- **REST API**:
  - Exposes endpoints for retrieving raw data and calculated statistics.
  - Supports filtering, sorting, and pagination.

- **Swagger/OpenAPI Documentation**:
  - Automatically generated API documentation.

---

## Technologies Used

- **Python** (FastAPI, SQLAlchemy, asyncpg)
- **PostgreSQL**
- **Docker** (for local development and database containerization)
- **Railway** (optional deployment platform)
- **Terraform** (optional AWS deployment)

---

## Directory Structure

```
weather-api-assignment/
├── app/
│   ├── db/                # Database models and connection logic
│   ├── etl/               # ETL logic for weather and crop yield data
│   ├── models/            # Pydantic models for API responses
│   ├── routes/            # API routes (ingestion, weather, stats)
│   ├── utils/             # Utility scripts (e.g., logging)
│   └── main.py            # Entry point for FastAPI app
├── data/                  # Sample data files for ingestion
├── tests/                 # Unit tests for the application
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration for the app
├── docker-compose.yml     # Docker Compose for local development
├── build_zip.sh           # Script to package app for deployment
└── README.md              # Project documentation
```

---

## Setup and Installation

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional for local development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/weather-api-assignment.git
   cd weather-api-assignment
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Start a local PostgreSQL instance or use the Docker Compose file:
     ```bash
     docker-compose up -d
     ```
   - Run database migrations:
     ```bash
     alembic upgrade head
     ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Access the API at:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Environment Variables

The application requires the following environment variables:

```bash
DATABASE_URL=<your_database_url>
MIGRATION_SECRET=<your_migration_secret>
```

These can be configured in your Railway project or `.env` file locally.

---

## Endpoints

### `/api/upload_file`
- **Method**: POST
- **Description**: Upload raw weather or crop yield data files for ingestion.
- **Request Body**: File upload.
- **Response**: Confirmation of ingestion.

### `/api/weather`
- **Method**: GET
- **Description**: Retrieve raw weather data with filtering, sorting, and pagination.
- **Query Parameters**:
  - `station_id` (optional)
  - `start_date` (optional)
  - `end_date` (optional)
  - `limit` (default: 100)
  - `offset` (default: 0)
- **Response**: List of weather data records.

### `/api/weather/stats`
- **Method**: GET
- **Description**: Retrieve aggregated weather statistics.
- **Query Parameters**:
  - `station_id` (optional)
  - `year` (optional)
  - `limit` (default: 100)
  - `offset` (default: 0)
- **Response**: List of weather statistics.

---

## Deployment

### Railway

1. Create a new Railway project and link your repository.
2. Add the PostgreSQL service.
3. Configure environment variables in the Railway dashboard.
4. Deploy the project.

### AWS (Optional)

1. Use the `build_zip.sh` script to package the app for deployment:
   ```bash
   bash build_zip.sh
   ```
2. Deploy the Lambda function and RDS database manually or using Terraform.

---

## Future Improvements

- Add additional unit tests for edge cases.
- Implement a CI/CD pipeline.
- Add support for more data sources.
- Optimize database queries for large datasets.
- Implement better error handling for edge cases.

---

## Contributors

- Gavin Nelson

---

