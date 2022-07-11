import redis
import requests
import time
import tweepy
import operator

consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""
bearer_token = ""

auth = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, wait_on_rate_limit=True)
redis = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)




def get_match(name, tag):
    try:    
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}
        url = f"https://api.henrikdev.xyz/valorant/v3/matches/na/{name}/{tag}"
        request = requests.get(url, headers=headers)
        r = request.json()
        # time.sleep(0.5)
        print(r['data'][0]['metadata']['matchid'])
        return r['data'][0]['metadata']['matchid']
    except Exception as e:
        print(r)  


def get_matchv2(puuid):
    try:
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}
        url = f"https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/na/{puuid}"
        request = requests.get(url, headers=headers)
        r = request.json()
        return r['data'][0]['metadata']['matchid']
    except Exception as e:
        print(r)  


def get_m(puuid):
    check_match_mvp_acsdict = {}
    red_mvp_acsdict = {}
    blue_mvp_acsdict = {}
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}
    url = f"https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/na/{puuid}"
    request = requests.get(url, headers=headers)
    r = request.json()
    compList = []
    for i in r['data']:
        if i['metadata']['mode'] == 'Competitive':
            compList.append(i['metadata']['matchid'])
    if len(compList) == 0:
       game_status = 'N/A'
       duo = 'N/A'
       kills = 'N/A'
       deaths = 'N/A'
       assists = 'N/A'
       round_status = 'N/A'
       agent = 'N/A'
       map = 'N/A'
       mvp = 'N/A'
       acs = 'N/A'
       return game_status, duo, kills, deaths, assists, round_status, agent, map, mvp, acs
    url2 = f"https://api.henrikdev.xyz/valorant/v2/match/{compList[0]}"
    request2 = requests.get(url2, headers=headers)
    r2 = request2.json()
    players = r2['data']['players']['all_players']
    for p in players:
        if p['puuid'] == puuid:
            pteam = p['team'].lower()
            agent = p['character']
            party = p['party_id']

            acs = p['stats']['score'] / r2['data']['metadata']['rounds_played']
            kills = p['stats']['kills']
            deaths = p['stats']['deaths']
            assists = p['stats']['assists']
            
            if r2['data']['teams']['red']['has_won'] == True and pteam == 'red':
                game_status = 'Won'
                round_status = f"{r2['data']['teams']['red']['rounds_won']}-{r2['data']['teams']['red']['rounds_lost']}"
            elif r2['data']['teams']['red']['has_won'] == True and pteam == 'blue':
                game_status = 'Lost'
                round_status = f"{r2['data']['teams']['red']['rounds_lost']}-{r2['data']['teams']['red']['rounds_won']}"
            
            if r2['data']['teams']['blue']['has_won'] == True and pteam == 'blue':
                game_status = 'Won'
                round_status = f"{r2['data']['teams']['blue']['rounds_won']}-{r2['data']['teams']['blue']['rounds_lost']}"
            elif r2['data']['teams']['blue']['has_won'] == True and pteam == 'red':
                game_status = 'Lost'
                round_status = f"{r2['data']['teams']['blue']['rounds_lost']}-{r2['data']['teams']['blue']['rounds_won']}"

            if r2['data']['teams']['blue']['has_won'] == False and r2['data']['teams']['red']['has_won'] == False:
                game_status = 'Draw'
                round_status = f"{r2['data']['teams']['red']['rounds_won']}-{r2['data']['teams']['red']['rounds_lost']}"

            duoList = []
            for pp in players:
                if pp['party_id'] == party and pp['puuid'] != puuid:
                    duoList.append(pp['name'])
                    duo = duoList[-1]

        check_match_mvp_acsdict[p['puuid']] = p['stats']['score']
    

    if len(duoList) == 0:
        duo = 'Solo'
    
    check_match_mvp = (max(check_match_mvp_acsdict.items(), key=operator.itemgetter(1))[0])
    if check_match_mvp == puuid:
       mvp = '🏅 Match MVP'
    elif pteam == 'red':
        for red_players in r2['data']['players']['red']:
            red_mvp_acsdict[red_players['puuid']] = red_players['stats']['score']
        check_team_mvp = (max(red_mvp_acsdict.items(), key=operator.itemgetter(1))[0])
        if check_team_mvp == puuid:
            mvp = '🥇 Team MVP'
        else:
            mvp = None   
    elif pteam == 'blue':
        for blue_players in r2['data']['players']['blue']:
            blue_mvp_acsdict[blue_players['puuid']] = blue_players['stats']['score']
        check_team_mvp = (max(blue_mvp_acsdict.items(), key=operator.itemgetter(1))[0])
        if check_team_mvp == puuid:
            mvp = '🥇 Team MVP'
        else:
            mvp = None
    else:
        mvp = None

    map = r2['data']['metadata']['map']
    
    if mvp is None:
        mvp = ''

    return game_status, duo, kills, deaths, assists, round_status, agent, map, mvp, round(acs)


