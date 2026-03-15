# Setup

This file contains information on how each system is setup and how these systems communicate with one another.

## MinIO

The MinIO setup is determined by its config file under [`setup/minio/config.env`](../setup/minio/config.env).

### MinIO Web Services

| Container Address | Container Port | Host Address   | Host Port | Description   |
|-------------------|----------------|----------------|-----------|---------------|
| minio             | 9000           | localhost      | 9000      | API           |
| minio             | 9001           | localhost      | 9001      | WebUI         |
| adminer           | 8080           | localhost      | 8080      | Adminer WebUI |

Login credentials:

- **User**: minioadmin
- **Password**: minioadmin

### MinIO File Storage

File storage is handled using a volume for the docker container with `data/minio/:/mnt/data/`.

## PostgreSQL

There are multiple PostgreSQL services running, hosting multiple DBs. Aditionally, there's an Adminer service for DB monitoring.

### Airflow DB

- Service Name: `db-airflow`
- Active Ports: `5432`

Specified by:

| File                                                                                  | Function              |
|---------------------------------------------------------------------------------------|-----------------------|
| [`compose.yaml`](../compose.yaml)                                                     | Service definition    |
| [`setup/airflow/db/config_airflow_db.env`](../setup/airflow/db/config_airflow_db.env) | Environment variables |
| [`setup/airflow/db/init_airflow.sql`](../setup/airflow/db/init_airflow.sql)           | Initial DB setup      |

#### Airflow DB Variables

```conf
POSTGRES_DB="airflow_db"
POSTGRES_USER="airflow_db_user"
POSTGRES_PASSWORD="airflow_db_password"
```

#### Airflow DB File Storage

File storage is handled using a Docker Volume:

| Host                      | Service                    |
|---------------------------|----------------------------|
| `data/airflow/airflow_db` | `/var/lib/postgresql/data` |

### Redditor DB

- Service Name: `db-redditor`
- Active Ports: `5432`

Specified by:

| File                                                                                      | Function              |
|-------------------------------------------------------------------------------------------|-----------------------|
| [`compose.yaml`](../compose.yaml)                                                         | Service definition    |
| [`setup/redditor_db/config_redditor_db.env`](../setup/redditor_db/config_redditor_db.env) | Environment variables |
| [`setup/redditor_db/init_redditor.sql`](../setup/redditor_db/init_redditor.sql)           | Initial DB setup      |

#### Redditor DB Variables

```conf
POSTGRES_DB="redditor_db"
POSTGRES_USER="redditor_db_user"
POSTGRES_PASSWORD="redditor_db_password"
```

#### Redditor DB File Storage

File storage is handled using a Docker Volume:

| Host               | Service                    |
|--------------------|----------------------------|
| `data/redditor_db` | `/var/lib/postgresql/data` |

### Superset DB

- Service Name: `db-superset`
- Active Ports: `5432`

Specified by:

| File                                                                                      | Function              |
|-------------------------------------------------------------------------------------------|-----------------------|
| [`compose.yaml`](../compose.yaml)                                                         | Service definition    |
| [`setup/superset/db/config_superset_db.env`](../setup/superset/db/config_superset_db.env) | Environment variables |
| [`setup/superset/db/init_superset.sql`](../setup/superset/db/init_superset.sql)           | Initial DB setup      |

#### Superset DB Credentials

```conf
POSTGRES_DB="superset_db"
SUPERSET_DB_USER_USERNAME="superset_db_user"
SUPERSET_DB_USER_PASSWORD="superset_db_password"
```

#### Superset DB File Storage

File storage is handled using a Docker Volume:

| Host                        | Service                    |
|-----------------------------|----------------------------|
| `data/superset/superset_db` | `/var/lib/postgresql/data` |

### Adminer

- Service Name: `adminer-db-manager`
- Active Ports: `8080:8080`

Specified by:

| File                              | Function           |
|-----------------------------------|--------------------|
| [`compose.yaml`](../compose.yaml) | Service definition |

