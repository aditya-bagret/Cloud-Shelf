from flask import Blueprint, render_template, request
from db_config import get_db_connection
from pymysql.cursors import DictCursor

search_results_bp = Blueprint('search_results', __name__)

@search_results_bp.route('/search')
def search_results():
    query = request.args.get('q', '')

    conn = get_db_connection()
    if not conn:
        return "Database connection failed.", 500

    with conn.cursor(DictCursor) as cursor:
        cursor.execute("""
            SELECT id, title, author, year, img_url 
            FROM book WHERE title LIKE %s OR author LIKE %s
        """, (f"%{query}%", f"%{query}%"))
        books = cursor.fetchall()  # ✅ Fetch as a list of dictionaries

    conn.close()

    print(books)  # 🔍 Debugging: See if `id` exists in books

    return render_template('search_results.html', books=books)
