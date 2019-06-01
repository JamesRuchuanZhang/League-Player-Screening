import requests

def getSummonerID(ign):
    url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/"+ign+"?api_key=" + api)
    response = requests.get(url).json()
    return response['accountId']

def getMatchData(accountID):
    url = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+ accountID + "?queue=400&endIndex=20&api_key=" + api)
    response = requests.get(url).json()
    return [x['gameId'] for x in response['matches']]
    #Short handing for making a list
    
def getMatchStats(matchData):
    values = []
    for match in matchData:
        url = "https://na1.api.riotgames.com/lol/match/v4/matches/"+ str(match) +"?api_key="+ api)
        response = requests.get(url).json()
        values.append(parseMatch(response))
    return response

def parseMatch(match):
    pass

ign = input("Please enter your ign: ")
api = input("Please enter your API Key: ")
accountID = getSummonerID(ign)
matchData = getMatchData(accountID)
matchStats = getMatchStats(matchData)
print(matchStats) 
