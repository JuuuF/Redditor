# Redditor Roadmap

This project follows a more or less strict roadmap. Since I am new to pretty much everything this project encompasses, I cannot determine whether this roadmap holds up during the project's lifetime nor am I even able to come up with such a roadmap in the first place. Hence, this roadmap was AI generated in order to give me something to orient myself to.

## Week 1 - Infrastructure Foundation

### Goal

Build the base data platform environment.

### Tasks

Set up services using Docker:

- MinIO (data lake storage)
- PostGreSQL (warehouse)
- Spark (processing)
- Airflow (pipeline scheduler)
- Superset (BI)

### Techniques to Learn

- Docker Compose multi-service environments
- Service networking
- Environment variables
- Data persistence with volumes

### Checklist

Infrastructure is ready when:

- [ ] `docker compose up` starts all services
- [X] MinIO dashboard is accessible
- [X] PostgreSQL accepts connections
- [X] Spark container starts successfully
- [X] Airflow UI loads
- [ ] Superset UI loads
- [ ] All services can communicate via Docker network
