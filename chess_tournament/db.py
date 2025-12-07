import sqlite3
import click
from flask import current_app, g

# --- CORE CONNECTION FUNCTIONS ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# --- PLAYER FUNCTIONS ---
def get_all_players_from_db():
    db = get_db()
    players = db.execute('SELECT SrNo, name, rating, points FROM players ORDER BY points DESC, rating DESC').fetchall()
    return players

def add_player_to_db(name, rating):
    db = get_db()
    db.execute('INSERT INTO players (name, rating) VALUES (?, ?)', (name, rating))
    db.commit()

def update_player_score_in_db(player_sr_no, points_to_add):
    db = get_db()
    db.execute('UPDATE players SET points = points + ? WHERE SrNo = ?', (points_to_add, player_sr_no))
    db.commit()

# --- PAIRING FUNCTIONS ---
def add_pairings_to_db(pairings, round_number):
    db = get_db()
    db.executemany(
        'INSERT INTO pairings (round_number, player1_SrNo, player2_SrNo) VALUES (?, ?, ?)',
        [(round_number, p1, p2) for p1, p2 in pairings]
    )
    db.commit()

def get_current_pairings_from_db():
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
    db = get_db()
    history_tuples = db.execute('SELECT player1_SrNo, player2_SrNo FROM pairings WHERE player2_SrNo IS NOT NULL').fetchall()
    history = {tuple(sorted((p1, p2))) for p1, p2 in history_tuples}
    return history

def get_latest_round_number():
    db = get_db()
    result = db.execute('SELECT MAX(round_number) FROM pairings').fetchone()
    return result[0] if result[0] is not None else 0

def update_match_result_in_db(table_no, result):
    db = get_db()
    db.execute('UPDATE pairings SET result = ? WHERE Table_No = ?', (result, table_no))
    db.commit()

def get_match_by_table_no(table_no):
    db = get_db()
    match = db.execute('SELECT * FROM pairings WHERE Table_No = ?', (table_no,)).fetchone()
    return match

def are_all_results_in():
    db = get_db()
    latest_round = get_latest_round_number()
    if latest_round == 0: return True
    pending_matches = db.execute(
        'SELECT COUNT(*) FROM pairings WHERE round_number = ? AND result = ? AND player2_SrNo IS NOT NULL',
        (latest_round, 'pending')
    ).fetchone()[0]
    return pending_matches == 0

def get_all_finished_matches_from_db():
    db = get_db()
    matches = db.execute("SELECT player1_SrNo, player2_SrNo, result FROM pairings WHERE result IS NOT 'pending' AND player2_SrNo IS NOT NULL").fetchall()
    return matches

# --- ACTIVE TOURNAMENT FUNCTIONS ---
def conclude_round_in_db():
    db = get_db()
    latest_round = get_latest_round_number()
    if latest_round > 0:
        db.execute("UPDATE pairings SET result = '0-0' WHERE round_number = ? AND result = 'pending' AND player2_SrNo IS NOT NULL", (latest_round,))
        db.commit()

def reset_tournament_in_db():
    db = get_db()
    db.execute('DELETE FROM pairings')
    db.execute('DELETE FROM players')
    db.execute("DELETE FROM sqlite_sequence WHERE name IN ('players', 'pairings')")
    db.commit()

# --- HISTORY / ARCHIVE FUNCTIONS ---

def save_tournament_to_history(tournament_name, final_standings):
    """Saves the current tournament standings to the history tables."""
    db = get_db()
    cursor = db.cursor()
    
    # 1. Create Tournament Entry
    cursor.execute('INSERT INTO tournaments (name) VALUES (?)', (tournament_name,))
    tournament_id = cursor.lastrowid
    
    # 2. Save each player's final stats
    # final_standings is expected to be a list of dicts with 'name', 'rating', 'points', 'buchholz'
    for rank, player in enumerate(final_standings, 1):
        cursor.execute('''
            INSERT INTO history_standings (tournament_id, rank, name, rating, points, buchholz)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tournament_id, rank, player['name'], player['rating'], player['points'], player['buchholz']))
    
    db.commit()
    return tournament_id

def get_all_tournaments():
    """Returns a list of all past tournaments."""
    db = get_db()
    return db.execute('SELECT * FROM tournaments ORDER BY date_concluded DESC').fetchall()

def get_tournament_details(tournament_id):
    """Returns the metadata for a specific tournament."""
    db = get_db()
    return db.execute('SELECT * FROM tournaments WHERE id = ?', (tournament_id,)).fetchone()

def get_tournament_standings(tournament_id):
    """Returns the full standings for a specific past tournament."""
    db = get_db()
    return db.execute('SELECT * FROM history_standings WHERE tournament_id = ? ORDER BY rank ASC', (tournament_id,)).fetchall()