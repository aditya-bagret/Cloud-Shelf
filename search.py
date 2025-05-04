from flask import Blueprint, render_template, request, jsonify
from db_config import get_db_connection
from pymysql.cursors import DictCursor

search_bp = Blueprint('search', __name__)  # Create a Blueprint

# Search Suggestions Route
@search_bp.route('/search_suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip().lower()

    if not query:
        return jsonify([])

    conn = get_db_connection()
    if not conn:
        return jsonify([])

    with conn.cursor(DictCursor) as cursor:
        cursor.execute("SELECT title FROM book WHERE LOWER(title) LIKE %s LIMIT 5", (f"%{query}%",))
        books = cursor.fetchall()

    conn.close()
    return jsonify(books)

# Search Results Page
@search_bp.route('/search_results')
def search_results():
    query = request.args.get('q', '').strip().lower()

    if not query:
        return render_template("search_results.html", books=[], query=query)

    conn = get_db_connection()
    if not conn:
        return render_template("search_results.html", books=[], query=query)

    with conn.cursor(DictCursor) as cursor:
        # ✅ Select the `id` field too
        cursor.execute("SELECT id, title, author, year, img_url FROM book WHERE LOWER(title) LIKE %s", (f"%{query}%",))
        books = cursor.fetchall()

    conn.close()

    print(books)  # Optional: helpful for debugging
    return render_template("search_results.html", books=books, query=query)
