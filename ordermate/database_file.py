import sqlite3

import click
from flask import current_app, g


def get_database_connection():
    if 'database_connection' not in g:
        g.database_connection = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.database_connection.row_factory = sqlite3.Row

    return g.database_connection


def close_database_connection(e=None):
    database_connection = g.pop('database_connection', None)

    if database_connection is not None:
        database_connection.close()


def initialize_database():
    database_connection = get_database_connection()

    with current_app.open_resource('schema.sql') as schema_file:
        database_connection.executescript(schema_file.read().decode('utf8'))


@click.command('initialize-database')
def initialize_database_command():
    """Clear the existing data and create new tables."""
    initialize_database()
    click.echo('Initialized the database.')


def initialize_app(app):
    app.teardown_appcontext(close_database_connection)
    app.cli.add_command(initialize_database_command)

