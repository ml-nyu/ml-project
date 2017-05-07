import tweepy
import json
import re
import math
import time
import collections
from time import sleep,mktime
import datetime
from datetime import timedelta
import pandas as pd
import numpy as np

consumer_key_arr = []
consumer_secret_arr = []

access_token_arr = []
access_token_secret_arr = []

apikeycount = 0
def get_tweepy_api():
    global apikeycount
    auth = tweepy.OAuthHandler(consumer_key_arr[apikeycount], consumer_secret_arr[apikeycount])
    auth.set_access_token(access_token_arr[apikeycount], access_token_secret_arr[apikeycount])
    apikeycount = (apikeycount+1)%len(consumer_key_arr)
    return tweepy.API(auth)

api = get_tweepy_api()

attributes = ['id','id_str','screen_name','location','description','url','followers_count','friends_count','listedcount','created_at','favourites_count','verified','statuses_count','lang','status','default_profile','default_profile_image','has_extended_profile','name','bot']

df = pd.read_csv('training_data_2_csv_UTF.csv', header=0,names=attributes,na_values='?')

#Uncomment below line to run on test data
# df = pd.read_csv('test_data_4_students.csv', header=0,names=attributes,na_values='?')

snames = np.array(df['screen_name'])

#Removing comma characters before screen_name
trimmer = lambda s: re.sub("^\"|\"$", "", s)
trimfunc = np.vectorize(trimmer)
snames = trimfunc(snames)

accounts = snames.tolist()
values = np.array(df['bot']).tolist()

# Default Information for suspended accounts
def get_dummy_account(screenname):
    return {'description': ''
            ,'followers': 0
            ,'friends': 0
            ,'name': ''
            ,'socialness': 0
            ,'listed_count': 0
            ,'favourites': 0
            ,'verified': 0
            ,'totaltweets': 0
            ,'default_profile': 0
            ,'default_profile_image': 0
            ,'location': 0
            ,'has_extended_profile': 0
            ,'avghashtags': 0
            ,'avglen': 0
            ,'avgurls': 0
            ,'isperiodic': 0
            ,'in_reply_to_status_id': 0
            ,'is_quote_status': 0
            ,'created_at': 0.0
            ,'active_ts': 0.0
            ,'retweet_count': 0
            ,'screenname': screenname}




unacquiredaccounts = {}
usertweets = collections.OrderedDict()

#
# Extracting the below features:
# screen_name
# followers
# friends
# socialness
# listed_count
# favourites
# verified
# totaltweets
# default_profile
# avghashtags
# avglen
# avgurls
# isperiodic
# tweets
# creationts
# has_extended_profile
# in_reply_to_status_id
# is_quote_status
# retweet_count
# created_at
# active_ts

