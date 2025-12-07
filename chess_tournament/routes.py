import csv
import io
from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response, session
from . import db
from . import pairing_logic
from chess_tournament.auth import login_required

bp = Blueprint('main', __name__)

@bp.route('/', methods=('GET', 'POST'))
@login_required 
def index():
    # 1. Check if Tournament Name is set in Session
    tournament_name = session.get('tournament_name')

    # If NO name is set, we just render the template. 
    if not tournament_name:
        return render_template('index.html', tournament_name=None)

    # If Name IS set, proceed with Player Logic
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
    
    # Calculate live standings
    raw_players = db.get_all_players_from_db()
    matches = db.get_all_finished_matches_from_db()
    detailed_players = pairing_logic.calculate_standings_with_tiebreaks(raw_players, matches)
    current_round = db.get_latest_round_number()
    
    return render_template('index.html', players=detailed_players, current_round=current_round, tournament_name=tournament_name)

@bp.route('/set-name', methods=('POST',))
@login_required 
def set_tournament_name():
    """Sets the tournament name in the session to start the flow."""
    name = request.form['tournament_name']
    if name:
        session['tournament_name'] = name
        # Also ensure DB is clear for a fresh start
        db.reset_tournament_in_db() 
        flash(f'Tournament "{name}" started! Now add players.', 'success')
    return redirect(url_for('main.index'))

# --- PAIRING & RESULTS ROUTES ---
@bp.route('/generate-pairings', methods=('POST',))
@login_required 
def generate_pairings():
    if not db.are_all_results_in():
        flash('Cannot generate next round. The current round must be concluded first.', 'error')
        return redirect(url_for('main.view_pairings'))
    players = db.get_all_players_from_db()
    if len(players) < 2:
        flash('You need at least two players.', 'error')
        return redirect(url_for('main.index'))
    latest_round = db.get_latest_round_number()
    next_round = latest_round + 1
    if next_round == 1:
        pairings = pairing_logic.generate_first_round_pairs(players)
    else:
        history = db.get_match_history_from_db()
        pairings = pairing_logic.generate_swiss_pairs(players, history)
    db.add_pairings_to_db(pairings, next_round)
    
    # Auto-win byes
    for p1, p2 in pairings:
        if p2 is None:
            db.update_player_score_in_db(p1, 1.0)
            break
            
    flash(f'Round {next_round} pairings generated!', 'success')
    return redirect(url_for('main.view_pairings'))

@bp.route('/pairings')
def view_pairings():
    pairings = db.get_current_pairings_from_db()
    current_round = db.get_latest_round_number()
    return render_template('pairings.html', pairings=pairings, current_round=current_round)

@bp.route('/record-result', methods=('POST',))
@login_required 
def record_result():
    table_no = int(request.form['table_no'])
    new_result = request.form['result']
    player1_sr_no = int(request.form['player1_sr_no'])
    
    # Handle optional player 2
    p2_val = request.form.get('player2_sr_no')
    player2_sr_no = int(p2_val) if p2_val and p2_val != 'None' else None

    # 1. Get Old Result
    old_match = db.get_match_by_table_no(table_no)
    old_result = old_match['result']

    # 2. Revert Old Score Logic
    if old_result == '1-0': db.update_player_score_in_db(player1_sr_no, -1.0)
    elif old_result == '0-1' and player2_sr_no: db.update_player_score_in_db(player2_sr_no, -1.0)
    elif old_result == '0.5-0.5':
        db.update_player_score_in_db(player1_sr_no, -0.5)
        if player2_sr_no: db.update_player_score_in_db(player2_sr_no, -0.5)

    # 3. Apply New Result & Score
    db.update_match_result_in_db(table_no, new_result)
    
    if new_result == '1-0': db.update_player_score_in_db(player1_sr_no, 1.0)
    elif new_result == '0-1' and player2_sr_no: db.update_player_score_in_db(player2_sr_no, 1.0)
    elif new_result == '0.5-0.5':
        db.update_player_score_in_db(player1_sr_no, 0.5)
        if player2_sr_no: db.update_player_score_in_db(player2_sr_no, 0.5)
            
    # 4. Return Response
    return redirect(url_for('main.view_pairings'))

@bp.route('/conclude-round', methods=('POST',))
@login_required 
def conclude_round():
    current_round = db.get_latest_round_number()
    db.conclude_round_in_db()
    flash(f'Round {current_round} has been concluded.', 'success')
    return redirect(url_for('main.index'))

# --- HISTORY & END TOURNAMENT ROUTES ---

@bp.route('/end-tournament', methods=('POST',))
@login_required 
def end_tournament():
    # Get name from Session (preferred) or form
    tournament_name = session.get('tournament_name') or request.form.get('tournament_name')
    
    if not tournament_name:
        flash("Error: Tournament name missing.", "error")
        return redirect(url_for('main.index'))

    # Calculate Final Standings
    raw_players = db.get_all_players_from_db()
    matches = db.get_all_finished_matches_from_db()
    final_standings = pairing_logic.calculate_standings_with_tiebreaks(raw_players, matches)
    
    # Archive
    tournament_id = db.save_tournament_to_history(tournament_name, final_standings)
    
    # Clear Session to allow new tournament
    session.pop('tournament_name', None)
    
    flash(f'Tournament "{tournament_name}" archived successfully!', 'success')
    return redirect(url_for('main.tournament_details', tournament_id=tournament_id, is_fresh=1))

@bp.route('/history')
def history():
    tournaments = db.get_all_tournaments()
    return render_template('history.html', tournaments=tournaments)

@bp.route('/history/<int:tournament_id>')
def tournament_details(tournament_id):
    is_fresh = request.args.get('is_fresh', 0)
    metadata = db.get_tournament_details(tournament_id)
    standings = db.get_tournament_standings(tournament_id)
    return render_template('tournament_details.html', tournament=metadata, standings=standings, is_fresh=is_fresh)

@bp.route('/export_history/<int:tournament_id>')
def export_history(tournament_id):
    metadata = db.get_tournament_details(tournament_id)
    standings = db.get_tournament_standings(tournament_id)
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Rank', 'Name', 'Rating', 'Points', 'Tiebreak (Buchholz)'])
    for p in standings:
        cw.writerow([p['rank'], p['name'], p['rating'], p['points'], p['buchholz']])

    output = make_response(si.getvalue())
    filename = f"{metadata['name'].replace(' ', '_')}_results.csv"
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"
    return output

@bp.route('/reset-and-home')
@login_required 
def reset_and_home():
    db.reset_tournament_in_db()
    session.pop('tournament_name', None) # Clear session
    flash('Board cleared.', 'success')
    return redirect(url_for('main.index'))