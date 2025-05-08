create database dht11_db;
use dht11_db;

create table dht11_readings(
	id INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT,
    humidity FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from dht11_readings;