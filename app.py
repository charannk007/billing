from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mysqldb import MySQL
from config import Config
from utils.barcode_generator import generate_barcode
from datetime import datetime
import uuid
import os
from flask import request, redirect, flash, render_template
from flask import Flask
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for





app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)
app.secret_key = '872956aa6e95015744dd90e57ced02a4c947a86b0e507f95aa36c4d62cc44b66' 


# Ensure barcodes directory exists
if not os.path.exists('static/barcodes'):
    os.makedirs('static/barcodes')

# Routes
@app.route('/')
def index():
    if 'user' in session:
        if session['user'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['user'] == 'cashier':
            return redirect(url_for('cashier_dashboard'))
    return render_template('index.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':  # Replace with secure auth
            session['user'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('admin_login.html')


@app.route('/cashier_login', methods=['GET', 'POST'])
def cashier_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM cashiers WHERE username = %s", (username,))
        cashier = cur.fetchone()
        cur.close()

        if cashier and check_password_hash(cashier[2], password):  # cashier[2] = password hash
            session['user'] = 'cashier'
            session['cashier_id'] = cashier[0]
            session['cashier_name'] = cashier[1]
            return redirect(url_for('cashier_dashboard'))
        else:
            flash('Invalid credentials')

    return render_template('cashier_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' in session and session['user'] == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM stocks WHERE quantity < 100")
        low_stock_count = cur.fetchone()[0]
        cur.close()
        return render_template('admin_dashboard.html', low_stock_count=low_stock_count)
    return redirect(url_for('index'))

@app.route('/create_cashier', methods=['GET', 'POST'])
def create_cashier():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']  # ✅ Get phone
        hashed_pw = generate_password_hash(password)
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO cashiers (username, password, phone) VALUES (%s, %s, %s)", (username, hashed_pw, phone))
        mysql.connection.commit()
        cursor.close()
        flash("Cashier created successfully!")
        return redirect(url_for('create_cashier'))
    return render_template('create_cashier.html')


@app.route('/reset_cashier_password', methods=['GET', 'POST'])
def reset_cashier_password():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            cashier_id = request.form['cashier_id']
            new_password = request.form['new_password']
            hashed_pw = generate_password_hash(new_password)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE cashiers SET password = %s WHERE id = %s", (hashed_pw, cashier_id))
            mysql.connection.commit()
            cur.close()
            flash('Password reset successfully')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, phone FROM cashiers")
        cashiers = cur.fetchall()
        cur.close()
        return render_template('reset_cashier_password.html', cashiers=cashiers)
    return redirect(url_for('admin_login'))



@app.route('/remove_cashier', methods=['POST'])
def remove_cashier():
    if 'user' in session and session['user'] == 'admin':
        cashier_id = request.form['cashier_id']
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM cashiers WHERE id = %s", (cashier_id,))
        mysql.connection.commit()
        cur.close()
        flash('Cashier removed successfully')
        return redirect(url_for('reset_cashier_password'))
    return redirect(url_for('admin_login'))

@app.route('/create_category', methods=['GET', 'POST'])
def create_category():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            category_name = request.form['category_name']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
            mysql.connection.commit()
            cur.close()
            flash('Category created successfully')
        return render_template('create_category.html')
    return redirect(url_for('admin_login'))

@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            item_name = request.form['item_name']
            price = request.form['price']
            quantity = request.form['quantity']
            category_id = request.form['category_id']
            item_id = str(uuid.uuid4())
            barcode_path = generate_barcode(item_id)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO stocks (id, item_name, price, quantity, category_id, barcode) VALUES (%s, %s, %s, %s, %s, %s)",
                        (item_id, item_name, price, quantity, category_id, barcode_path))
            mysql.connection.commit()
            cur.close()
            flash('Stock added successfully')
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name FROM categories")
        categories = cur.fetchall()
        cur.close()
        return render_template('add_stock.html', categories=categories)
    return redirect(url_for('admin_login'))

@app.route('/check_stocks')
def check_stocks():
    if 'user' in session and session['user'] == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("SELECT s.id, s.item_name, s.price, s.quantity, c.name, s.barcode FROM stocks s JOIN categories c ON s.category_id = c.id")
        stocks = cur.fetchall()
        cur.execute("SELECT id, name FROM categories")
        categories = cur.fetchall()
        cur.close()
        return render_template('check_stocks.html', stocks=stocks, categories=categories)
    return redirect(url_for('admin_login'))

@app.route('/filter_stocks', methods=['POST'])
def filter_stocks():
    if 'user' in session and session['user'] == 'admin':
        category_id = request.form['category_id']
        cur = mysql.connection.cursor()
        if category_id:
            cur.execute("SELECT s.id, s.item_name, s.price, s.quantity, c.name, s.barcode FROM stocks s JOIN categories c ON s.category_id = c.id WHERE s.category_id = %s", (category_id,))
        else:
            cur.execute("SELECT s.id, s.item_name, s.price, s.quantity, c.name, s.barcode FROM stocks s JOIN categories c ON s.category_id = c.id")
        stocks = cur.fetchall()
        cur.close()
        return jsonify(stocks=stocks)
    return redirect(url_for('admin_login'))

@app.route('/notifications')
def notifications():
    if 'user' in session and session['user'] == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("SELECT s.item_name, s.quantity, c.name FROM stocks s JOIN categories c ON s.category_id = c.id WHERE s.quantity < 100")
        low_stocks = cur.fetchall()
        cur.close()
        return render_template('notifications.html', low_stocks=low_stocks)
    return redirect(url_for('admin_login'))

@app.route('/transactions')
def transactions():
    if 'user' in session and session['user'] == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.id, t.date, t.time, t.total, c.username, GROUP_CONCAT(s.item_name) as items 
            FROM transactions t 
            JOIN cashiers c ON t.cashier_id = c.id 
            JOIN transaction_items ti ON t.id = ti.transaction_id 
            JOIN stocks s ON ti.item_id = s.id 
            GROUP BY t.id
        """)
        transactions = cur.fetchall()
        cur.close()
        return render_template('transactions.html', transactions=transactions)
    return redirect(url_for('admin_login'))


@app.route('/monthly_report')
def monthly_report():
    if 'user' in session and session['user'] == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATE_FORMAT(transaction_date, '%Y-%m') as month, SUM(total_amount) as total, COUNT(*) as transaction_count, GROUP_CONCAT(c.username) as cashiers FROM transactions t JOIN cashiers c ON t.cashier_id = c.id GROUP BY month")
        report = cur.fetchall()
        cur.close()
        return render_template('monthly_report.html', report=report)
    return redirect(url_for('admin_login'))

@app.route('/cashier_dashboard')
def cashier_dashboard():
    if session.get('user') == 'cashier':
        cashier_name = session.get('cashier_name', 'Cashier')
        return render_template('cashier_dashboard.html', cashier_name=cashier_name)
    return redirect(url_for('cashier_login'))


@app.route('/search_items', methods=['POST'])
def search_items():
    try:
        if session.get('user') == 'cashier':
            query = request.form['query']
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, item_name, price FROM stocks WHERE item_name LIKE %s", ('%' + query + '%',))
            items = cur.fetchall()
            cur.close()
            return jsonify(items=items)
        return redirect(url_for('cashier_login'))
    except Exception as e:
        print("Error in /search_items:", e)  # ✅ This prints to Flask console
        return jsonify({'error': 'Internal Server Error'}), 500
    

@app.route('/scan_barcode', methods=['POST'])
def scan_barcode():
    if 'user' in session and session['user'] == 'cashier':
        barcode = request.form['barcode']
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, item_name, price FROM stocks WHERE barcode = %s", (barcode,))
        item = cur.fetchone()
        cur.close()
        return jsonify(item=item)
    return redirect(url_for('cashier_login'))

@app.route('/new_billing', methods=['GET', 'POST'])
def new_billing():
    if request.method == 'POST':
        total_amount_str = request.form.get('total_amount', '').strip()

        if not total_amount_str:
            flash("Total amount is required", "error")
            return redirect('/new_billing')

        try:
            total_amount = float(total_amount_str)
        except ValueError:
            flash("Invalid total amount entered", "error")
            return redirect('/new_billing') 
    return render_template('new_billing.html')

@app.route('/print_bill/<int:transaction_id>')
def print_bill(transaction_id):
    cur = mysql.connection.cursor()

    # ✅ Correct column names from the DB
    cur.execute("""
    SELECT t.date, t.time, t.total, t.cashier_id, c.username
    FROM transactions t
    LEFT JOIN cashiers c ON t.cashier_id = c.id
    WHERE t.id = %s
""", (transaction_id,))

    
    transaction = cur.fetchone()

    if not transaction:
        return "Transaction not found", 404

    date, time, total, cashier_id, cashier_name = transaction

    # ✅ Fetch items
    cur.execute("""
        SELECT s.item_name, ti.quantity, s.price
        FROM transaction_items ti
        JOIN stocks s ON ti.item_id = s.id
        WHERE ti.transaction_id = %s
    """, (transaction_id,))
    
    items = cur.fetchall()
    cur.close()

    # ✅ Pass correct variables to template
    return render_template('print_bill.html',
                           transaction_id=transaction_id,
                           total=total,
                           items=items,
                           date=date,
                           time=time,
                           cashier=cashier_name)




@app.route('/submit_billing', methods=['POST'])
def submit_billing():
    items = request.form['items'].split(',')
    quantities = request.form['quantities'].split(',')
    total = request.form['total']

    cashier_id = session.get('cashier_id', 1)

    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    cur = mysql.connection.cursor()

    # ✅ Insert transaction with date & time
    cur.execute("""
        INSERT INTO transactions (cashier_id, total, date, time)
        VALUES (%s, %s, %s, %s)
    """, (cashier_id, total, current_date, current_time))
    
    transaction_id = cur.lastrowid

    # ✅ Insert each item in the transaction
    for item_id, qty in zip(items, quantities):
        cur.execute("""
            INSERT INTO transaction_items (transaction_id, item_id, quantity)
            VALUES (%s, %s, %s)
        """, (transaction_id, item_id, qty))

    mysql.connection.commit()
    cur.close()

    return redirect(url_for('print_bill', transaction_id=transaction_id))


@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)
