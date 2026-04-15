#!/bin/bash

# Start containers
docker compose up -d

# Run script
docker exec -it spark-client spark-submit --master spark://spark-master:7077 /opt/spark/work-dir/jobs/test_minio_connectivity.py