#### Adminer Credentials

On `localhost:8080`, you can log into a DB using:

| Login information | Value               | Example              |
|-------------------|---------------------|----------------------|
| System            | PostgreSQL          |                      |
| Server            | \<DB Service Name\> | db-redditor          |
| Username          | \<DB Username\>     | redditor_db_user     |
| Password          | \<DB Password\>     | redditor_db_password |
| Database          | \<DB Name\>         | redditor_db          |

## Apache Spark

The Spark containers are determined fully by [`compose.yaml`](../compose.yaml).

### Spark Associated Services

| Service Name     | Function               |
|------------------|------------------------|
| spark-master     | Spark Master Container |
| spark-worker-[x] | Spark Worker with ID x |

### Spark Web Services

| Container Address | Container Port | Host Address | Host Port | Description |
|-------------------|----------------|--------------|-----------|-------------|
| spark-master      | 7077           | localhost    | 7077      | Master API  |
| spark-master      | 8080           | localhost    | 9090      | Spark WebUI |
| spark-worker-1    |                |              | 8081      | Worker UI   |

## Apache Airflow

Apache Airflow is used to control the execution process. You can specify tasks in a specific order using a DAG. These tasks may be arbitrary operations that may depend on one another. Airflow's scheduling and executing system makes sure all tasks are executed correctly and efficiently. At least that's the hope for now.

Airflow configuration files:

- [`setup/airflow/config_common.env`](../setup/airflow/config_common.env): Environment variables
- [`setup/airflow/init.sh`](../setup/airflow/init.sh): Initialization script run by init container

### Airflow Associated Services

| Service Name         | Function                                 | Open Ports | Port Function              |
|----------------------|------------------------------------------|------------|----------------------------|
| airfolw-init         | Initialize Airflow settings upon startup |            |                            |
| airflow-apiserver    | Airflow communication                    | 8082:8080  | Execution API + Airflow UI |
| airflow-scheduler    | Airflow Scheduler instance               |            |                            |
| airflow-broker-redis | Celery Broker instance                   | 6379       | API                        |

The Airflow UI can be accessed at `localhost:8082`.

Logging in can be done using Airflow DB credentials:

```conf
AIRFLOW_API_USER_USERNAME='airflow_db_user'
AIRFLOW_API_USER_PASSWORD='airflow_db_password'
AIRFLOW_API_USER_ROLE='Admin'
AIRFLOW_API_USER_FIRSTNAME='Admin'
AIRFLOW_API_USER_LASTNAME='User'
AIRFLOW_API_USER_EMAIL='admin@example.org'
```

## Apache Superset

Apache Superset is used to gain insights into the data. At least it needs access to the database. At the moment, only the UI loads and I am not fully certain at which point in the project I will get to using this system. But it was on the roadmap, which was enough reason for me to get it up and running. I will hopefully add more information about this system once I know more about it.

### Superset Associated Services

| Service Name  | Function            |
|---------------|---------------------|
| superset-init | Initialize Superset |
| superset      | Run Superset        |

Superset is configured using:

- [`setup/superset/config.env`](../setup/superset/config.env): Environment Variables
- [`setup/superset/init.sh`](../setup/superset/init.sh): Init script run by superset-init
- [`setup/superset/superset_config.py`](../setup/superset/superset_config.py): Python script for further configuration

### Superset Environment Variables

```conf
SUPERSET_ADMIN_USERNAME="admin"
SUPERSET_ADMIN_FIRSTNAME="Admin"
SUPERSET_ADMIN_LASTNAME="User"
SUPERSET_ADMIN_EMAIL="admin@example.org"
SUPERSET_ADMIN_PASSWORD="superset_password"

SUPERSET_DB_USER_USERNAME="superset_db_user"
SUPERSET_DB_USER_PASSWORD="superset_db_password"
```

### Superset Networking

The Superset UI is hosted at `localhost:8088`, which connects to `superset:8088` within the docker network. Use the admin login info as stated in [environment variables](#superset-environment-variables).
