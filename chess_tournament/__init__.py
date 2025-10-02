import os
from flask import Flask

def create_app(test_config=None):
    """
    This is the application factory. It creates and configures the Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load the default configuration from the config.py file
    app.config.from_object('config.Config')

    # Ensure the instance folder exists so the database can be created there
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # --- Initialize Database ---
    # This connects the database functions from db.py to our app
    from . import db
    db.init_app(app)

    # --- Register Routes (Blueprint) ---
    # This is the single, correct way to connect all the routes
    # from your routes.py file to the application.
    from . import routes
    app.register_blueprint(routes.bp)
    
    return app

