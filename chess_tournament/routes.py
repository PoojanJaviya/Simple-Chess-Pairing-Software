from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from . import pairing_logic

bp = Blueprint('main', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    """Main page: lists players and handles new player form."""
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        error = None
        if not name: error = 'Name is required.'
        elif not rating: error = 'Rating is required.'
        if error is None:
            try:
                players_in_db = db.get_all_players_from_db()
                if any(p['name'].lower() == name.lower() for p in players_in_db):
                     raise db.get_db().IntegrityError
                db.add_player_to_db(name, int(rating))
                flash('Player added successfully!', 'success')
            except db.get_db().IntegrityError:
                flash(f"Player '{name}' is already registered.", 'error')
            except ValueError:
                flash("Rating must be an integer.", 'error')
            return redirect(url_for('main.index'))
        flash(error, 'error')
    players = db.get_all_players_from_db()
    return render_template('index.html', players=players)


@bp.route('/generate-pairings', methods=('POST',))
def generate_pairings():
    """Generates pairings and awards BYE points."""
    players = db.get_all_players_from_db()
    if len(players) < 2:
        flash('You need at least two players to generate pairings.', 'error')
        return redirect(url_for('main.index'))
    
    db.clear_pairings_from_db()
    pairings = pairing_logic.generate_first_round_pairs(players)
    db.add_pairings_to_db(pairings)
    
    # Award point to BYE player immediately
    for p1_sr_no, p2_sr_no in pairings:
        if p2_sr_no is None:
            db.update_player_score_in_db(p1_sr_no, 1.0)
            flash('BYE point awarded successfully.', 'info')
            break

    flash('Pairings generated successfully!', 'success')
    return redirect(url_for('main.view_pairings'))


@bp.route('/pairings')
def view_pairings():
    """Displays the current pairings."""
    pairings = db.get_pairings_from_db()
    return render_template('pairings.html', pairings=pairings)


@bp.route('/record-result', methods=('POST',))
def record_result():
    """Handles submission of a match result."""
    board_display_number = request.form['board_display_number']
    table_no = request.form['table_no']
    result = request.form['result']
    player1_sr_no = request.form['player1_sr_no']
    player2_sr_no = request.form['player2_sr_no']
    
    db.update_match_result_in_db(table_no, result)
    
    if result == '1-0':
        db.update_player_score_in_db(int(player1_sr_no), 1.0)
    elif result == '0-1':
        if player2_sr_no:
            db.update_player_score_in_db(int(player2_sr_no), 1.0)
    elif result == '0.5-0.5':
        db.update_player_score_in_db(int(player1_sr_no), 0.5)
        if player2_sr_no:
            db.update_player_score_in_db(int(player2_sr_no), 0.5)
            
    flash(f'Result for Board {board_display_number} recorded!', 'success')
    return redirect(url_for('main.view_pairings'))


@bp.route('/reset-tournament', methods=('POST',))
def reset_tournament():
    """Resets the tournament by deleting all data."""
    db.reset_tournament_in_db()
    flash('Tournament has been reset. All players and pairings deleted.', 'success')
    return redirect(url_for('main.index'))

