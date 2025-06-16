CREATE DATABASE supermarket_db;
USE supermarket_db;

CREATE TABLE cashiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    phone VARCHAR(15),
    name VARCHAR(100)
);


CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE stocks (
    id VARCHAR(36) PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    category_id INT,
    barcode VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cashier_id INT,
    total_amount DECIMAL(10, 2),
    transaction_date DATETIME,
    total DECIMAL(10, 2),
    date DATE,
    time TIME,
    FOREIGN KEY (cashier_id) REFERENCES cashiers(id)
);

CREATE TABLE transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    item_id VARCHAR(36),
    quantity INT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (item_id) REFERENCES stocks(id)
);
