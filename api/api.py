 # import time
from flask import Flask, request
# import cassiopeia as cass
# from cassiopeia import Summoner, Match, Champion, Map
# from cassiopeia.data import Season, Queue
# import random
from collections import Counter
# import datetime
# import sys
from riotwatcher import LolWatcher, ApiError

#constants
CHAMP_DICT = {266: 'Aatrox', 103: 'Ahri', 84: 'Akali', 12: 'Alistar', 32: 'Amumu', 34: 'Anivia', 1: 'Annie', 523: 'Aphelios', 22: 'Ashe', 136: 'Aurelion Sol', 268: 'Azir', 432: 'Bard', 53: 'Blitzcrank', 63: 'Brand', 201: 'Braum', 51: 'Caitlyn', 164: 'Camille', 69: 'Cassiopeia', 31: "Cho'Gath", 42: 'Corki', 122: 'Darius', 131: 'Diana', 119: 'Draven', 36: 'Dr. Mundo', 245: 'Ekko', 60: 'Elise', 28: 'Evelynn', 81: 'Ezreal', 9: 'Fiddlesticks', 114: 'Fiora', 105: 'Fizz', 3: 'Galio', 41: 'Gangplank', 86: 'Garen', 150: 'Gnar', 79: 'Gragas', 104: 'Graves', 120: 'Hecarim', 74: 'Heimerdinger', 420: 'Illaoi', 39: 'Irelia', 427: 'Ivern', 40: 'Janna', 59: 'Jarvan IV', 24: 'Jax', 126: 'Jayce', 202: 'Jhin', 222: 'Jinx', 145: "Kai'Sa", 429: 'Kalista', 43: 'Karma', 30: 'Karthus', 38: 'Kassadin', 55: 'Katarina', 10: 'Kayle', 141: 'Kayn', 85: 'Kennen', 121: "Kha'Zix", 203: 'Kindred', 240: 'Kled', 96: "Kog'Maw", 7: 'LeBlanc', 64: 'Lee Sin', 89: 'Leona', 127: 'Lissandra', 236: 'Lucian', 117: 'Lulu', 99: 'Lux', 54: 'Malphite', 90: 'Malzahar', 57: 'Maokai', 11: 'Master Yi', 21: 'Miss Fortune', 62: 'Wukong', 82: 'Mordekaiser', 25: 'Morgana', 267: 'Nami', 75: 'Nasus', 111: 'Nautilus', 518: 'Neeko', 76: 'Nidalee', 56: 'Nocturne', 20: 'Nunu & Willump', 2: 'Olaf', 61: 'Orianna', 516: 'Ornn', 80: 'Pantheon', 78: 'Poppy', 555: 'Pyke', 246: 'Qiyana', 133: 'Quinn', 497: 'Rakan', 33: 'Rammus', 421: "Rek'Sai", 58: 'Renekton', 107: 'Rengar', 92: 'Riven', 68: 'Rumble', 13: 'Ryze', 113: 'Sejuani', 235: 'Senna', 875: 'Sett', 35: 'Shaco', 98: 'Shen', 102: 'Shyvana', 27: 'Singed', 14: 'Sion', 15: 'Sivir', 72: 'Skarner', 37: 'Sona', 16: 'Soraka', 50: 'Swain', 517: 'Sylas', 134: 'Syndra', 223: 'Tahm Kench', 163: 'Taliyah', 91: 'Talon', 44: 'Taric', 17: 'Teemo', 412: 'Thresh', 18: 'Tristana', 48: 'Trundle', 23: 'Tryndamere', 4: 'Twisted Fate', 29: 'Twitch', 77: 'Udyr', 6: 'Urgot', 110: 'Varus', 67: 'Vayne', 45: 'Veigar', 161: "Vel'Koz", 254: 'Vi', 112: 'Viktor', 8: 'Vladimir', 106: 'Volibear', 19: 'Warwick', 498: 'Xayah', 101: 'Xerath', 5: 'Xin Zhao', 157: 'Yasuo', 83: 'Yorick', 350: 'Yuumi', 154: 'Zac', 238: 'Zed', 115: 'Ziggs', 26: 'Zilean', 142: 'Zoe', 143: 'Zyra'}
CHAMP_FLIPPED_DICT = {value: key for key, value in CHAMP_DICT.items()}


API_KEY = "RGAPI-1cbcef94-ad83-45b0-aeaf-04402a0e1158"

lol_watcher = LolWatcher(API_KEY)
my_region = 'na1'

