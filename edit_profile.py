from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_config import get_db_connection
from pymysql.cursors import DictCursor

edit_profile_bp = Blueprint('edit_profile', __name__)

@edit_profile_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        favorite_genre = request.form.get('favorite_genre', '')

        # Handle Profile Picture Upload
        profile_pic = request.files.get('profile_pic')
        if profile_pic and profile_pic.filename:
            profile_path = f"static/images/{session['user_id']}.png"
            profile_pic.save(profile_path)

        with conn.cursor(DictCursor) as cursor:
            cursor.execute("UPDATE users SET full_name=%s, email=%s, favorite_genre=%s WHERE id=%s",
                           (full_name, email, favorite_genre, session['user_id']))
            conn.commit()

        conn.close()
        session['user_name'] = full_name  # Update session name
        flash("Profile updated successfully!", "success")
        return redirect(url_for('dashboard'))

    with conn.cursor(DictCursor) as cursor:
        cursor.execute("SELECT full_name, email, favorite_genre FROM users WHERE id=%s", (session['user_id'],))
        user = cursor.fetchone()

    conn.close()
    return render_template('edit_profile.html', user=user)
