from flask import (
    Blueprint, flash, g, jsonify, redirect, request, url_for
)
from werkzeug.exceptions import abort

from ordermate.auth import login_required
from ordermate.database_file import get_database_connection

bp = Blueprint('blog', __name__)

@bp.route('/posts', methods=['GET'])
def index():
    database_connection = get_database_connection()
    posts = database_connection.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    print("API Response:", posts)  # Add this line to print the response data
    return jsonify([dict(post) for post in posts])

@bp.route('/create', methods=['POST'])
@login_required
def create():
    title = request.json['title']
    body = request.json['body']
    print(f"Received title: {title}, body: {body}")  # Add this line
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return jsonify({"error": error}), 400
    else:
        database_connection = get_database_connection()
        database_connection.execute(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (?, ?, ?)',
            (title, body, g.user['id'])
        )
        database_connection.commit()
        return jsonify({"success": "Post created."})

@bp.route('/<int:id>', methods=['GET'])
def get_post(id, check_author=True):
    post = get_database_connection().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        return jsonify({"error": f"Post id {id} doesn't exist."}), 404

    if check_author and post['author_id'] != g.user['id']:
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(dict(post))

@bp.route('/<int:id>/update', methods=['PUT'])
@login_required
def update(id):
    post = get_post(id, check_author=False)

    title = request.json['title']
    body = request.json['body']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        return jsonify({"error": error}), 400
    else:
        database_connection = get_database_connection()
        database_connection.execute(
            'UPDATE post SET title = ?, body = ?'
            ' WHERE id = ?',
            (title, body, id)
        )
        database_connection.commit()
        return jsonify({"success": "Post updated."})

@bp.route('/<int:id>/delete', methods=['DELETE'])
@login_required
def delete(id):
    get_post(id, check_author=False)
    database_connection = get_database_connection()
    database_connection.execute('DELETE FROM post WHERE id = ?', (id,))
    database_connection.commit()
    return jsonify({"success": "Post deleted."})

