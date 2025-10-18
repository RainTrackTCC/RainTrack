CREATE DATABASE rainTrack;
USE rainTrack;

CREATE TABLE users (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role TINYINT(1) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);

CREATE TABLE stations (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    latitude VARCHAR(255) NOT NULL,
    longitude VARCHAR(255) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uuid VARCHAR(17) NOT NULL UNIQUE,
    cdUser INT NULL,
    FOREIGN KEY (cdUser) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE typeParameters (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    typeJson VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    unit VARCHAR(255) NOT NULL,
    numberOfDecimalPlaces INT NOT NULL
);

CREATE TABLE parameters (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    cdTypeParameter INT NOT NULL,
    cdStation INT,
    FOREIGN KEY (cdTypeParameter) REFERENCES typeParameters(id) ON DELETE CASCADE,
    FOREIGN KEY (cdStation) REFERENCES stations(id) ON DELETE CASCADE
);


CREATE TABLE measures (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    value FLOAT NOT NULL,
    cdParameter INT NOT NULL,
    measureTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cdParameter) REFERENCES parameters(id) ON DELETE CASCADE
);

DELIMITER $$
CREATE TRIGGER delete_typeparameters
BEFORE DELETE ON typeParameters
FOR EACH ROW
BEGIN
    DELETE measures 
    FROM measures
    INNER JOIN parameters ON measures.cdParameter = parameters.id
    WHERE parameters.cdTypeParameter = OLD.id;

    DELETE FROM parameters
    WHERE cdTypeParameter = OLD.id;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER Delete_stations
BEFORE DELETE ON stations
FOR EACH ROW
BEGIN    

    DELETE
    FROM measures
    WHERE cdParameter IN (SELECT id FROM parameters WHERE cdStation = OLD.id);
    
	DELETE
    FROM parameters
    WHERE cdStation = OLD.id;
    
END$$
DELIMITER ;

INSERT INTO users (name, cpf, email, password, role) 
VALUES
('Admin', '00000000000', 'raintrack@gmail.com', '$2b$12$jxaB3glGF8oJVYZDNPLj0OekBOq3DpRCIeQCms38e1I.1NeCjWv7S', 1);