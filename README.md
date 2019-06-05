# League-Player-Screening
Gathering data and training a predictive model to determine if a given individual would compliment my personal playstyle in League of Legends.

The metrics used were gathered over the latest 15 game that a player has played on:
-5v5 Blind Summoner's Rift
-5v5 Draft Pick Summoner's Rift
-5v5 Ranked Solo/Duo Summoner's Rift
-5v5 Flex Ranked Summoner's Rift
-3v3 Ranked Twisted Treeline

1. Average KDA to ensure they have a good understanding of how to play with restraint.
2. Average Vision Score to ensure that they can play the game from a macro perspective (And also to accomodate for my less than stellar performance in this category).
3. Average time spent applying crowd control effects to enemies to compliment my preferred bruiser-centric play style.
4. Percentage of games spent playing Top Lane, which is my personal preferred role. Preference was given to those who would leave the position open for me to take.
5. Average CS differential to assess proficiency in laning phase and ability to consistenly stay relevant as games progress. Limited to first 10 minutes of gameplay to ensure that this metric reflects individual performance over wholistic game state.

A player will be requested to enter their API key from Riot's developer portal (https://developer.riotgames.com/) and their ign.
Upon executing, the program will compile these stats from Riot's API. The results are tested against a predictive model of pre-determined 
player profiles and return either "Yes" or "No" based on their fit with my preferred qualifications for a League of Legends player.

Currently there are only 100 data points that each entry is being tested against. New data points are still being updated and parameters are being refined to produce more accurate models still.
