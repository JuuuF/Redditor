# Networking Information

The system communicates over a Docker Network. In it, the services use a multitude of addresses and ports. For the sake of documentation, this document keeps track of which service occupies which port.

| Host IP   | Host Port | Service        | Local IP             | Local Port | Description                |
|-----------|-----------|----------------|----------------------|------------|----------------------------|
|           |           | Redis          | airflow-broker-redis | 6379       | Redis broker communication |
|           |           |                |                      |            |                            |
|           |           | PostgreSQL     | postgres             | 5432       | DB communication           |
|           |           |                |                      |            |                            |
| localhost | 8080      | Adminer        | adminer_db_manager   | 8080       | Adminer WebUI              |
|           |           |                |                      |            |                            |
| localhost | 9000      | MinIO          | minio                | 9000       | MinIO API                  |
| localhost | 9001      | MinIO          | minio                | 9001       | MinIO Web UI               |
|           |           |                |                      |            |                            |
| localhost | 8082      | Airflow-API    | airflow-apiserver    | 8080       | Airflow API                |
|           |           |                |                      |            |                            |
| localhost | 7077      | Spark-Master   | spark-master         | 7077       | API                        |
| localhost | 9090      | Spark-Master   | spark-master         | 8080       | MasterUI                   |
| localhost | 8888      | Spark-Notebook | spark-notebook       | 8888       | Spark Notebook             |
|           |           |                |                      |            |                            |
|           |           | Spark-Worker   | spark-worker-x       | 8081       | WorkerUI                   |
|           |           |                |                      |            |                            |
| localhost | 8088      | Superset       | superset             | 8088       | Superset UI                |
