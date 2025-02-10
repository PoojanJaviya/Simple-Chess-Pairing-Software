#This is a file where every command related to database is stored

import sqlite3

#initialization of database
def init_db():
    conn = sqlite3.connect('database.db')
    with open('schema.sql','r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

#connection to database
def connect_to_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#player addition to database
def add_players_to_db(SrNo,players_names,player_ratings):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    player_data = zip(SrNo,players_names,player_ratings)
    cursor.executemany("INSERT INTO players (SrNo,name,rating) VALUES (?,?)",player_data)
    conn.commit()
    conn.close()

#fuctions to retrieve players from database
def ordered_by_ratings():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM players ORDER BY rating DESC")
    ordered_players = cursor.fetchall()
    
    conn.close()
    return ordered_players  

def get_players_from_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    return players

#below functions are just for testing if anytime needed to delete tables
def deleting_table_players():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE players")
    conn.commit()
    conn.close()
def deleting_table_pairings():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE pairings")
    conn.commit()
    conn.close()


#pairing functions
def add_pairings_to_database(pairings):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO pairings (player1_SrNo,player2_SrNo) VALUES (?,?)",pairings)
    conn.commit()
    conn.close()

def fetching_pairings():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pairings")
    pairings = cursor.fetchall()
    conn.commit()
    conn.close()
    return pairings