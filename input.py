# This file is specifically made to take inputs from user (e.g. How many rounds?, number of player,etc.)

import pandas as pd
from database import add_players_to_db

def taking_input_storing_in_dataframe():
    #Taking Input from user
    total_rounds = int(input("Enter the number of rounds:").strip())
    player_count = int(input("Enter total number of players playing in the tournaments:").strip())
    player_names = []
    player_ratings = []
    SrNo = [i for i in range(1,player_count+1)]
    for i in range(player_count):
        name = input("Enter Player Name:")
        rating = int(input("Enter the rating of the correspondence player:").strip())
        player_names.append(name)
        player_ratings.append(rating)
    add_players_to_db(player_names,player_ratings)

    #Storing it in Dataframe
    df = pd.DataFrame({ "Sr No." : SrNo,
                "Names":player_names,
                "Rating":player_ratings,
                    "Points": [0 for i in range(player_count)]},
                    index=[i for i in range( 1 , player_count+1)])
    df = df.sort_values(by="Rating", ascending=False)
    df.index= range( 1 , player_count+1)
    df.index.name = "Ranking"
    return df

