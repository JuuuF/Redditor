-- Create DB Schema
CREATE SCHEMA redditor;

-- Grant users all privileges
GRANT ALL PRIVILEGES ON SCHEMA redditor TO redditor_db_user;

-- Point roles to correct schemas
ALTER ROLE redditor_db_user SET search_path TO redditor;
