import os

# Get the absolute path of the directory the config.py file is in
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-super-secret-key-that-you-should-change'
    # Define the path for the database file inside the 'instance' folder
    DATABASE = os.path.join(BASE_DIR, 'instance', 'tournament.sqlite')

