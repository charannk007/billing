
CREATE DATABASE supermarket_db;
USE supermarket_db;

CREATE TABLE cashiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
ALTER TABLE cashiers ADD phone VARCHAR(15);
ALTER TABLE cashiers ADD name VARCHAR(100);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE stocks (
    id VARCHAR(36) PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    category_id INT,
    barcode VARCHAR(255),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);


CREATE TABLE transactions (
    id VARCHAR(36) PRIMARY KEY,
    cashier_id INT,
    total_amount DECIMAL(10, 2),
    transaction_date DATETIME,
    FOREIGN KEY (cashier_id) REFERENCES cashiers(id)
);
ALTER TABLE transactions ADD COLUMN total DECIMAL(10,2);
ALTER TABLE transactions DROP PRIMARY KEY;
ALTER TABLE transactions MODIFY id INT AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE transactions
ADD COLUMN date DATE,
ADD COLUMN time TIME;




CREATE TABLE transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT,
    item_id VARCHAR(36),
    quantity INT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (item_id) REFERENCES stocks(id)
);

















