# Redditor

A Reddit Data Collector for Trend examination.

This project is a means for me in order to get into data engineering and learn about this job's nooks and crannies. The goal of this project is not to create something ground breaking, but for me to learn as much as possible.

## Quick Start

The system is based upon Docker. To start the system, run:

```bash
docker compose up -d
```

## Setup

This section contains information on how each system is setup and how these systems communicate with one another.

### MinIO

The MinIO setup is determined by its config file under `setup/minio/config.env`.

#### MinIO Web Services

| Container Address | Container Port | Host Address   | Port | Description |
|-------------------|----------------|----------------|------|-------------|
| 172.18.0.2        | 9000           | localhost      | 9000 | API         |
| 172.18.0.2        | 9001           | localhost      | 9001 | WebUI       |

Login credentials:

- **User**: minioadmin
- **Password**: minioadmin

#### MinIO File Storage

File storage is handled using a bind volume for the docker container:\
`./data/minio/:/mnt/data/`

### PostgreSQL

The PostgreSQL setup is determined by its config file at `setup/postgres/config.env` as well as `conpose.yaml`.

#### Postgres Associated Containers

| Service Name | Function      |
|--------------|---------------|
| postgres     | DB hosting    |
| adminer      | DB monitoring |

#### Adminer Credentials

| Login information | Value             | Description                         |
|-------------------|-------------------|-------------------------------------|
| System            | PostgreSQL        |                                     |
| Server            | postgres          | = service name in `compose.yaml`    |
| Username          | postgres_user     | = POSTGRES_USER in `config.env`     |
| Password          | postgres_password | = POSTGERS_PASSWORD in `config.env` |
| Database          | redditor_db       | = POSTGERS_DB in `config.env`       |

#### PostgreSQL File Storage

File storage is handled using a bind volume for the docker container:\
`./data/postgres/:/var/lib/postgresql/data/`

### Apache Spark

The Spark containers are determined fully by `compose.yaml`:

#### Spark Associated Containers

| Service Name     | Function               |
|------------------|------------------------|
| spark-master     | Spark Master Container |
| spark-worker-[x] | Spark Worker with ID x |

#### Spark Web Services

| Container Address           | Container Port | Host Address | Host Port | Description |
|-----------------------------|----------------|--------------|-----------|-------------|
| 172.18.0.3 (spark-master)   | 7077           | localhost    | 7077      | API?        |
| 172.18.0.3 (spark-master)   | 8080           | localhost    | 9090      | Spark WebUI |
| 172.18.0.6 (spark-worker-1) |                |              |           |             |
