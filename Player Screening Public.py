from sklearn import tree
from sklearn.svm import SVC
from sklearn.linear_model import Perceptron
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import numpy as np
import requests
import xlrd
import xlwt
from xlutils.copy import copy

#Making the initial call for the summoner profile and parsing the account ID from it
def getSummonerID(ign, api):
        url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+ign+"?api_key=" + api
        response = requests.get(url).json()
        return response['accountId']

#Returns an array of the last 15 match IDs the user had played within the given queue parameters
def getMatchData(accountID,api):
    url = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+accountID+"?queue=400&queue=420&queue=430&queue=440&queue=470&endIndex=15&api_key=" + api
    response = requests.get(url).json()
    return [x['gameId'] for x in response['matches']]
    #Short handing for making a list

#calculating the desired stats from each of the 15 games and taking the averages. Returns an array with 5 floats.    
def getMatchStats(matchData, ign,api):
    playerStats=[]
    kdas = 0
    visionScores = 0
    ccTime = 0
    topLane = 0
    csds = 0
    csdCount = 0
    for match in matchData:
        url = "https://na1.api.riotgames.com/lol/match/v4/matches/"+ str(match) +"?api_key="+ api
        response = requests.get(url).json()
        userIndex = getParticipantID(response, ign)
        kdas += calculateKDA(response, userIndex)
        visionScores += calculateVisionScore(response, userIndex)
        ccTime += calculateCCTime(response, userIndex)
        lane = getLaneStats(response, userIndex)
        if lane == 'TOP':
            topLane += 1
        #Riot's API will occasionally be unable to specify a lane opponent for a player, therefore omitting a CSD value as well. Only the matches with clearly defined CSDs are included in the average calculation.    
        csd = getCSD(response, userIndex, lane)
        if csd != False:
            csds += csd
            csdCount +=1
        
    avgKda = kdas/15
    avgVisionScore = visionScores/15
    avgCCTime = ccTime/15
    percentTop = topLane/15
    avgCsd = csds/csdCount
    playerStats.append(avgKda)
    playerStats.append(avgVisionScore)
    playerStats.append(avgCCTime)
    playerStats.append(percentTop)
    playerStats.append(avgCsd)
    
    return playerStats

#establishes the indexing for the user in each json's set of match statistics.
def getParticipantID(matchStats, ign):
    #Each match has exactly 10 players
    for i in range(10):
        tempIGN = matchStats['participantIdentities'][i]['player']['summonerName']
        if tempIGN == ign:
            participantID = i
    return participantID

#parses out the kills, deaths and assists values for each match and returns a ratio for those 3 values.
def calculateKDA(matchStats, participantID):
    #Traditional KDA doesn't differentiate between 0 deaths and 1 death for ratio calculations. This handles the divide by 0 edge case.
    if matchStats['participants'][participantID]['stats']['deaths'] == 0:
        deaths = 1
    else:
        deaths = matchStats['participants'][participantID]['stats']['deaths']

    kills = matchStats['participants'][participantID]['stats']['kills']
    assists = matchStats['participants'][participantID]['stats']['assists']
    kda = (kills + assists)/deaths
    return kda

#Returns the vision score for the player per match. Note that this value is heavily correlated with the amount of wards bought, but is not equivilant to it.
def calculateVisionScore(matchStats, participantID):
    visionScore = matchStats['participants'][participantID]['stats']['visionScore']
    return visionScore

#Returns the time spent applying crown control effects to enemy champions.
def calculateCCTime(matchStats, participantID):
    ccTime = matchStats['participants'][participantID]['stats']['timeCCingOthers']
    return ccTime

#Returns the role that the player played. The only value of interest here is "TOP". All other values will pass and not be a part of the calculations.
def getLaneStats(matchStats, participantID):
    lane = matchStats['participants'][participantID]['timeline']['lane']
    return lane

#Returns the CSD prior to 10 minutes in each match's time line.
def getCSD(matchStats, participantID, lane):
    #The try-except block is implemented here to check for the cases where CSD is unable to be calculated by Riot's API.
    try:
        #Supports don't traditionally CS, any differentials here are omitted since this is not a metric that defines proficiency at the role.
        if lane != "SUPPORT":
            csd = matchStats['participants'][participantID]['timeline']['csDiffPerMinDeltas']['0-10']
            return csd
    except:
        return False 

#Creates the array of pre-entered data points from the .xlsx sheet to be passed later for the prediction model.
def getTrain(sheet):
    train = []

    for i in range(100):
        temp = []
        temp.append(sheet.cell_value(i,0))
        temp.append(sheet.cell_value(i,1))
        temp.append(sheet.cell_value(i,2))
        temp.append(sheet.cell_value(i,3))
        temp.append(sheet.cell_value(i,4))
        train.append(temp)

    return train

#Compares the user's statistics against those used to train this predictive model.
def predict(train, decision, matchStats):
    clf_tree = tree.DecisionTreeClassifier().fit(train,decision)
    clf_svm = SVC().fit(train,decision)
    clf_perceptron = Perceptron().fit(train,decision)
    clf_KNN = KNeighborsClassifier().fit(train,decision)

    #Testing each of the models with the same data and determining the accuracy of each method
    predict_tree = clf_tree.predict(train)
    acc_tree = accuracy_score(decision, predict_tree)
    
    predict_svm = clf_svm.predict(train)
    acc_svm = accuracy_score(decision, predict_svm)

    predict_per = clf_perceptron.predict(train)
    acc_per = accuracy_score(decision, predict_tree)

    predict_KNN = clf_KNN.predict(train)
    acc_KNN = accuracy_score(decision, predict_KNN)

    #Adding all of the models' accuracies to a dictionary and pulling the max value
    accuracy = {'tree': acc_tree, 'svm': acc_svm, 'per':acc_per, 'KNN':acc_KNN}
    optimal = max(accuracy, key=accuracy.get)

    #prediction is returned based on which model had the highest accuracy score. Add in additional parameters for ties in the future. 
    if optimal == 'tree':
            prediction = clf_tree.predict([matchStats])
    if optimal == 'svm':
            prediction = clf_svm.predict([matchStats])
    if optimal == 'per':
            prediction = clf_per.predict([matchStats])
    if optimal == 'KNN':
            prediction = clf_KNN.predict([matchStats])
    return prediction
    
def main():
    ign = input("Please enter your ign: ")
    api = input("Please enter your API Key:" )
    accountID = getSummonerID(ign,api)
    matchData = getMatchData(accountID,api)
    matchStats = getMatchStats(matchData,ign,api)
    
    workbook = xlrd.open_workbook('League Screening Training Data.xlsx')
    sheet = workbook.sheet_by_index(0)
    decision = sheet.col_values(5) #Contains the "Yes" or "No" values on players that I had decided based on their stats.
    train = getTrain(sheet)
    prediction = predict(train, decision, matchStats)
    
    print("The following values are based off your most recent 15 games in all Summoner's Rift and Twisted Treeline Queues:")
    print("KDA: %.2f" % matchStats[0])
    print("Average Vision Score: %.2f" % matchStats[1])
    print("Your average time in seconds spent CCing enemies: %.2f" % matchStats[2])
    print("Your percent games played in top lane: %.2f" % matchStats[3])
    print("Your average CS differential by 10 minutes: %.2f" % matchStats[4])
    print("Verdict, would I play with you?: " + prediction[0])

if __name__ == "__main__":
    main()
