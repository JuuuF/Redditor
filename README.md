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

#### Web Services

| Container Address | Container Port | Host Address   | Port | Description |
|-------------------|----------------|----------------|------|-------------|
| 172.18.0.2        | 9000           | localhost      | 9000 | API         |
| 172.18.0.2        | 9001           | localhost      | 9001 | WebUI       |

Login credentials:

- **User**: minioadmin
- **Password**: minioadmin

#### File Storage

File storage is handled using a bind volume for the docker container:\
`./data/minio/:/mnt/data/`
