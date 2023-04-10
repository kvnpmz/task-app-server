import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from ordermate.database_file import get_database_connection

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('POST',))
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    database_connection = get_database_connection()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'

    if error is None:
        try:
            database_connection.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
            database_connection.commit()
        except database_connection.IntegrityError:
            error = f"User {username} is already registered."
        else:
            return jsonify({'success': True})

    return jsonify({'error': error})

@bp.route('/login', methods=('POST',))
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    database_connection = get_database_connection()
    error = None
    user = database_connection.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if user is None:
        error = 'Incorrect username.'
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['user_id'] = user['id']
        return jsonify({'success': True})

    return jsonify({'success': False, 'error': error})

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_database_connection().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    response = jsonify({'message': 'Logged out successfully'})
    response.status_code = 200
    return response

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({'success': True})

        return view(**kwargs)

    return wrapped_view
