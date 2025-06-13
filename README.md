# Charan Super Market

A Python-based web application for supermarket management built with Flask, MySQL, and Tailwind CSS.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt


Configure MySQL:

Update config/config.py with your MySQL credentials.
Run schema.sql in MySQL to create the supermarket_db database and tables.


Run the Application:
python app.py


Access the app at http://localhost:5000.



Features
Admin

Login with credentials (default: admin/admin123).
Create, reset, or remove cashier accounts.
Manage categories (e.g., Cosmetics).
Add stocks with item name, price, quantity, category, and auto-generated barcode.
View and filter stocks by category.
Receive notifications for items with quantity < 100.
View daily transaction details (items sold, cashier performance, filter by amount).
Generate monthly reports (total amount, transaction count, cashiers).

Cashier

Login with credentials set by admin.
Search items by name.
Scan barcodes to add items to billing.
Manage billing: add/remove items, view total.
Complete billing and print bills with transaction ID, timestamp, items, total, and store branding.
Start new billing after completion.

Directory Structure
supermarket_app/
├── app.py
├── schema.sql
├── requirements.txt
├── static/
│   ├── barcodes/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── scripts.js
├── templates/
│   ├── index.html
│   ├── admin_login.html
│   ├── cashier_login.html
│   ├── admin_dashboard.html
│   ├── create_cashier.html
│   ├── reset_cashier_password.html
│   ├── create_category.html
│   ├── add_stock.html
│   ├── check_stocks.html
│   ├── notifications.html
│   ├── transactions.html
│   ├── monthly_report.html
│   ├── cashier_dashboard.html
│   ├── new_billing.html
│   └── print_bill.html
├── config/
│   └── config.py
├── utils/
│   └── barcode_generator.py
├── tests/
│   └── test_app.py
└── README.md

Notes

Security: Replace default admin credentials and use password hashing (e.g., bcrypt) for production.
UI/UX: Tailwind CSS ensures a modern, responsive design. Customize styles.css for branding.
Deployment: Use Gunicorn/Nginx for production and secure MySQL connections.
Testing: Expand test_app.py to cover more functionality.



