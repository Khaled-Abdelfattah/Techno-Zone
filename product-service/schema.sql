-- Product Service Schema
CREATE DATABASE IF NOT EXISTS product_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE product_db;

CREATE TABLE IF NOT EXISTS categories (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS products (
    id          VARCHAR(10)    PRIMARY KEY,
    name        VARCHAR(200)   NOT NULL,
    price       DECIMAL(10,2)  NOT NULL,
    category_id INT,
    image       VARCHAR(255),
    rating      INT  DEFAULT 0,
    badge       VARCHAR(50),
    stock       INT  DEFAULT 0,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
