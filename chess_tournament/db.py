import sqlite3
import click
from flask import current_app, g

def get_db():
    """Connect to the application database for the current request."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Clear existing data and create new tables from schema.sql."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """A command-line command that initializes the database."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app instance."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_all_players_from_db():
    """Get all players, ordered by points, then rating."""
    db = get_db()
    players = db.execute('SELECT SrNo, name, rating, points FROM players ORDER BY points DESC, rating DESC').fetchall()
    return players

def add_player_to_db(name, rating):
    """Add a new player to the database."""
    db = get_db()
    db.execute('INSERT INTO players (name, rating) VALUES (?, ?)', (name, rating))
    db.commit()

def clear_pairings_from_db():
    """Clear all pairings from the database."""
    db = get_db()
    db.execute('DELETE FROM pairings')
    db.commit()

def add_pairings_to_db(pairings):
    """Add a list of pairings to the database."""
    db = get_db()
    db.executemany('INSERT INTO pairings (player1_SrNo, player2_SrNo) VALUES (?, ?)', pairings)
    db.commit()

def get_pairings_from_db():
    """Get current pairings with player names using a JOIN."""
    db = get_db()
    pairings = db.execute('''
        SELECT
            p.Table_No, p.player1_SrNo, p.player2_SrNo,
            p1.name as player1_name, p2.name as player2_name, p.result
        FROM pairings p
        JOIN players p1 ON p.player1_SrNo = p1.SrNo
        LEFT JOIN players p2 ON p.player2_SrNo = p2.SrNo
    ''').fetchall()
    return pairings

def update_match_result_in_db(table_no, result):
    """Update the result for a given match."""
    db = get_db()
    db.execute(
        'UPDATE pairings SET result = ? WHERE Table_No = ?',
        (result, table_no)
    )
    db.commit()

def update_player_score_in_db(player_sr_no, points_to_add):
    """Update a player's score by adding points."""
    db = get_db()
    db.execute(
        'UPDATE players SET points = points + ? WHERE SrNo = ?',
        (points_to_add, player_sr_no)
    )
    db.commit()

def reset_tournament_in_db():
    """Deletes all players and pairings to reset the tournament."""
    db = get_db()
    db.execute('DELETE FROM pairings')
    db.execute('DELETE FROM players')
    db.commit()

