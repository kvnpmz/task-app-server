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

