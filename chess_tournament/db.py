import sqlite3
import click
from flask import current_app, g

def get_db():
    """
    Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """
    If a connection was created, close it. This is called automatically
    when the application context is torn down.
    """
    db = g.pop('db', None)
    # This is the corrected line
    if db is not None:
        db.close()

def init_db():
    """Clear existing data and create new tables."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """CLI command to initialize the database."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# --- CORE DATABASE QUERY FUNCTIONS ---

def get_all_players_from_db():
    """Fetches all players, ordered by rating."""
    db = get_db()
    players = db.execute(
        'SELECT SrNo, name, rating, points FROM players ORDER BY rating DESC'
    ).fetchall()
    return players

def add_player_to_db(name, rating):
    """Adds a new player to the database."""
    db = get_db()
    db.execute(
        'INSERT INTO players (name, rating) VALUES (?, ?)',
        (name, rating)
    )
    db.commit()

