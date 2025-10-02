from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from . import pairing_logic

bp = Blueprint('main', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    """
    Handles the main page for adding and viewing players.
    """
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        error = None

        if not name:
            error = 'Name is required.'
        elif not rating:
            error = 'Rating is required.'
        
        if error is None:
            try:
                # Check for duplicate name before adding
                players_in_db = db.get_all_players_from_db()
                if any(p['name'].lower() == name.lower() for p in players_in_db):
                     raise db.get_db().IntegrityError

                db.add_player_to_db(name, int(rating))
                flash('Player added successfully!', 'success')
            except db.get_db().IntegrityError:
                error = f"Player {name} is already registered."
                flash(error, 'error')
            except ValueError:
                error = "Rating must be an integer."
                flash(error, 'error')
            return redirect(url_for('main.index'))
        
        flash(error, 'error')

    players = db.get_all_players_from_db()
    return render_template('index.html', players=players)

@bp.route('/generate-pairings', methods=('POST',))
def generate_pairings():
    """
    Generates and saves new pairings for the first round.
    """
    players = db.get_all_players_from_db()
    if len(players) < 2:
        flash('You need at least two players to generate pairings.', 'error')
        return redirect(url_for('main.index'))

    # Clear old pairings before creating new ones
    db.clear_pairings_from_db()

    # Generate the pairs
    pairings = pairing_logic.generate_first_round_pairs(players)

    # Save to the database
    db.add_pairings_to_db(pairings)
    
    flash('Pairings generated successfully!', 'success')
    return redirect(url_for('main.view_pairings'))

@bp.route('/pairings')
def view_pairings():
    """
    Displays the current round's pairings.
    """
    pairings = db.get_pairings_from_db()
    return render_template('pairings.html', pairings=pairings)

