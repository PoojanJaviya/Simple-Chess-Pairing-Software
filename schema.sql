CREATE TABLE IF NOT EXISTS players(
    SrNo INTEGER NOT NULL,
    name TEXT NOT NULL,
    rating INTEGER NOT NULL,
    points DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pairings(
    Table_No INTEGER PRIMARY KEY AUTOINCREMENT,
    player1_SrNo INTEGER,
    player2_SrNo INTEGER NULL,
    result TEXT DEFAULT NULL,
    FOREIGN KEY (player1_SrNo) REFERENCES players(SrNo)
    FOREIGN KEY (player2_SrNo) REFERENCES players(SrNo)  
);

