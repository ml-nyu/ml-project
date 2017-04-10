import tweepy
import random
import json
consumer_key = 'h0rkGHiHfLWXcDC2JpLwFsOM1'
consumer_secret = '2LwMfoJdrP7wwmXrla1ntPHKTwXkAuEp9Hy1MubPhqXhQqy2hb'

access_token = '783020130842345472-gmnBzJ4FYy9o6tvaVZbFiD1f315rHy2'
access_token_secret = 'w08lwDNAlzdnBnWT1RxECCJWYKliHsSEEiqujuOi1CUDQ'

# nonbots = ['MesutOzil1088','LudovicoEinaud','Cristiano','theamitsinghal','MrDtAFC','goonerclaude','Arsenal_Trooper','Yanni','imVkohli','Alex_OxChambo','The_AnuMalik','SrBachchan','kobebryant','KingJames','ABdeVilliers17','coldplay','cpulisic_10','rioferdy5','themichaelowen','TheNotoriousMMA','FloydMayweather','RafaelNadal','RaviShastriOfc','rogerfederer','sachin_rt','travisk','satyanadella','JeffBezos','jeffweiner','Werner','DjokerNole','narendramodi','prattprattpratt','SamuelLJackson','JKCorden','realDonaldTrump','TheYoungTurks','BarackObama','MichelleObama','SHAQ','mertesacker','ThierryHenry','GeorgeHWBush','Pele','SethMacFarlane','neiltyson','EmmaWatson','Y_Strahovski','GordonRamsay','piersmorgan']

bots = ['tribunenow','AdvRecovRes','FLrecoverygroup','TinyAdv','riverlevel_1867','holidaybot4000','iMamaAfrica','googlebot27','AuthorShana','WPmuti','WalesBuzz','MythologyBot','empathydeck','Madenza_','ocatkitty','nmstereo','haikuthegibson','janusnode','WWE_Network_Bot','SEMNewsBot','clicktotweet','GetRockbot','DaftPunkRockbot','FashionBot','gamebotCanada','__oort__','WYR_bot','selfcare_bot','HeyDiddleBot','conwaylifebot','selfportraitexe','GraciousKY','BadAllyBot','orindacrazynews','__brobama__','OpiLeaks','usethewhat','NoBotsSky','FakeDispatchBot','floweys_advice','theroboreporter','HeyDiddleBot','booktitlebot','tinycarebot','_PPBot','EnnardBenedict','NaMoGenBo','bot_dot_d','conceptsbot','fartb0t']

accounts = ['RuPaulBOTS','ChatBotsLife', 'FundiBots','BotsAndBrains', 'AweSoftware','BillGates', 'drknglnaidu', 'Oprah', 'Twitter', 'bhogleharsha', 'LeoDiCaprio', 'SushmaSwaraj', 'michiokaku', 'gussand', 'kaushik_cb']
values = [1,1,1,1,1,0,0,0,0,0,0,0,0,0,0]

c = list(zip(accounts, values))
random.shuffle(c)

accounts, values = zip(*c)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# make initial request for most recent tweets (200 is the maximum allowed count)

def generate_tweets(accounts):
    alltweets = []
    for screennames in accounts:
        #print(screennames)
        new_tweets = api.user_timeline(screen_name=screennames, count=5)
        for tweet in new_tweets:
            alltweets.append(tweet._json)
    return alltweets


def generate_features_json(accounts, classification):
    rows = []
    for i, user in enumerate(accounts):
        print(user)
        res = api.get_user(screen_name=user)
        status = res.status
        json_str = status._json
        rows.append([
            res.default_profile,
            res.favourites_count,
            res.followers_count,
            res.friends_count,
            res.statuses_count,
            res.verified,
            json_str['retweet_count'],
            classification[i]
        ])
    return rows

def generate_lookup_json(accounts, classification):
    rows = []
    for i, user in enumerate(accounts):
        print(user)
        res = api.get_user(screen_name=user)
        status = res.status
        json_str = status._json
        rows.append([res.id,
        res.id_str,
        res.screen_name.encode("utf-8",'ignore'),
        res.location,
        res.description.encode("utf-8",'ignore'),
        res.url,
        res.followers_count,
        res.friends_count,
        res.listed_count,
        res.created_at,
        res.favourites_count,
        res.verified,
        res.statuses_count,
        json_str.encode("utf-8",'ignore'),
        res.lang,
        res.default_profile,
        res.default_profile_image,
        res.name,
        res.has_extended_profile,
        classification[i]
        ])
    return rows

def write_to_json_file(filename, rows):
    with open(filename, 'w') as outfile:
        json.dump(rows, outfile)

rows = generate_features_json(accounts, values)
write_to_json_file('newnonbotslookup.json',rows)

# CSV WRITER
# import csv
# with open('bots.csv', 'w') as output_file:
#     file_writer = csv.writer(output_file, delimiter='|')
#     file_writer.writerows(rows)
#
# with open('nonbots.txt', 'w') as output_file:
#     for user in rows:
#         print(user)
#         output_file.write(helper(user))

