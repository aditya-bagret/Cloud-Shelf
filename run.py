from flask import Flask, render_template, request, redirect, url_for, session, flash
from db_config import get_db_connection
import hashlib
from pymysql.cursors import DictCursor

# Blueprints
from search import search_bp
from search_results import search_results_bp
from edit_profile import edit_profile_bp
from book_routes import book_routes_bp
from book_details_routes import book_details_bp
from wishlist_routes import wishlist_view_bp

# MySQL setup
from db import mysql

# Create Flask app
app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Required for session management

# Initialize MySQL
mysql.init_app(app)

# Register Blueprints
app.register_blueprint(search_bp)
app.register_blueprint(search_results_bp)
app.register_blueprint(edit_profile_bp)
app.register_blueprint(book_routes_bp)
app.register_blueprint(book_details_bp)  # ✅ Moved to correct place
app.register_blueprint(wishlist_view_bp)


# Home Route
@app.route('/')
def home():
    return render_template('index.html')


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for('register'))

        with conn.cursor(DictCursor) as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash(f"User already registered with email: {email}", "warning")
                return redirect(url_for('login'))

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)",
                (full_name, email, password_hash)
            )
            conn.commit()

        conn.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return redirect(url_for('login'))

        with conn.cursor(DictCursor) as cursor:
            cursor.execute("SELECT id, full_name, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

        conn.close()

        if not user:
            flash("No account found. Please register.", "danger")
            return redirect(url_for('register'))

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user['password'] != password_hash:
            flash("Invalid password. Try again.", "danger")
            return redirect(url_for('login'))

        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))

    return render_template('login.html')


# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('login'))

    with conn.cursor(DictCursor) as cursor:
        cursor.execute("SELECT id, full_name, email FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()

    conn.close()

    return render_template('dashboard.html', user=user)


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
