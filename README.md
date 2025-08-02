# User Guide

## 1. Register for an Account
1. Visit the **Register** page.
2. Fill in:
   - Your name
   - Email address
   - A password
3. Click **Register** to create your account.
4. You’ll be redirected to the login page.

## 2. Log In
1. Go to the **Login** page (you should be taken there automatically after registering).
2. Enter your registered email and password.
3. After successful login, you’ll be redirected to the **Products** page.

## 3. Browse Products
1. On the **Products** page, you’ll see a list of all available grocery items.
2. Each product shows:
   - Name
   - Description
   - Price
3. Click **Add to Cart** to add items.

## 4. View Cart
1. Click **Cart** from the navigation bar.
2. You will see:
   - All items in your cart
   - Quantity per item
   - Subtotal for each item
   - Total and tax calculated
3. Click **Checkout** to proceed.

## 5. Checkout and Pseudo Payment
1. When ready, click **Checkout** in the cart.
2. You will be redirected to the **Payment** page.
3. Select a payment method and click **Confirm Payment**.
4. You’ll be redirected to the **Order History** page.

## 6. Order History
1. View your past orders in **Orders**.
2. Each order displays:
   - Order ID
   - Date
   - Total
   - List of purchased items and their prices

## 7. Account Info
1. Click **Account** in the navigation bar.
2. View your:
   - Name
   - Email
3. Click **Delete Account** to remove your account and all data.

## 8. Log Out
- Click **Logout** in the top-right corner of the navigation bar.

---

## MySQL Setup

Go to `db_config.py` and change the password (and any other connection settings) under the `# connection` comment if needed.

Then run the following SQL commands:

```sql
CREATE DATABASE grocery_portal;
USE grocery_portal;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    price DECIMAL(6, 2),
    stock INT
);

INSERT INTO products (name, description, price, stock) VALUES
('Milk', '1 gallon whole milk', 3.49, 25),
('Bread', 'Wheat sandwich loaf', 2.99, 15),
('Eggs', 'Dozen large eggs', 2.79, 30),
('Apples', 'Fresh red apples (3 lb bag)', 4.50, 20),
('Chicken Breast', 'Boneless skinless (1 lb)', 5.99, 10);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    total DECIMAL(8, 2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    price DECIMAL(6, 2)
);
