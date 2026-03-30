# Kiel-o-Meter Roadmap

This project follows a more or less strict roadmap. Since I am new to pretty much everything this project encompasses, I cannot determine whether this roadmap holds up during the project's lifetime nor am I even able to come up with such a roadmap in the first place. Hence, this roadmap was AI generated in order to give me something to orient myself to.

## Week 1 - Infrastructure Foundation

### W1 Goal

Build the base data platform environment.

### W1 Tasks

Set up services using Docker:

- MinIO (data lake storage)
- PostGreSQL (warehouse)
- Spark (processing)
- Airflow (pipeline scheduler)
- Superset (BI)

### W1 Techniques to Learn

- Docker Compose multi-service environments
- Service networking
- Environment variables
- Data persistence with volumes

### W1 Checklist

Infrastructure is ready when:

- [X] `docker compose up` starts all services
- [X] MinIO dashboard is accessible
- [X] PostgreSQL accepts connections
- [X] Spark container starts successfully
- [X] Airflow UI loads
- [X] Superset UI loads
- [X] All services can communicate via Docker network

## Week 2 - KVG Data Ingrestion

### W2 Goal

Build your first data ingestion pipeline.

Write a Python service that collects KVG data.

### W2 Tasks

- Learn KVG endpoints
- Fetch live tracking data
- Store raw results locally

### W2 Techniques to Learn

- REST APIs
- HTTP requests
- JSON data parsing
- API rate limiting

Libraries you may use:

- requests
- json

### W2 Checklist

Your collector works when:

- [ ] API authentication works -> There's no API in this case
- [X] You can fetch data from multiple bus stops
- [X] Each data includes metadata (arrive times, departure times etc.)
- [X] The script runs repeatedly without crashing
- [X] Results are saved locally as JSON

## Week 3 - Data Lake Design

### W3 Goal

Create the raw data lake.

Instead of JSON files, data is stored as Parquet datasets in MinIO.

### W3 Tasks

- Convert JSON → Parquet
- Upload Parquet files to MinIO
- Create partition structure

Example structure:

```plaintext
data_lake/
   raw/
      kiel-o-meter/
         year=2026/
            month=03/
               day=15/
                  posts.parquet
```

### W3 Techniques to Learn

- Columnar storage
- Parquet format
- Data partitioning
- Object storage
- S3 APIs

Libraries:

- pyarrow
- boto3
- s3fs

### W3 Checklist

Your data lake works when:

- [ ] KVG data is stored in Parquet format
- [ ] Files are partitioned by date
- [ ] Data uploads successfully to MinIO
- [ ] Data can be downloaded again
- [ ] Schema remains consistent across files
