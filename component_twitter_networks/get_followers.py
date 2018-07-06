import os
import json
import tweepy
from get_tweepy_api import API
from config import id_or_screen_name,project_name,db_host,db_port,db_name,followerID_collection_name

from pymongo import MongoClient

# we are going to collect their followers
id_or_screen_name = id_or_screen_name.split(' ')

# connect to mongodb
client = MongoClient(db_host, db_port)

# specify the db name
db = client[db_name]

for name in id_or_screen_name:

    FOLLOWERS_CURSOR = tweepy.Cursor(API.followers_ids, id=name, count=5000).items()

    # get target user's followers
    while True:
        try:
            FOLLOWER = FOLLOWERS_CURSOR.next()
	    # save the followerID and user in the mongoDB
            result = db[followerID_collection_name].insert_one({"followerID":FOLLOWER, "user":name})
        except StopIteration:
            break

    print('Done for user: ', name)

print('Done for all!')


