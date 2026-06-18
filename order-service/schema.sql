-- Order Service Schema
CREATE DATABASE IF NOT EXISTS order_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE order_db;

CREATE TABLE IF NOT EXISTS orders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT            NOT NULL,
    coupon_code VARCHAR(50),
    subtotal    DECIMAL(10,2)  NOT NULL,
    discount    DECIMAL(10,2)  DEFAULT 0.00,
    total       DECIMAL(10,2)  NOT NULL,
    status      VARCHAR(20)    DEFAULT 'pending',
    created_at  DATETIME       DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS order_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT            NOT NULL,
    product_id VARCHAR(10)    NOT NULL,
    name       VARCHAR(200)   NOT NULL,
    image      VARCHAR(255),
    qty        INT            NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2)  NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
