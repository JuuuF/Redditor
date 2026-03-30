-- Create DB Schema
CREATE SCHEMA kvg;

-- Grant users all privileges
GRANT ALL PRIVILEGES ON SCHEMA kvg TO kvg_db_user;

-- Point roles to correct schemas
ALTER ROLE kvg_db_user SET search_path TO kvg;
