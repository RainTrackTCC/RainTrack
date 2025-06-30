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
    cdParameter INT
);

CREATE TABLE typeParameters (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    typeJson VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    unit VARCHAR(255) NOT NULL,
    numberOfDecimalPlaces INT NOT NULL,
    cdParameter INT
);

CREATE TABLE parameters (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    cdTypeParameter INT NOT NULL,
    cdStation INT NOT NULL,
    FOREIGN KEY (cdTypeParameter) REFERENCES typeParameters(id),
    FOREIGN KEY (cdStation) REFERENCES stations(id)
);

ALTER TABLE stations
ADD CONSTRAINT fk_station_parameter
FOREIGN KEY (cdParameter) REFERENCES parameters(id);

ALTER TABLE typeParameters
ADD CONSTRAINT fk_typeparameter_parameter
FOREIGN KEY (cdParameter) REFERENCES parameters(id);

CREATE TABLE measures (
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    value FLOAT NOT NULL,
    cdParameter INT NOT NULL,
    measureTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cdParameter) REFERENCES parameters(id)
);

INSERT INTO users (name, cpf, email, password, role) 
VALUES
('Admin', '00000000000', 'raintrack@gmail.com', '123', 1);

SELECT * FROM users;