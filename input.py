# This file is specifically made to take inputs from user (e.g. How many rounds?, number of player,etc.)
import pandas as pd
total_rounds = int(input("Enter Number of Rounds:").strip())
player_count = int(input("Enter total number of players playing in the tournaments:").strip())
player_names = []
player_ratings = []
for i in range(player_count):
    name = input("Enter Player Name:")
    rating = int(input("Enter the rating of the correspondence player:").strip())
    player_names.append(name)
    player_ratings.append(rating)

