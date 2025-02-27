#This is a file where pairing logic is.

from database import ordered_by_ratings, add_pairings_to_database
import random


# First Round pairing logic
def pairing_players():
    table = ordered_by_ratings()
    paired = set()
    pairings = []
    possible_pairings = []
    players = []
    for i in table:
        players.append[i[0]]

    if(len(players)%2==1):
        players.append(None)
        
    for i in (players):
        ls = [(a,b) for a in players for b in players if(a!=b) ]
        possible_pairings = possible_pairings + ls
        
    unpaired = players.copy()
    while(len(unpaired)!=0):   
        pairing = (random.choice(possible_pairings))
        if(pairing[0] not in paired and pairing[1] not in paired and pairing not in pairings):
            pairings.append(pairing)
            paired.add(pairing[0])
            paired.add(pairing[1])
            unpaired.remove(pairing[0])
            unpaired.remove(pairing[1])
    return pairings