app = Flask(__name__)

@app.route('/info', methods=['GET'])
def get_summoner_info():
    app.logger.info("HERE" + str(request.args))
    try:

        # #INPUT
        name = request.args.get('sn', None)
        me = lol_watcher.summoner.by_name(my_region, name)

        match_histories = [lol_watcher.match.matchlist_by_account(
                        region=my_region,
                        encrypted_account_id=me['accountId'],
                        season=[13],
                        begin_index=b,
                        end_index=b+100
                        ) for b in range(0, 1000, 100)]
        matches = [i for subl in [mh['matches'] for mh in match_histories] for i in subl]
        played_champs = Counter()
        for match in matches:
            champid = match['champion']
            played_champs[champid] += 1
        print(played_champs)
        champlist = [(champid, count, CHAMP_DICT[champid]) for (champid, count) in played_champs.most_common(15) if count >= 25]

        return {'champlist' : champlist, 'bad_request' : False}
    except:
        return {'bad_request' : True}

def get_info(me, my_region, matches, items):
    item_stamps = {}

    for match in matches[:15]:
        tl = lol_watcher.match.timeline_by_match(region=my_region, match_id=match['gameId'])
        print("h2")
        actmatch = lol_watcher.match.by_id(region=my_region, match_id=match['gameId'])
        print("h1")
        ids = actmatch['participantIdentities']
        my_id = ''
        for id in ids:
            if id['player']['accountId'] == me['accountId']:
                my_id = id['participantId']
        frames = tl['frames']
        for mframe in frames:
            for event in mframe['events']:
                if 'participantId' in event and event['participantId'] == my_id and event['type'] == 'ITEM_PURCHASED':
                    # print(mframe['participantFrames'])
                    try:
                        item = items[str(event['itemId'])]
                    except:
                        continue
                    #(item['gold']['base'] > 800
                    if 'Boots' in item['tags'] or (int(event['timestamp']) < 600000 and item['gold']['total'] > 800) or item['gold']['total'] > 1300:
                        if item['name'] in item_stamps:
                            item_stamps[item['name']].append(int(event['timestamp'])//1000)
                        else:
                            item_stamps[item['name']] = [int(event['timestamp'])//1000]
    print(item_stamps)
    return item_stamps


@app.route('/itemtl', methods=['GET'])
def get_item_timeline():
    app.logger.info("HERE2" + str(request.args))
    #http://static.developer.riotgames.com/docs/lol/queues.json
    # try:
    name = request.args.get('sn', None)
    champ = request.args.get('cid', None)
    me = lol_watcher.summoner.by_name(my_region, name)
    match_histories = [lol_watcher.match.matchlist_by_account(
                    region=my_region,
                    encrypted_account_id=me['accountId'],
                    queue=[440, 420, 400],
                    season=[13],
                    begin_index=b,
                    end_index=b+100,
                    champion=[champ]
                    ) for b in range(0, 1000, 100)]
    matches = [i for subl in [mh['matches'] for mh in match_histories] for i in subl]

    items = lol_watcher.data_dragon.items(version="10.11.1")['data']

    chally = lol_watcher.league.challenger_by_queue(region=my_region, queue="RANKED_SOLO_5x5")
    cme = ''
    chall_matches = []
    for entry in chally['entries']:
        try:
            bme = lol_watcher.summoner.by_id(region=my_region, encrypted_summoner_id=entry['summonerId'])
            match_histories = [lol_watcher.match.matchlist_by_account(
                            region=my_region,
                            encrypted_account_id=bme['accountId'],
                            queue=[440, 420, 400],
                            season=[13],
                            begin_index=b,
                            end_index=b+100,
                            champion=[champ]
                            ) for b in range(0, 1000, 100)]
            smatches = [i for subl in [mh['matches'] for mh in match_histories] for i in subl]
            if len(smatches) >= 10:
                chall_matches = smatches
                cme  = bme
                break
        except:
            print("this chally failed")
    print(len(chall_matches))
    item_stamps = get_info(me, my_region, matches, items)
    cis = get_info(cme, my_region, chall_matches, items)
    # print(chall_matches, cis, cks, cls)
    triples = []
    for key,value in item_stamps.items():
        if key in cis and len(value) >= 3 and len(cis[key]) >= 3:
            triples.append((sum(value)//len(value)/60, key, value, cis[key]))
    triples.sort(key=lambda x:x[0])
    return {
        "item" : triples,
        "bad_request" : False
    }
