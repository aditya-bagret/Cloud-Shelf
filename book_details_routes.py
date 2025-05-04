from flask import Blueprint, render_template, session, jsonify, make_response, request
from db_config import get_db_connection

book_details_bp = Blueprint("book_details_bp", __name__)

# Route to display book details
@book_details_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch book details and category
        cursor.execute("""
            SELECT b.*, c.name AS category_name
            FROM book b
            LEFT JOIN category c ON b.category_id = c.id
            WHERE b.id = %s
        """, (book_id,))
        book = cursor.fetchone()

        if not book:
            return "Book not found", 404

        # Check if the book is in the user's wishlist
        in_wishlist = False
        if user_id:
            cursor.execute("""
                SELECT 1 FROM wishlist WHERE user_id = %s AND book_id = %s
            """, (user_id, book_id))
            in_wishlist = cursor.fetchone() is not None

        # Render the book detail page with wishlist status
        response = make_response(render_template("book_details.html", book=book, in_wishlist=in_wishlist))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    except Exception as e:
        print(f"Error in book_detail: {str(e)}")
        return "Server error", 500
    finally:
        cursor.close()
        conn.close()

# Route to read the book and fetch reading progress
@book_details_bp.route('/book/<int:book_id>/read')
def read_book(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return render_template("login_required.html")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM book WHERE id = %s", (book_id,))
        book = cursor.fetchone()

        # Default to page 1 if no progress found
        cursor.execute("""
            SELECT last_page FROM reading_progress
            WHERE user_id = %s AND book_id = %s
        """, (user_id, book_id))
        progress = cursor.fetchone()
        last_page = progress['last_page'] if progress else 1

        return render_template("blank_reader.html", book=book, last_page=last_page)

    except Exception as e:
        print(f"Error in read_book: {str(e)}")
        return "Server error", 500
    finally:
        cursor.close()
        conn.close()

# Route to update reading progress via AJAX (JSON)
@book_details_bp.route('/update_progress/<int:book_id>', methods=['POST'])
def update_progress(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        current_page = data.get('page', 1)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert or update last_page in reading_progress
        cursor.execute("""
            INSERT INTO reading_progress (user_id, book_id, last_page)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE last_page = %s
        """, (user_id, book_id, current_page, current_page))
        conn.commit()

        return jsonify({'message': 'Progress saved'}), 200

    except Exception as e:
        print(f"Error in update_progress: {str(e)}")
        return jsonify({'message': 'Error updating progress'}), 500
    finally:
        cursor.close()
        conn.close()

# Route to add a book to the wishlist
@book_details_bp.route('/wishlist/add/<int:book_id>', methods=['POST'])
def add_to_wishlist(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO wishlist (user_id, book_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE user_id = user_id
        """, (user_id, book_id))
        conn.commit()

        return jsonify({"message": "Added to wishlist"}), 200

    except Exception as e:
        conn.rollback()
        print(f"Error in add_to_wishlist: {str(e)}")
        return jsonify({"message": "Error adding to wishlist"}), 500

    finally:
        cursor.close()
        conn.close()

# Route to remove a book from the wishlist
@book_details_bp.route('/wishlist/remove/<int:book_id>', methods=['POST'])
def remove_from_wishlist(book_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND book_id = %s", (user_id, book_id))
        conn.commit()
        return jsonify({"message": "Removed from wishlist"}), 200

    except Exception as e:
        conn.rollback()
        print(f"Error in remove_from_wishlist: {str(e)}")
        return jsonify({"message": "Error removing from wishlist"}), 500

    finally:
        cursor.close()
        conn.close()
