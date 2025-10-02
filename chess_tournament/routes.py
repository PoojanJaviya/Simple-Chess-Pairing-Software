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
                     raise ValueError(f"Player '{name}' is already registered.")
                db.add_player_to_db(name, int(rating))
                flash('Player added successfully!', 'success')
            except ValueError as e:
                flash(str(e), 'error')
            return redirect(url_for('main.index'))

        flash(error, 'error')
    
    players = db.get_all_players_from_db()
    current_round = db.get_latest_round_number()
    return render_template('index.html', players=players, current_round=current_round)


@bp.route('/generate-pairings', methods=('POST',))
def generate_pairings():
    """Generates pairings only if the previous round is complete."""
    if not db.are_all_results_in():
        flash('Cannot generate next round. The current round must be concluded first.', 'error')
        return redirect(url_for('main.view_pairings'))

    players = db.get_all_players_from_db()
    if len(players) < 2:
        flash('You need at least two players to generate pairings.', 'error')
        return redirect(url_for('main.index'))
    
    latest_round = db.get_latest_round_number()
    next_round = latest_round + 1

    if next_round == 1:
        pairings = pairing_logic.generate_first_round_pairs(players)
    else:
        history = db.get_match_history_from_db()
        pairings = pairing_logic.generate_swiss_pairs(players, history)

    db.add_pairings_to_db(pairings, next_round)
    
    for p1_sr_no, p2_sr_no in pairings:
        if p2_sr_no is None:
            db.update_player_score_in_db(p1_sr_no, 1.0)
            flash('BYE point awarded successfully.', 'info')
            break

    flash(f'Round {next_round} pairings generated successfully!', 'success')
    return redirect(url_for('main.view_pairings'))


@bp.route('/pairings')
def view_pairings():
    """Displays the current pairings."""
    pairings = db.get_current_pairings_from_db()
    current_round = db.get_latest_round_number()
    return render_template('pairings.html', pairings=pairings, current_round=current_round)


@bp.route('/record-result', methods=('POST',))
def record_result():
    """Handles result changes, reversing old scores and applying new ones."""
    table_no = int(request.form['table_no'])
    new_result = request.form['result']
    player1_sr_no = int(request.form['player1_sr_no'])
    player2_sr_no_str = request.form.get('player2_sr_no')
    player2_sr_no = int(player2_sr_no_str) if player2_sr_no_str else None

    # --- Score Correction Logic ---
    old_match = db.get_match_by_table_no(table_no)
    old_result = old_match['result']

    # 1. Subtract points from the old result
    if old_result == '1-0':
        db.update_player_score_in_db(player1_sr_no, -1.0)
    elif old_result == '0-1' and player2_sr_no:
        db.update_player_score_in_db(player2_sr_no, -1.0)
    elif old_result == '0.5-0.5':
        db.update_player_score_in_db(player1_sr_no, -0.5)
        if player2_sr_no:
            db.update_player_score_in_db(player2_sr_no, -0.5)

    # 2. Update the match to the new result
    db.update_match_result_in_db(table_no, new_result)

    # 3. Add points for the new result
    if new_result == '1-0':
        db.update_player_score_in_db(player1_sr_no, 1.0)
    elif new_result == '0-1' and player2_sr_no:
        db.update_player_score_in_db(player2_sr_no, 1.0)
    elif new_result == '0.5-0.5':
        db.update_player_score_in_db(player1_sr_no, 0.5)
        if player2_sr_no:
            db.update_player_score_in_db(player2_sr_no, 0.5)
            
    flash(f'Result for Board {request.form["board_display_number"]} updated!', 'success')
    return redirect(url_for('main.view_pairings'))


@bp.route('/conclude-round', methods=('POST',))
def conclude_round():
    """Finalizes the current round."""
    current_round = db.get_latest_round_number()
    db.conclude_round_in_db()
    flash(f'Round {current_round} has been concluded. You can now generate the next round.', 'success')
    return redirect(url_for('main.index'))


@bp.route('/reset-tournament', methods=('POST',))
def reset_tournament():
    """Resets the tournament by deleting all data."""
    db.reset_tournament_in_db()
    flash('Tournament has been reset. All players and pairings deleted.', 'success')
    return redirect(url_for('main.index'))

