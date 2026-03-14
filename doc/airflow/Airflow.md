# Airflow

Airflow handles and schedules tasks. I'm not yet sure which tasks exactly, but I hope we'll get into this a bit later.

## Quick overview

Quick overview of the Airflow components:

1. DAG
    - defines dependencies of tasks
2. Airflow Scheduler
    - **schedules tasks**
3. Celery Broker
    - e.g. Redis -> **task queue**
    - checks for ready tasks and marks them as ready to run
4. Airflow Workers
    - **execute tasks**
5. Result Backend
    - e.g. Postgres -> **metadata database**
    - collects results

### The DAGs

The tasks to be executed are listed in form of DAGs. These show dependencies across the data's transformations (we just assume there's data involved at this point):

```plaintext
A -> B -> D
A -> C -> D
```

These are stored in a database, like PostgreSQL.

### The Scheduler

The scheduler takes the DAGs and turns them into *Task Instances*. They get ordered in a way that respects their dependencies:

1. A[run1] (no dependencies)
2. B[run1] (depends on A)
3. C[run1] (depends on A)
4. D[run1] (depends on B and C)

In this example, B and C could be switched since they both depend on A.

The scheduler keeps an overview on the task states. In the beginning, all tasks are initialized as state **NONE**.

To begin execution, the scheduler marks tasks without dependencies (i.e. the root nodes of the DAG) as **SCHEDULED**.

### The Broker

The broker's responsibility is to check for tasks tagged as *scheduled*. It pushes their information into the broker queue.

Example message sent to the broker queue:

```python
execute_task(
    dag_id="example_pipeline",
    task_id="A",
    run_id="run1"
)
```

### The Workers

Workers poll the broker queue if they are not busy. Once they receive a task, they execute it and update the task's state in the database to **RUNNING**. Once successfully executed, its status is changed to **SUCCESS**, **FAILED**, **UP_FOR_RETRY** or **SKIPPED**.

```python
while True:
    task = queue.get()
    result = run(task)
    db.update(task, result)
```

### The Return of the Scheduler

Once tasks are marked with *success*, the scheduler re-evalutates the dependencies and marks tasks that are now runnable as *scheduled*. From this point on, the broker takes action again and the cycle continues until all tasks are executed.

### Task states

Possible task states are:

| State            | Description                                                              |
|------------------|--------------------------------------------------------------------------|
| NONE             | Task is not yet ready to be executed, i.e. dependencies are not yet done |
| SCHEDULED        | Task is ready to be executed                                             |
| RUNNING / QUEUED | Task is currently in execution                                           |
| SUCCESS          | Task has been successfully executed                                      |
| FAILED           | Task has failed to execute                                               |
| UP_FOR_RETRY     | Task failed, but execution can be repeated                               |
| SKIPPED          | Task execution has been skipped                                          |

## Working Diagram

```plaintext
    ┌─────────────┐
    │  Scheduler  │         -> decides what to do
    └──────┬──────┘
           │
           │ uses
           ▼
    ┌─────────────┐
    │   Executor  │         -> decides how to run it
    │ (Celery)    │
    └──────┬──────┘
           │
           │ sends tasks
           ▼
    ┌─────────────┐
    │ Message     │         -> queues jobs
    │ Broker      │
    │ (Redis)     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │ Workers     │         -> do the work
    │ run tasks   │
    └──────┬──────┘
           │ 
           │ update DB entries (success / failed)
           ▼
    ┌─────────────┐
    |  Scheduler  |
    └─────────────┘
```

## Minimal Airflow Setup

A minimal Airflow setup consists of:

- Scheduler
  - triggering scheduled tasks
  - submitting tasks to executor
- (Executor)
  - runs on the scheduler instance
- DAG processor
  - parse the DAG files
  - serialize them into metadata database
- Webserver
  - UI for inspection, triggering and debugging
- Folder for DAG files
- Metadata DB
  - usually PostgreSQL / MySQL
  - storing task states, DAGs and variables

## Airflow Tasks

What Airflow actually does in this system:

1. Download API data
2. Store data in MinIO
3. Clean data
4. Store clean data in Postgres
