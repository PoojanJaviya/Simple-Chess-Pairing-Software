-- Delete existing tables if they exist to ensure a fresh start
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS pairings;

-- Create the players table with a primary key
CREATE TABLE players(
    SrNo INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    rating INTEGER NOT NULL,
    points REAL DEFAULT 0.0
);

-- Create the pairings table with the new round_number column
CREATE TABLE pairings(
    Table_No INTEGER PRIMARY KEY AUTOINCREMENT,
    round_number INTEGER NOT NULL,
    player1_SrNo INTEGER NOT NULL,
    player2_SrNo INTEGER,
    result TEXT DEFAULT 'pending',
    FOREIGN KEY (player1_SrNo) REFERENCES players(SrNo),
    FOREIGN KEY (player2_SrNo) REFERENCES players(SrNo)
);