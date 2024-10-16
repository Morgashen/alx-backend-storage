-- Script to create a trigger that resets valid_email when email is changed
-- This assumes a table named 'users' with 'email' and 'valid_email' columns

DELIMITER //

CREATE TRIGGER reset_valid_email
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    IF NEW.email <> OLD.email THEN
        SET NEW.valid_email = 0;
    END IF;
END;//

DELIMITER ;
