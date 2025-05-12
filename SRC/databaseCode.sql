CREATE DATABASE dht11_db;
USE dht11_db;

CREATE TABLE dht11_readings(
	id INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT,
    humidity FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM dht11_readings;