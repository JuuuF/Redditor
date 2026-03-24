# Data Collection

This file contains information on how the data is collected.

## The Collection Service

- Docker container: Python image
- Running python script upon startup
- Dependant on:
  - now: no other containers
  - later: data lake

## Connectivity

- needs web access for connecting to reddit API
- needs to be able to talk to other services
  - infrastructure already setup by docker network

## Parametrization

- script has to accept arguments
- 2 ways:
  - pass arguments by command line
  - pass arguments by environment variables
- command line approach
  - arguments can be passed through compose.yaml
  - how do they get there?
  - environment variables? -> then we are at second possibility already
- environment variables
  - .env file for necessary variables
  - passed to docker service
  - read through `os.environ(...)`

### Variables

- which subreddits to access
  - limit to reddit?
  - maybe specify API and request body?
  - more modular and probably easier to adapt to other APIs
  - in case of expansion to other websites, we can launch another instance of the service with another API specified
- access/refresh period
- authentication parameters
- storage location
  - local: file path
  - another service: URI

## Script Contents

- parse arguments
- setup API communication
  - connect to reddit API?
  - authenticate beforehand?
  - need to check how reddit API works / if any setup is necessary
- periodically fetch retrieve data from API
  - don't always retrieve all data
  - only call for data that can change
- store results
- repeat
