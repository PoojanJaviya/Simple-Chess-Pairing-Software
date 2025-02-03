from input import taking_input_storing_in_dataframe

#pairing the players
paired = set()
pairings = []

df = taking_input_storing_in_dataframe()

def pairing_players(df):
    for i in range(len(df)-1):
        player1 = df.iloc[i]["Names"]
        player2 = df.iloc[i+1]["Names"]
        if player1 in paired or player2 in paired:
            continue
        
        paired.add(player1)
        paired.add(player2)

        pairings.append((player1,player2))

    #If there are odd players then one gets a bye
    if(len(df)%2 == 1):
        pairings.append((df["Names"].iloc[-1],"Bye"))
        paired.add(df["Names"].iloc[-1])
    return paired , pairings

pairing_players(df)
print(paired)
print(pairings)

