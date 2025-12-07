-- Drop existing tables
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS pairings;
DROP TABLE IF EXISTS tournaments;
DROP TABLE IF EXISTS history_standings;

-- Active Tournament Tables
CREATE TABLE players(
    SrNo INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    rating INTEGER NOT NULL,
    points REAL DEFAULT 0.0
);

CREATE TABLE pairings(
    Table_No INTEGER PRIMARY KEY AUTOINCREMENT,
    round_number INTEGER NOT NULL,
    player1_SrNo INTEGER NOT NULL,
    player2_SrNo INTEGER,
    result TEXT DEFAULT 'pending',
    FOREIGN KEY (player1_SrNo) REFERENCES players(SrNo),
    FOREIGN KEY (player2_SrNo) REFERENCES players(SrNo)
);

-- History / Archiving Tables
CREATE TABLE tournaments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date_concluded TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE history_standings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tournament_id INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    name TEXT NOT NULL,
    rating INTEGER NOT NULL,
    points REAL NOT NULL,
    buchholz REAL NOT NULL,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
);