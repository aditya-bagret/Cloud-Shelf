
import logging
from db_config import get_db_connection
from pymysql.cursors import DictCursor
from flask import Blueprint, render_template, session, g, redirect, url_for, flash, request, jsonify
from datetime import datetime
import random

dashboard_bp = Blueprint('dashboard', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch user info from the database
def get_user():
    """
    Fetches user information from the database based on the user ID stored in the session.
    """
    user_id = session.get('user_id')
    if not user_id:
        logger.debug("No user_id in session")
        return None
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(DictCursor)
    try:
        cursor.execute("SELECT id, full_name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        user = None
    finally:
        cursor.close()
        conn.close()
    return user

# Fetch all books from the database
def get_all_books():
    """
    Fetches all books from the database.
    """
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(DictCursor)
    try:
        cursor.execute("SELECT id, title, author, img_url FROM book")
        books = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching all books: {e}")
        books = []
    finally:
        cursor.close()
        conn.close()
    return books

# Fetch a single book by ID
def get_book_by_id(book_id):
    """
    Fetches a single book from the database based on its ID.
    """
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(DictCursor)
    try:
        cursor.execute("SELECT id, title, author, img_url FROM book WHERE id = %s", (book_id,))
        book = cursor.fetchone()
    except Exception as e:
        logger.error(f"Error fetching book by ID: {e}")
        book = None
    finally:
        cursor.close()
        conn.close()
    return book

# Fetch reviews for a specific book
def get_reviews_by_book_id(book_id):
    """
    Fetches reviews for a specific book from the database.
    """
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(DictCursor)
    sql = """
        SELECT r.id, r.review_text, r.rating, u.full_name, r.created_at, u.id as user_id
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.book_id = %s
        ORDER BY r.created_at DESC
    """
    try:
        cursor.execute(sql, (book_id,))
        reviews = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching reviews by book ID: {e}")
        reviews = []
    finally:
        cursor.close()
        conn.close()
    return reviews

# Fetch reviews written by the current user
def get_reviews_by_user_id(user_id):
    """
    Fetches reviews written by a specific user from the database.
    """
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(DictCursor)
    sql = """
        SELECT r.id, r.review_text, r.rating, r.created_at,
                b.title AS book_title, b.author AS book_author, b.id AS book_id
        FROM reviews r
        JOIN book b ON r.book_id = b.id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
    """
    try:
        cursor.execute(sql, (user_id,))
        reviews = cursor.fetchall()
    except Exception as e:
        logger.error(f"Error fetching reviews by user ID: {e}")
        reviews = []
    finally:
        cursor.close()
        conn.close()
    return reviews

# Fetch a single review by its ID
def get_review_by_id(review_id):
    """Fetches a single review from the database."""
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(DictCursor)
    try:
        cursor.execute("SELECT id, book_id, review_text, rating, user_id FROM reviews WHERE id = %s", (review_id,))
        review = cursor.fetchone()
    except Exception as e:
        logger.error(f"Error fetching review by id: {e}")
        review = None
    finally:
        cursor.close()
        conn.close()
    return review

@dashboard_bp.before_request
def load_user():
    """
    Loads the current user's information before each request.
    """
    g.user = get_user()
    if not g.user and (request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
        logger.debug("AJAX request with no user, returning JSON redirect")
        return jsonify({'status': 'error', 'message': 'You must be logged in.', 'redirect': url_for('login')}), 401

@dashboard_bp.route('/dashboard')
def dashboard():
    """
    Renders the main dashboard page.
    """
    if not g.user:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))

    all_books = get_all_books()
    recommended_books = []
    if all_books:
        num_recommendations = min(6, len(all_books))
        try:
            recommended_books = random.sample(all_books, num_recommendations)
        except ValueError:
            recommended_books = all_books
    else:
        flash("No books available for recommendations.", "info")

    return render_template(
        'dashboard/dashboard.html',
        active_page='dashboard',
        user=g.user,
        recommended_books=recommended_books
    )

@dashboard_bp.route('/my-library')
def my_library():
    """
    Renders the user's library page.
    """
    if not g.user:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard/my_library.html', active_page='my_library')

@dashboard_bp.route('/wishlist')
def wishlist():
    """
    Renders the user's wishlist page.
    """
    if not g.user:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard/wishlist.html', active_page='wishlist')

@dashboard_bp.route('/recommendations')
def recommendations():
    """
    Renders the recommendations page.
    """
    if not g.user:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))

    all_books = get_all_books()
    recommended_books = []
    if all_books:
        num_recommendations = min(6, len(all_books))
        try:
            recommended_books = random.sample(all_books, num_recommendations)
        except ValueError:
            recommended_books = all_books
    else:
        flash("No books available for recommendations.", "info")

    return render_template(
        'dashboard/recommendations.html',
        active_page='recommendations',
        recommended_books=recommended_books
    )

