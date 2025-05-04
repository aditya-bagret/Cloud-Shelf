from flask import Blueprint, render_template, session, redirect, url_for, request
from db_config import get_db_connection

wishlist_view_bp = Blueprint("wishlist_view_bp", __name__)

@wishlist_view_bp.route('/wishlist')
def view_wishlist():
    user_id = session.get('user_id')
    if not user_id:
        return "Please log in to view your wishlist.", 401

    conn = get_db_connection()
    cursor = conn.cursor()

    # Join wishlist and book tables to get full book details
    query = """
        SELECT b.id, b.title, b.author, b.year, b.img_url
        FROM wishlist w
        JOIN book b ON w.book_id = b.id
        WHERE w.user_id = %s
    """
    cursor.execute(query, (user_id,))
    wishlist_books = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("wishlist.html", wishlist_books=wishlist_books)


@wishlist_view_bp.route('/remove_from_wishlist/<int:book_id>', methods=["POST"])
def remove_from_wishlist(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return "Please log in to remove books from wishlist.", 401

    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete book from wishlist table
    query = "DELETE FROM wishlist WHERE user_id = %s AND book_id = %s"
    cursor.execute(query, (user_id, book_id))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('wishlist_view_bp.view_wishlist'))


@wishlist_view_bp.route('/book/<int:book_id>')
def book_details_from_wishlist(book_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get book details from the database
    query = "SELECT * FROM book WHERE id = %s"
    cursor.execute(query, (book_id,))
    book_details = cursor.fetchone()

    cursor.close()
    conn.close()

    if book_details:
        return render_template('book_details.html', book=book_details)
    else:
        return "Book not found", 404
