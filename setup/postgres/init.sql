-- Create DB Schemas
CREATE SCHEMA redditor;
CREATE SCHEMA airflow;
CREATE SCHEMA superset;

-- Create Users
CREATE USER airflow_user WITH PASSWORD 'airflow_password';
CREATE USER superset_user WITH PASSWORD 'superset_password';

-- Grant users all privileges
GRANT ALL PRIVILEGES ON SCHEMA airflow TO airflow_user;
GRANT ALL PRIVILEGES ON SCHEMA superset TO superset_user;
