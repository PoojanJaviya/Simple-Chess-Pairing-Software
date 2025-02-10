#This is a file where pairing logic is.

from input import taking_input_storing_in_dataframe
from database import  init_db, ordered_by_ratings, add_pairings_to_database

#pairing the players

init_db()
df = taking_input_storing_in_dataframe()
ordered_list = ordered_by_ratings()

def pairing_players():
    players = ordered_by_ratings()
    paired = set()
    pairings = []
    for i in range(len(players)-1):
        player1_SrNo = players[i][0]
        player2_SrNo = players[i+1][0]
        if player1_SrNo in paired or player2_SrNo in paired:
            continue

        pairings.append((player1_SrNo,player2_SrNo))
        paired.add(player1_SrNo)
        paired.add(player2_SrNo)

    if(len(df)%2 == 1):
        pairings.append((players[-1][0],None))
        paired.add(players[-1][0])

    return pairings
pairings = pairing_players()
add_pairings_to_database(pairings)