while True:
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0'}
        request = requests.get('https://dgxfkpkb4zk5c.cloudfront.net/leaderboards/affinity/NA/queue/competitive/act/67e373c7-48f7-b422-641b-079ace30b427?startIndex=9&size=10', headers=headers)
        r = request.json()
        players = r['players']   
        for p in r['players'][::-1]:
            if 'puuid' in p and p['puuid'] != "":
                puuid = p['puuid']
                gameName = p['gameName']
                tagLine = p['tagLine']
                rankedRating = p['rankedRating']
                leaderboardRank = p['leaderboardRank']
                numberOfWins = p['numberOfWins']

                player = redis.hget(f"player#{puuid}", 'puuid')
                last_match = get_matchv2(puuid)
                game_status, duo, kills, deaths, assists, round_status, agent, map, mvp, acs = get_m(puuid)

                if game_status == 'Won':
                   status_emoji = f'🟢 Won last match {round_status}'
                elif game_status == 'Lost':
                    status_emoji = f'🔴 Lost last match {round_status}'
                else:
                    status_emoji = f'⚪️ Draw last match {round_status}'

                kda = f"📊 K/D/A: {kills}/{deaths}/{assists}"


                if duo == 'Solo':
                    duo_status = '👤 Solo'
                else:
                    duo_status = f'👥 Duo with {duo}'

                twitterName = redis.hget(f"player#{puuid}", 'twitter')
                if twitterName is None:
                    gameName1 = gameName
                elif twitterName != 'empty':
                    gameName1 = f"@{twitterName}" 
                else:
                    gameName1 = gameName

                if player is None:
                    tweetText = f"""⬆️ {gameName1} is now on Rank #{leaderboardRank} with {rankedRating} RR.

{status_emoji}
🌎 {map}
🦹‍♂️ {agent}
{kda}
📈 ACS: {acs}
{mvp}
{duo_status}                   
"""
                    NoneTweet = auth.create_tweet(text=tweetText)
                    # print(f"{tweetText} --------------------")

                    redis.hset(f"player#{puuid}", 'puuid', puuid)
                    redis.hset(f"player#{puuid}", 'twitter', 'empty')
                    redis.hset(f"player#{puuid}", 'lastTweet', NoneTweet[0]['id'])
                else:
                    rank = redis.hget(f"player#{puuid}", 'leaderboardRank')
                    rr = redis.hget(f"player#{puuid}", 'rankedRating')
                    last_match2 = redis.hget(f"player#{puuid}", 'lastMatch')
                    if int(rank) != int(leaderboardRank) and int(rr) != int(rankedRating) and last_match2 != last_match:
                        if int(rank) > int(leaderboardRank):
                            statusEmoji = '⬆️'
                        elif int(rank) < int(leaderboardRank):
                            statusEmoji = '⬇️'
                        qt = redis.hget(f"player#{puuid}", 'lastTweet')
                        tweetText = f"""{statusEmoji} {gameName1} is now on Rank #{leaderboardRank} with {rankedRating} RR.

{status_emoji}
🌎 {map}
🦹‍♂️ {agent}
{kda}
📈 ACS: {acs}
{mvp}
{duo_status}                   
"""
                        NewTweet = auth.create_tweet(text=tweetText, quote_tweet_id=int(qt))
                        redis.hset(f"player#{puuid}", 'lastTweet', NewTweet[0]['id'])
                        # print(tweetText)
                    else:
                        pass
                print(leaderboardRank)
                redis.hset(f"player#{puuid}", 'leaderboardRank', leaderboardRank)
                redis.hset(f"player#{puuid}", 'rankedRating', rankedRating)
                redis.hset(f"player#{puuid}", 'numberOfWins', numberOfWins)
                redis.hset(f"player#{puuid}", 'gameName', gameName)
                redis.hset(f"player#{puuid}", 'tagLine', tagLine)
                redis.hset(f"player#{puuid}", 'lastMatch', last_match)
                time.sleep(10)
