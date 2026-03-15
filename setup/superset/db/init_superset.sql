-- Create DB Schema
CREATE SCHEMA superset;

-- Grant users all privileges
GRANT ALL PRIVILEGES ON SCHEMA superset TO superset_db_user;

-- Point roles to correct schemas
ALTER ROLE superset_db_user SET search_path TO superset;
