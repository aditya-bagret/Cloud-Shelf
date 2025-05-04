from flask import Blueprint, render_template, session, jsonify, make_response
from db_config import get_db_connection

book_details_bp = Blueprint("book_details_bp", __name__)

# Route to display book details
@book_details_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    user_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get book details
        cursor.execute("""
            SELECT b.*, c.name AS category_name
            FROM book b
            LEFT JOIN category c ON b.category_id = c.id
            WHERE b.id = %s
        """, (book_id,))
        book = cursor.fetchone()

        if not book:
            print(f"Book not found for book_id: {book_id}")
            return "Book not found", 404

        # Check if the book is in the user's wishlist
        in_wishlist = False
        if user_id:
            cursor.execute("""
                SELECT user_id, book_id
                FROM wishlist
                WHERE user_id = %s AND book_id = %s
            """, (user_id, book_id))
            wishlist_entry = cursor.fetchone()
            in_wishlist = wishlist_entry is not None

            # Debug logging
            print(f"Session in book_detail: {session}")
            print(f"book_detail - User ID: {user_id}, Book ID: {book_id}, Wishlist Entry: {wishlist_entry}, In Wishlist: {in_wishlist}")

            # Log all wishlist entries to compare user_id
            cursor.execute("SELECT user_id, book_id FROM wishlist")
            all_wishlist_entries = cursor.fetchall()
            print(f"All Wishlist Entries: {all_wishlist_entries}")
        else:
            print("No user_id in session")

        # Render book details with wishlist status
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

# Route to read the book
@book_details_bp.route('/book/<int:book_id>/read')
def read_book(book_id):
    if not session.get('user_id'):
        return render_template("login_required.html")

    # Fetch book from database
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM book WHERE id = %s", (book_id,))
    book = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("blank_reader.html", book=book)

# Route to add book to wishlist
@book_details_bp.route('/wishlist/add/<int:book_id>', methods=['POST'])
def add_to_wishlist(book_id):
    user_id = session.get('user_id')
    if not user_id:
        print("add_to_wishlist - No user_id in session")
        return jsonify({"message": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Debug logging
        print(f"add_to_wishlist - User ID: {user_id}, Book ID: {book_id}")

        # Insert into wishlist, ignoring duplicates (requires unique constraint on user_id, book_id)
        cursor.execute("""
            INSERT INTO wishlist (user_id, book_id) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE user_id = user_id
        """, (user_id, book_id))
        conn.commit()

        # Log the inserted entry
        cursor.execute("SELECT user_id, book_id FROM wishlist WHERE user_id = %s AND book_id = %s", (user_id, book_id))
        inserted_entry = cursor.fetchone()
        print(f"Inserted Wishlist Entry: {inserted_entry}")

        return jsonify({"message": "Added to wishlist"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error in add_to_wishlist: {str(e)}")
        return jsonify({"message": f"Error adding to wishlist: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

# Route to remove book from wishlist
@book_details_bp.route('/wishlist/remove/<int:book_id>', methods=['POST'])
def remove_from_wishlist(book_id):
    user_id = session.get('user_id')
    if not user_id:
        print("remove_from_wishlist - No user_id in session")
        return jsonify({"message": "Unauthorized"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Debug logging
        print(f"remove_from_wishlist - User ID: {user_id}, Book ID: {book_id}")

        # Remove the book from the wishlist
        cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND book_id = %s", (user_id, book_id))
        conn.commit()
        return jsonify({"message": "Removed from wishlist"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error in remove_from_wishlist: {str(e)}")
        return jsonify({"message": f"Error removing from wishlist: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()