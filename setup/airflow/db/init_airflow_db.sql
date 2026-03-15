-- Create DB Schema
CREATE SCHEMA airflow;

-- Grant users all privileges
GRANT ALL PRIVILEGES ON SCHEMA airflow TO airflow_db_user;

-- Point roles to correct schemas
ALTER ROLE airflow_db_user SET search_path TO airflow;
