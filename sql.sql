-- Buat database
CREATE DATABASE mqtt_sensor;

-- Gunakan database
USE mqtt_sensor;

-- Buat tabel untuk menyimpan data sensor
CREATE TABLE sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    pressure FLOAT NOT NULL,
    altitude FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp)
);

-- Cek tabel
DESCRIBE sensor_data;~