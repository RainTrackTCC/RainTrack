CREATE DATABASE dht11_db;
USE dht11_db;

CREATE TABLE dht11_readings(
	id INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT,
    humidity FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(200) NOT NULL UNIQUE,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

INSERT INTO users(nome, email, cpf, senha)
VALUES
("Igor", "igor@gmail.com", "52637383829", "123");

-- SELECT * FROM dht11_readings;
-- SELECT * FROM users;