@dashboard_bp.route('/reviews')
def reviews():
    """
    Renders the user's reviews page, showing the reviews they have written.
    """
    if not g.user:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))

    user_reviews = get_reviews_by_user_id(g.user['id'])
    return render_template('dashboard/reviews.html', active_page='reviews', reviews=user_reviews)

@dashboard_bp.route('/book/<int:book_id>')
def book_details(book_id):
    """
    Renders the details page for a specific book.
    """
    if not g.user:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))

    book = get_book_by_id(book_id)
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    reviews = get_reviews_by_book_id(book_id)

    return render_template(
        'dashboard/book_details.html',
        active_page='book_details',
        book=book,
        reviews=reviews
    )

@dashboard_bp.route('/book/<int:book_id>/write_review', methods=['GET', 'POST'])
def write_review(book_id):
    """
    Handles the creation of a new review for a book.
    """
    if not g.user:
        flash("You must be logged in to write a review.", "warning")
        return redirect(url_for('login'))

    book = get_book_by_id(book_id)
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        review_text = request.form.get('review_text')
        rating = request.form.get('rating', None)

        if not review_text:
            flash("Review text cannot be empty.", "danger")
            return render_template('dashboard/write_review.html', book=book)

        if rating is None or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            flash("Rating must be a number between 1 and 5.", "danger")
            return render_template('dashboard/write_review.html', book=book)

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template('dashboard/write_review.html', book=book)

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO reviews (user_id, book_id, review_text, rating, created_at) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (g.user['id'], book_id, review_text, int(rating), datetime.now()))
            conn.commit()
            flash("Your review has been submitted!", "success")
            return redirect(url_for('dashboard.reviews'))
        except Exception as e:
            logger.error(f"Error submitting review: {e}")
            conn.rollback()
            flash(f"Error submitting review: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('dashboard/write_review.html', book=book)

@dashboard_bp.route('/review/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    """Handles deleting an existing review."""
    # Ensure the request is AJAX
    if not (request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest'):
        logger.debug(f"Non-AJAX request for review delete: {review_id}")
        return jsonify({'status': 'error', 'message': 'Invalid request type.'}), 400

    # Check CSRF token if Flask-WTF is enabled
    csrf_token = request.headers.get('X-CSRF-Token')
    if not csrf_token:
        logger.debug(f"CSRF token missing for review delete: {review_id}")
        return jsonify({'status': 'error', 'message': 'CSRF token missing.'}), 403

    if not g.user:
        logger.debug("Unauthorized delete attempt: No user logged in")
        return jsonify({'status': 'error', 'message': 'You must be logged in to delete a review.', 'redirect': url_for('login')}), 401

    review = get_review_by_id(review_id)
    if not review:
        logger.debug(f"Review not found: {review_id}")
        return jsonify({'status': 'error', 'message': 'Review not found.'}), 404

    if review['user_id'] != g.user['id']:
        logger.debug(f"Unauthorized delete attempt by user {g.user['id']} for review {review_id}")
        return jsonify({'status': 'error', 'message': 'You are not authorized to delete this review.'}), 403

    conn = get_db_connection()
    if not conn:
        logger.error("Database connection failed during delete review")
        return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM reviews WHERE id = %s"
        cursor.execute(sql, (review_id,))
        conn.commit()
        logger.info(f"Review {review_id} deleted by user {g.user['id']}")
        return jsonify({'status': 'success', 'message': 'Your review has been deleted!'}), 200
    except Exception as e:
        logger.error(f"Error deleting review {review_id}: {e}")
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'Error deleting review: {str(e)}'}), 500
    finally:
        cursor.close()
        conn.close()

@dashboard_bp.route('/my_profile')
def my_profile():
    """
    Renders the user's profile page.
    """
    if not g.user:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))
    return render_template('my_profile.html', active_page='my_profile')

@dashboard_bp.route('/logout')
def logout():
    """
    Logs the user out by clearing the session and redirecting to the login page.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))