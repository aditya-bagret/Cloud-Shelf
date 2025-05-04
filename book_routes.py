from flask import Blueprint, render_template
from db_config import get_db_connection
from pymysql.cursors import DictCursor

book_routes_bp = Blueprint('book_routes', __name__)

@book_routes_bp.route('/book/<int:book_id>')
def book_details(book_id):
    conn = get_db_connection()
    if not conn:
        return "Database connection failed.", 500

    with conn.cursor(DictCursor) as cursor:
        cursor.execute("SELECT * FROM book WHERE id = %s", (book_id,))
        book = cursor.fetchone()  # ✅ Fetch book details

    conn.close()

    if not book:
        return "Book not found.", 404

    return render_template('book_details.html', book=book)
