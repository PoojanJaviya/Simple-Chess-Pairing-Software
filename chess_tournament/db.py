import sqlite3
import click
from flask import current_app, g

# --- CORE CONNECTION FUNCTIONS ---
def get_db():
    """Connect to the application database."""
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

# --- PLAYER FUNCTIONS ---
def get_all_players_from_db():
    """Get all players, ordered by points, then rating."""
    db = get_db()
    players = db.execute('SELECT SrNo, name, rating, points FROM players ORDER BY points DESC, rating DESC').fetchall()
    return players

def add_player_to_db(name, rating):
    """Add a new player."""
    db = get_db()
    db.execute('INSERT INTO players (name, rating) VALUES (?, ?)', (name, rating))
    db.commit()

def update_player_score_in_db(player_sr_no, points_to_add):
    """Update a player's score by adding/subtracting points."""
    db = get_db()
    db.execute('UPDATE players SET points = points + ? WHERE SrNo = ?', (points_to_add, player_sr_no))
    db.commit()

# --- PAIRING/MATCH FUNCTIONS ---
def add_pairings_to_db(pairings, round_number):
    """Add a list of pairings for a specific round."""
    db = get_db()
    db.executemany(
        'INSERT INTO pairings (round_number, player1_SrNo, player2_SrNo) VALUES (?, ?, ?)',
        [(round_number, p1, p2) for p1, p2 in pairings]
    )
    db.commit()

def get_current_pairings_from_db():
    """Get pairings for the most recent round."""
    db = get_db()
    pairings = db.execute('''
        SELECT p.Table_No, p.round_number, p.player1_SrNo, p.player2_SrNo,
               p1.name as player1_name, p2.name as player2_name, p.result
        FROM pairings p
        JOIN players p1 ON p.player1_SrNo = p1.SrNo
        LEFT JOIN players p2 ON p.player2_SrNo = p2.SrNo
        WHERE p.round_number = (SELECT MAX(round_number) FROM pairings)
    ''').fetchall()
    return pairings

def get_match_history_from_db():
    """Get a set of all past matchups to avoid rematches."""
    db = get_db()
    history_tuples = db.execute('SELECT player1_SrNo, player2_SrNo FROM pairings WHERE player2_SrNo IS NOT NULL').fetchall()
    history = {tuple(sorted((p1, p2))) for p1, p2 in history_tuples}
    return history

def get_latest_round_number():
    """Get the number of the most recent round."""
    db = get_db()
    result = db.execute('SELECT MAX(round_number) FROM pairings').fetchone()
    return result[0] if result[0] is not None else 0

def update_match_result_in_db(table_no, result):
    """Update the result for a given match."""
    db = get_db()
    db.execute('UPDATE pairings SET result = ? WHERE Table_No = ?', (result, table_no))
    db.commit()

def get_match_by_table_no(table_no):
    """Gets a single match's details by its primary key."""
    db = get_db()
    match = db.execute('SELECT * FROM pairings WHERE Table_No = ?', (table_no,)).fetchone()
    return match

def are_all_results_in():
    """Check if all playable matches in the latest round are concluded."""
    db = get_db()
    latest_round = get_latest_round_number()
    if latest_round == 0:
        return True
    
    pending_matches = db.execute(
        'SELECT COUNT(*) FROM pairings WHERE round_number = ? AND result = ? AND player2_SrNo IS NOT NULL',
        (latest_round, 'pending')
    ).fetchone()[0]
    
    return pending_matches == 0

def get_all_finished_matches_from_db():
    """Get all matches that have been played (for tiebreak calculation)."""
    db = get_db()
    matches = db.execute('''
        SELECT player1_SrNo, player2_SrNo, result 
        FROM pairings 
        WHERE result IS NOT 'pending' AND player2_SrNo IS NOT NULL
    ''').fetchall()
    return matches

# --- TOURNAMENT FUNCTIONS ---
def conclude_round_in_db():
    """Finalizes the current round by marking pending games as 0-0."""
    db = get_db()
    latest_round = get_latest_round_number()
    if latest_round > 0:
        db.execute(
            "UPDATE pairings SET result = '0-0' WHERE round_number = ? AND result = 'pending' AND player2_SrNo IS NOT NULL",
            (latest_round,)
        )
        db.commit()

def reset_tournament_in_db():
    """Delete all players and pairings."""
    db = get_db()
    db.execute('DELETE FROM pairings')
    db.execute('DELETE FROM players')
    db.execute("DELETE FROM sqlite_sequence WHERE name IN ('players', 'pairings')")
    db.commit()