def get_tweets(accounts,values):
    global api
    for idx, screennames in enumerate(accounts):
        print(idx,"     ",screennames)
        try:
            new_tweets = api.user_timeline(screen_name=screennames, count=200)
        except tweepy.RateLimitError as e:
            api = get_tweepy_api()
            print('KEY CHANGED at     ',idx,"     ",screennames)
            time.sleep(5)
            new_tweets = api.user_timeline(screen_name=screennames, count=200)
        except tweepy.TweepError as e:
            pass

        if not new_tweets:
            try:
                res = api.get_user(screen_name=screennames)
            except tweepy.RateLimitError as e:
                api = get_tweepy_api()
                print('KEY CHANGED at     ',idx,"     ",screennames)
                time.sleep(5)
                res = api.get_user(screen_name=screennames)
            except tweepy.TweepError as e:
                unacquiredaccounts[idx] = screennames
                # Since these accounts are suspended but we need to preserve order in test CSV
                usertweets[screennames] = get_dummy_account(screennames)
                continue

            usertweets[screennames] = {'description': res.description}
            usertweets[screennames] = {'followers': res.followers_count}
            usertweets[screennames] = {'friends': res.friends_count}
            usertweets[screennames] = {'name': res.name}
            if res.followers_count > 0:
                usertweets[screennames] = {'socialness': res.friends_count/float(res.followers_count)}
            else: usertweets[screennames] = {'socialness': 0}
            usertweets[screennames] = {'listed_count': res.listed_count}
            usertweets[screennames] = {'favourites': res.favourites_count}
            usertweets[screennames] = {'verified': 1 if res.verified == True else 0}
            usertweets[screennames] = {'totaltweets': res.statuses_count}
            usertweets[screennames] = {'default_profile': 1 if res.default_profile == True else 0}
            usertweets[screennames] = {'default_profile_image': 1 if res.default_profile_image == True else 0}
            usertweets[screennames] = {'location': res.location}
            usertweets[screennames] = {'has_extended_profile': 1 if res.has_extended_profile == True else 0}
            usertweets[screennames] = {'avghashtags': 0}
            usertweets[screennames] = {'avglen': 0}
            usertweets[screennames] = {'avgurls': 0}
            usertweets[screennames] = {'isperiodic': 0}
            usertweets[screennames] = {'in_reply_to_status_id': 0}
            usertweets[screennames] = {'is_quote_status': 0}
            #usertweets[screennames] = {'tweets': []}
            #usertweets[screennames] = {'creationts': []}
            usertweets[screennames] = {'created_at': res.created_at.timestamp()}
            usertweets[screennames] = {'active_ts': time.time() - res.created_at.timestamp()}
            usertweets[screennames] = {'retweet_count': []}
            continue

        inreplytostatusidcount = 0
        isquotestatuscount = 0
        hashtagcount = 0.0
        tweetlen = 0.0
        urls = 0.0
        isperiodic = 0
        #currentusertweets = []
        retweetcount = []
        #currentuserts = []
        diffts = -1234567890
        prevts = 0
        usertweets[screennames] = {'followers': 0}
        usertweets[screennames] = {'friends': 0}
        usertweets[screennames] = {'socialness': 0}
        usertweets[screennames] = {'listed_count': 0}
        usertweets[screennames] = {'favourites': 0}
        usertweets[screennames] = {'verified': 0}
        usertweets[screennames] = {'totaltweets': 0}
        usertweets[screennames] = {'default_profile': 0}
        usertweets[screennames] = {'avghashtags': 0}
        usertweets[screennames] = {'avglen': 0}
        usertweets[screennames] = {'avgurls': 0}
        usertweets[screennames] = {'isperiodic': 0}
        usertweets[screennames] = {'tweets': []}
        usertweets[screennames] = {'creationts': []}
        usertweets[screennames] = {'has_extended_profile': 0}

        for tweet in new_tweets:
            jsontweet = tweet._json
            tweettext = jsontweet['text']
            #currentusertweets.append(tweettext)
            retweetcount.append(jsontweet['retweet_count'])
            if jsontweet['in_reply_to_status_id'] is not None:
                inreplytostatusidcount = inreplytostatusidcount + 1
            if jsontweet['is_quote_status'] is True:
                isquotestatuscount = isquotestatuscount + 1
            usertweets[screennames]['description'] = jsontweet['user']['description']
            usertweets[screennames]['has_extended_profile'] = 1 if jsontweet['user']['has_extended_profile'] == True else 0
            usertweets[screennames]['created_at'] = get_ts_from_twitterdate(jsontweet['user']['created_at']).timestamp()
            usertweets[screennames]['followers'] = jsontweet['user']['followers_count']
            usertweets[screennames]['friends'] = jsontweet['user']['friends_count']
            usertweets[screennames]['listed_count'] = jsontweet['user']['listed_count']
            usertweets[screennames]['favourites'] = jsontweet['user']['favourites_count']
            usertweets[screennames]['verified'] = 1 if jsontweet['user']['verified'] == True else 0
            usertweets[screennames]['totaltweets'] = jsontweet['user']['statuses_count']
            usertweets[screennames]['default_profile'] = 1 if jsontweet['user']['default_profile'] == True else 0
            usertweets[screennames]['default_profile_image'] = 1 if jsontweet['user']['default_profile_image'] == True else 0
            usertweets[screennames]['location'] = jsontweet['user']['location']
            usertweets[screennames]['name'] = jsontweet['user']['name']
            if jsontweet['user']['followers_count'] > 0:
                usertweets[screennames]['socialness'] = float(jsontweet['user']['friends_count'])/jsontweet['user']['followers_count']
            if 'entities' in jsontweet and 'hashtags'in jsontweet['entities']:
                hashtagcount = hashtagcount + len(jsontweet['entities']['hashtags'])
            tweetlen = tweetlen + len(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweettext).split()))
            if 'entities' in jsontweet and 'urls' in jsontweet['entities']:
                urls = urls + len(jsontweet['entities']['urls'])
            ts = get_ts_from_twitterdate(jsontweet['created_at'])
            #currentuserts.append(ts.timestamp())
            if prevts != 0:
                td = ts - prevts
                diffts = td / timedelta(minutes=1)
                if math.fabs(prevdiffts - diffts) < 3:
                    isperiodic = 1
            prevts = ts
            prevdiffts = diffts

        if len(new_tweets) > 0:
            usertweets[screennames]['avghashtags'] = hashtagcount/ len(new_tweets)
            usertweets[screennames]['avglen'] = tweetlen/ len(new_tweets)
            usertweets[screennames]['avgurls'] = urls / len(new_tweets)
        usertweets[screennames]['isperiodic'] = isperiodic
        usertweets[screennames]['screenname'] = screennames
        #usertweets[screennames]['tweets'] = currentusertweets
        #usertweets[screennames]['creationts'] = currentuserts
        usertweets[screennames]['retweetcount'] = retweetcount
        usertweets[screennames]['in_reply_to_status_id'] = inreplytostatusidcount
        usertweets[screennames]['is_quote_status'] = isquotestatuscount
        usertweets[screennames]['bot'] = values[idx]

    return usertweets

def get_ts_from_twitterdate(str):
    return datetime.datetime.fromtimestamp(mktime(time.strptime(str,"%a %b %d %H:%M:%S +0000 %Y")))

def write_to_json_file(filename, rows):
    with open(filename, 'w') as outfile:
        json.dump(rows, outfile)

get_tweets(accounts,values)
write_to_json_file('twitter_features_training.json',usertweets)
print("There are ",len(unacquiredaccounts)," unacquired accounts. Details below.")
write_to_json_file('unacquired_accounts_training.json',unacquiredaccounts)
print('Length of Output File',len(usertweets))


