-- Category Service Schema
CREATE DATABASE IF NOT EXISTS category_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE category_db;

CREATE TABLE IF NOT EXISTS categories (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    icon VARCHAR(50)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Lightweight mirror for product counts.
-- In full microservice mode, replace with HTTP call to Product Service.
CREATE TABLE IF NOT EXISTS products (
    id          VARCHAR(10) PRIMARY KEY,
    name        VARCHAR(200),
    price       DECIMAL(10,2),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
