from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db

# THIS IS THE CRUCIAL LINE THAT WAS LIKELY MISSING
# It creates the Blueprint object that __init__.py is looking for.
bp = Blueprint('main', __name__)

@bp.route('/', methods=('GET', 'POST'))
def index():
    """
    Main page route. Displays players and handles new player submissions.
    """
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form['rating']
        error = None

        if not name:
            error = 'Name is required.'
        elif not rating:
            error = 'Rating is required.'
        else:
            try:
                db.add_player_to_db(name, int(rating))
                flash(f'Success! Player {name} has been added.', 'success')
                return redirect(url_for('main.index'))
            except ValueError:
                error = 'Rating must be a number.'
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    error = f"Player '{name}' already exists."
                else:
                    error = 'An error occurred while adding the player.'

        if error:
            flash(error, 'error')

    players = db.get_all_players_from_db()
    return render_template('index.html', players=players)
