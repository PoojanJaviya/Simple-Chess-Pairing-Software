import random
from collections import defaultdict

def generate_first_round_pairs(players):
    """Generates random pairings for the first round."""
    shuffled_players = list(players)
    random.shuffle(shuffled_players)
    
    # Handle BYE for odd number of players
    if len(shuffled_players) % 2 != 0:
        # The player with the lowest rating gets the bye
        lowest_rated_player = min(shuffled_players, key=lambda p: p['rating'])
        shuffled_players.remove(lowest_rated_player)
        shuffled_players.append(lowest_rated_player) # Move to end for pairing logic
        
    pairings = []
    # zip automatically handles odd numbers by stopping at the shortest list
    it = iter(shuffled_players)
    for p1 in it:
        try:
            p2 = next(it)
            pairings.append((p1['SrNo'], p2['SrNo']))
        except StopIteration:
            # This is the player who gets a bye
            pairings.append((p1['SrNo'], None))
            
    return pairings


def generate_swiss_pairs(players, history):
    """
    Generates pairings for subsequent rounds using Swiss-system logic.
    - Groups players by score.
    - Pairs within groups, avoiding rematches.
    - Floats down players if necessary.
    """
    # 1. Group players by their score
    score_groups = defaultdict(list)
    for player in players:
        score_groups[player['points']].append(player)

    # 2. Sort players within each group by rating
    for score in score_groups:
        score_groups[score].sort(key=lambda p: p['rating'], reverse=True)

    # 3. Pair players starting from the highest score group
    pairings = []
    unpaired_players = []
    sorted_scores = sorted(score_groups.keys(), reverse=True)

    for score in sorted_scores:
        group = unpaired_players + score_groups[score]
        unpaired_players = [] # Clear for this iteration
        
        while len(group) >= 2:
            p1 = group.pop(0)
            
            # Find a valid opponent for p1 in the rest of the group
            opponent_found = False
            for i, p2 in enumerate(group):
                # Check if this pairing has happened before
                matchup = tuple(sorted((p1['SrNo'], p2['SrNo'])))
                if matchup not in history:
                    pairings.append((p1['SrNo'], p2['SrNo']))
                    group.pop(i) # Remove p2 from the group
                    opponent_found = True
                    break
            
            if not opponent_found:
                # No valid opponent in this group, p1 will float down
                unpaired_players.append(p1)

        # Add any remaining player(s) to the unpaired list for the next lower group
        unpaired_players.extend(group)

    # 4. Handle the final unpaired player (the BYE)
    if unpaired_players:
        bye_player = unpaired_players.pop(0)
        pairings.append((bye_player['SrNo'], None))

    return pairings

