import os
import json
import tweepy
import datetime
from get_tweepy_api import API
from config import id_or_screen_name,project_name,db_host,db_port,db_name,followerID_collection_name,id_name_collection_name,tweet_collection_name,tweet_num,log_collection_name
from pymongo import MongoClient



# connect to localhost mongodb
client = MongoClient(db_host, db_port)

# set the database name
db = client[db_name]

# because there are some followers following more than one target users
# need to get the uniq followers 
uniq_followers = db[followerID_collection_name].distinct("followerID")

uniq_len = len(uniq_followers)



# followers already collected
result = db[id_name_collection_name].find({},{"_id":0,"id":1})
done_followers = []
for doc in result:
    done_followers.append(doc["id"])

# update the uniq_followers list
uniq_followers = [x for x in list(uniq_followers) if x not in done_followers]

# if this is the continue collection recovered from the previous collection process
if len(uniq_followers) != uniq_len:
    # delete the last id name mapping and will re-collect from this one 
    result = db[id_name_collection_name].delete_one({"id":done_followers[-1]})
    # delete the last one's tweets and will re-collect from this one
    result = db[tweet_collection_name].delete_many({"user.id":done_followers[-1]})
    # insert the last one into the begining of the new uniq_followers list
    uniq_followers.insert(0, done_followers[-1])

# iterate over followers
# get number of tweet_num latest tweets from each of those

id_or_screen_name = id_or_screen_name.split(' ')

for follower_id in uniq_followers:
    cursor = tweepy.Cursor(API.user_timeline, user_id=follower_id, count=tweet_num).items(tweet_num)
    # build the id:name map at the same time
    k = 0
    try:
        for item in cursor:
            result = db[tweet_collection_name].insert_one(item._json)
            # only need to insert onece for the name and id mapping
            if k == 0:
                result = db[id_name_collection_name].insert_one({"id":item._json['user']['id'],"name":item._json['user']['name'],"screen_name":item._json['user']['screen_name']})
                k = 1
            
    except tweepy.TweepError as error:
        ERROR_STRING = 'Tweepy error: {}. Failed to retrieve tweets of follower {}'.format(error.reason, follower_id)
        #print(ERROR_STRING)
        result = db[log_collection_name].insert_one({"time":datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"), "msg":ERROR_STRING})
        continue
    except StopIteration:
        #print("StopIteration")
        EXP_STRING = 'StopIteration'
        result = db[log_collection_name].insert_one({"time":datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"), "msg":EXP_STRING})
        break
    except:
        #print("Unkown error")
        UNKNOWNERR_STRING = 'Unknown error while processing follower {}'.format(follower_id)
        result = db[log_collection_name].insert_one({"time":datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S"), "msg":UNKNOWNERR_STRING})
        continue

