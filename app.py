import MySQLdb
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
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange

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
            flash('Password reset successfully', 'success')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, username, phone FROM cashiers WHERE is_active = TRUE")
        cashiers = cur.fetchall()
        cur.close()
        return render_template('reset_cashier_password.html', cashiers=cashiers)
    return redirect(url_for('admin_login'))

@app.route('/remove_cashier', methods=['POST'])
def remove_cashier():
    if 'user' in session and session['user'] == 'admin':
        cashier_id = request.form['cashier_id']
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE cashiers SET is_active = FALSE WHERE id = %s", (cashier_id,))
            mysql.connection.commit()
            flash('Cashier deactivated successfully', 'success')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            flash(f'Error deactivating cashier: {str(e)}', 'error')
        finally:
            cur.close()
        return redirect(url_for('reset_cashier_password'))
    return redirect(url_for('admin_login'))

@app.route('/create_category', methods=['GET', 'POST'])
def create_category():
    """
    Allows admin users to create a new product category via POST request and view all categories via GET request.
    Returns rendered HTML for normal requests and JSON for AJAX POST requests.
    """
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            category_name = request.form['category_name'].strip()
            cur = mysql.connection.cursor()
            try:
                # Check if category already exists (case-insensitive)
                cur.execute("SELECT id FROM categories WHERE LOWER(name) = LOWER(%s) AND is_deleted = FALSE", (category_name,))
                existing_category = cur.fetchone()
                if existing_category:
                    flash('Category already exists', 'error')
                else:
                    cur.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
                    mysql.connection.commit()
                    new_category_id = cur.lastrowid
                    flash('Category created successfully', 'success')
                    # For AJAX requests, return JSON and let frontend refresh
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'message': 'Category created successfully',
                            'category': {'id': new_category_id, 'name': category_name},
                            'refresh': True
                        })
                    # For normal POST, redirect to refresh page and show flash
                    return redirect(url_for('create_category'))
            except MySQLdb.IntegrityError as e:
                mysql.connection.rollback()
                if e.args[0] == 1062:  # Duplicate entry
                    flash('Category already exists', 'error')
                else:
                    flash(f'Error creating category: {str(e)}', 'error')
            except MySQLdb.Error as e:
                mysql.connection.rollback()
                flash(f'Error creating category: {str(e)}', 'error')
            finally:
                cur.close()
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name FROM categories WHERE is_deleted = FALSE")
        categories = cur.fetchall()
        cur.close()
        return render_template('create_category.html', categories=categories)
    return redirect(url_for('admin_login'))

@app.route('/delete_category', methods=['POST'])
def delete_category():
    if 'user' in session and session['user'] == 'admin':
        try:
            category_id = request.form['category_id']
            print(f"Attempting to delete category with ID: {category_id}")
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM stocks WHERE category_id = %s AND is_deleted = FALSE", (category_id,))
            stock_count = cur.fetchone()[0]
            if stock_count > 0:
                cur.close()
                return jsonify({'error': 'Cannot delete category with associated stocks'}), 400
            # Permanently delete the category from the database
            cur.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            if cur.rowcount == 0:
                print(f"No category found with ID: {category_id}")
                return jsonify({'error': 'Category not found'}), 404
            mysql.connection.commit()
            print(f"Category {category_id} permanently deleted")
            cur.close()
            # Add 'refresh': True to signal frontend to refresh the page
            return jsonify({'message': 'Category deleted successfully', 'refresh': True})
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            print(f"Database error during category deletion: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        except Exception as e:
            print(f"Unexpected error during category deletion: {str(e)}")
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    return jsonify({'error': 'Unauthorized'}), 401



@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    if 'user' not in session or session['user'] != 'admin':
        return redirect(url_for('admin_login'))

    # Fetch categories
    with mysql.connection.cursor() as cur:
        cur.execute("SELECT id, name FROM categories WHERE is_deleted = FALSE")
        categories = cur.fetchall()

    if not categories:
        flash('No categories available. Please add a category first.', 'error')
        return render_template('add_stock.html', categories=categories)

    if request.method == 'POST':
        item_name = request.form['item_name'].strip()
        price = request.form['price']
        quantity = request.form['quantity']
        category_id = request.form['category_id']

        # Server-side validation
        try:
            if not item_name:
                raise ValueError("Item name cannot be empty.")
            price = float(price)
            if price <= 0:
                raise ValueError("Price must be greater than 0.")
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be at least 1.")
            if not category_id:
                raise ValueError("Please select a category.")
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('add_stock.html', categories=categories)

        item_id = str(uuid.uuid4())
        barcode_path = generate_barcode(item_id, item_name, price)

        try:
            with mysql.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO stocks (id, item_name, price, quantity, category_id, barcode)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (item_id, item_name, price, quantity, category_id, barcode_path))
                mysql.connection.commit()
            flash('Stock added successfully!', 'success')
            return redirect(url_for('add_stock'))  # PRG: Redirect to same page (GET)
            # Alternatively: return redirect(url_for('admin_dashboard'))  # Redirect to dashboard
        except mysql.connector.IntegrityError:
            mysql.connection.rollback()
            flash('Item name already exists or invalid data provided.', 'error')
            return render_template('add_stock.html', categories=categories)
        except Exception as e:
            mysql.connection.rollback()
            flash('Failed to add stock. Please try again.', 'error')
            return render_template('add_stock.html', categories=categories)

    # GET request: Render the form
    return render_template('add_stock.html', categories=categories)

@app.route('/check_stocks')
def check_stocks():
    if 'user' in session and session['user'] == 'admin':
        cur = mysql.connection.cursor()
        cur.execute("SELECT s.id, s.item_name, s.price, s.quantity, c.name, s.barcode FROM stocks s JOIN categories c ON s.category_id = c.id WHERE s.is_deleted = FALSE")
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
            cur.execute("SELECT s.id, s.item_name, s.price, s.quantity, c.name, s.barcode FROM stocks s JOIN categories c ON s.category_id = c.id WHERE s.category_id = %s AND s.is_deleted = FALSE", (category_id,))
        else:
            cur.execute("SELECT s.id, s.item_name, s.price, s.quantity, c.name, s.barcode FROM stocks s JOIN categories c ON s.category_id = c.id WHERE s.is_deleted = FALSE")
        stocks = cur.fetchall()
        cur.close()
        return jsonify(stocks=stocks)
    return jsonify({'error': 'Unauthorized'}), 401

@app.route('/delete_stock', methods=['POST'])
def delete_stock():
    if 'user' in session and session['user'] == 'admin':
        try:
            stock_id = request.form['stock_id']
            print(f"Soft-deleting stock with ID: {stock_id}")
            cur = mysql.connection.cursor()
            # Soft delete instead of physical delete
            cur.execute("UPDATE stocks SET is_deleted = TRUE WHERE id = %s", (stock_id,))
            if cur.rowcount == 0:
                print(f"No stock found with ID: {stock_id}")
                return jsonify({'error': 'Stock not found'}), 404
            mysql.connection.commit()
            cur.close()
            return jsonify({'message': 'Stock soft-deleted successfully'})
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            print(f"Database error during deletion: {str(e)}")
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        except Exception as e:
            print(f"Unexpected error during deletion: {str(e)}")
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    return jsonify({'error': 'Unauthorized'}), 401


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
