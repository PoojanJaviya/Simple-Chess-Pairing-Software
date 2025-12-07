import random
from collections import defaultdict

def generate_first_round_pairs(players):
    """Generates random pairings for the first round."""
    shuffled_players = list(players)
    random.shuffle(shuffled_players)
    
    if len(shuffled_players) % 2 != 0:
        lowest_rated_player = min(shuffled_players, key=lambda p: p['rating'])
        shuffled_players.remove(lowest_rated_player)
        shuffled_players.append(lowest_rated_player)
        
    pairings = []
    it = iter(shuffled_players)
    for p1 in it:
        try:
            p2 = next(it)
            pairings.append((p1['SrNo'], p2['SrNo']))
        except StopIteration:
            pairings.append((p1['SrNo'], None))
            
    return pairings


def generate_swiss_pairs(players, history):
    """Generates pairings for subsequent rounds using Swiss-system logic."""
    score_groups = defaultdict(list)
    for player in players:
        score_groups[player['points']].append(player)

    for score in score_groups:
        score_groups[score].sort(key=lambda p: p['rating'], reverse=True)

    pairings = []
    unpaired_players = []
    sorted_scores = sorted(score_groups.keys(), reverse=True)

    for score in sorted_scores:
        group = unpaired_players + score_groups[score]
        unpaired_players = []
        
        while len(group) >= 2:
            p1 = group.pop(0)
            opponent_found = False
            for i, p2 in enumerate(group):
                matchup = tuple(sorted((p1['SrNo'], p2['SrNo'])))
                if matchup not in history:
                    pairings.append((p1['SrNo'], p2['SrNo']))
                    group.pop(i)
                    opponent_found = True
                    break
            
            if not opponent_found:
                unpaired_players.append(p1)

        unpaired_players.extend(group)

    if unpaired_players:
        bye_player = unpaired_players.pop(0)
        pairings.append((bye_player['SrNo'], None))

    return pairings

def calculate_standings_with_tiebreaks(players, matches):
    """
    Calculates Tiebreaks (Buchholz) for each player.
    Buchholz = Sum of scores of all opponents played.
    Returns a list of dicts with updated player stats.
    """
    # 1. Create a dictionary for quick score lookup: {player_id: score}
    player_scores = {p['SrNo']: p['points'] for p in players}
    
    # 2. Build a map of opponents: {player_id: [list_of_opponent_ids]}
    opponents_map = defaultdict(list)
    
    for m in matches:
        p1, p2 = m['player1_SrNo'], m['player2_SrNo']
        # Add each other to their opponents list
        opponents_map[p1].append(p2)
        opponents_map[p2].append(p1)

    # 3. Calculate Buchholz and convert rows to mutable dicts
    final_standings = []
    for p in players:
        p_dict = dict(p) # Convert sqlite3.Row to dict to add new fields
        p_id = p_dict['SrNo']
        
        # Calculate Buchholz: Sum of opponents' scores
        opponents = opponents_map.get(p_id, [])
        buchholz_score = sum(player_scores.get(oid, 0) for oid in opponents)
        
        p_dict['buchholz'] = buchholz_score
        final_standings.append(p_dict)

    # 4. Sort by: Points (Desc) -> Buchholz (Desc) -> Rating (Desc)
    final_standings.sort(key=lambda x: (x['points'], x['buchholz'], x['rating']), reverse=True)
    
    return final_standings