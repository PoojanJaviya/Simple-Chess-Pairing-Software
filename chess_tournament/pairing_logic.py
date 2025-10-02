import random

def generate_first_round_pairs(players):
    """
    Generates pairings for the first round.
    - Shuffles players to randomize pairings.
    - Handles odd number of players by giving the last one a bye.
    """
    # Create a list of player IDs from the player objects
    player_ids = [player['SrNo'] for player in players]
    
    # Shuffle the list for random pairings
    random.shuffle(player_ids)
    
    # Handle bye if there's an odd number of players
    if len(player_ids) % 2 != 0:
        # The last player in the shuffled list gets a bye
        bye_player_id = player_ids.pop()
        pairings = [(bye_player_id, None)] # None represents a bye
    else:
        pairings = []

    # Create pairs from the remaining players
    it = iter(player_ids)
    for p1 in it:
        p2 = next(it)
        pairings.append((p1, p2))
        
    return pairings

