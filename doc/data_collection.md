# Data Collection

This file contains information on how the data is collected.

## The Collection Service

- Docker container: Python image
- Running python script upon startup
- Dependant on:
  - now: no other containers
  - later: data lake

## Connectivity

- needs web access for connecting to KVG API
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

- access/refresh period
- authentication parameters
- storage location
  - local: file path
  - another service: URI

## Script Contents

- parse arguments
- setup API communication
  - authenticate beforehand?
  - need to check how KVG API works / if any setup is necessary
- periodically fetch retrieve data from API
  - don't always retrieve all data
  - only call for data that can change
- store results
- repeat
