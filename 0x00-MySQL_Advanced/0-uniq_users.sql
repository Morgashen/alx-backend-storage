-- Task: Create a 'users' table with id, email, and name fields
-- Description: This script creates a 'users' table if it doesn't exist,
-- with an auto-incrementing id, a unique email, and a name field.

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `name` VARCHAR(255)
);
