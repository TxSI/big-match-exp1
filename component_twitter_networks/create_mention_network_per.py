#import ijson
import networkx as nx
from config import project_name,db_host,db_port,db_name,followerID_collection_name,id_name_collection_name,tweet_collection_name,project_target_name
#from config import project_target_name
from pymongo import MongoClient
import codecs
import bson
import os

PROJECT_DIRECTORY = 'output/project/' + project_name

if not os.path.exists(PROJECT_DIRECTORY):
    os.makedirs(PROJECT_DIRECTORY)


PER_ORG_FILE = PROJECT_DIRECTORY + '/per_org_manually_classification_new.csv'
NETWORK_FILE_NAME = PROJECT_DIRECTORY + '/mention_network_ristrict_per.gexf'

# connect to localhost mongodb
client = MongoClient(db_host, db_port)

# set the database name
db = client[db_name]

# extract the tweets from target user's follower
project_target_name = project_target_name.split(' ')

for i in project_target_name:
    print(i)

# find target user's follower IDs
target_followers = []
cursor = db[followerID_collection_name].find({"user":{"$in":project_target_name}})
for doc in cursor:
   target_followers.append(doc["followerID"])

target_followers = list(set(target_followers))
print(type(target_followers[0]))

# read the person or organisation classification result
# and the targe followers are those classified as 'per'
per_org = {}

target_followers = []

per_org_file = codecs.open(PER_ORG_FILE,'r','utf-8')

for line in per_org_file:
    lines = line.split()
    per_org[lines[1]] = lines[2]
    if lines[2] == 'per':
        target_followers.append(bson.int64.Int64(lines[1]))


print(lines[1])
print(lines[2])
print(type(target_followers[0]))

# retrive the id name mapping
result = db[id_name_collection_name].find({"id":{"$in":target_followers}},{"_id":0})

ID_NAME = {}
for doc in result:
    if doc['screen_name'] not in project_target_name:
        ID_NAME[doc['id']] = doc['screen_name']

GRAPH = nx.DiGraph()

def add_connection(user_from, user_to):
    if not GRAPH.has_edge(user_from, user_to):
        # if connection does not yet exists, create one
        GRAPH.add_edge(user_from, user_to, weight=0)
    # add +1 to connection weight
    GRAPH[user_from][user_to]['weight'] += 1


def is_in_follower_list(user_id):
    if user_id in ID_NAME:
        return True
    else:
        return False


cursor = db[tweet_collection_name].find({"user.id":{"$in":target_followers}},\
                     {\
                      "retweeted":1, "retweeted_status":1, "is_quote_status":1,\
                      "quoted_status":1,"entities":1, "_id":0, "user":1 \
                      } \
        )

for document in cursor:
    KEY = document["user"]["id"]

    tweeter_name = document["user"]["screen_name"]
    
    if tweeter_name in project_target_name:
        print('Skipping', KEY)
        continue
    

    # the list to save his/her mentioned names
    mentioned_name = []
        
    # bulid the mentioned name list
    #for TWEET in VALUE:
    TWEET = document
        # if it is a retweet, only add the connection to the owner of the original tweet
        # not the other ones mentioned in the tweet
    if 'retweeted_status' in TWEET:
        mentioned_name.append({"name":TWEET['retweeted_status']['user']['screen_name'],"id":TWEET['retweeted_status']['user']['id']})
    elif 'quoted_status' in TWEET:
        for MENTIONED in TWEET['entities']['user_mentions']:
            mentioned_name.append({"name":MENTIONED['screen_name'],"id":MENTIONED['id']})
        # if it is a quote, add the owner of the orignial tweet
        try:
            mentioned_name.append({"name":TWEET['quoted_status']['user']['screen_name'],"id":TWEET['quoted_status']['user']['id']})
        except:
            pass
    else:
        for MENTIONED in TWEET['entities']['user_mentions']:
            mentioned_name.append({"name":MENTIONED['screen_name'],"id":MENTIONED['id']})


    # add the connection betweetn the tweeter user and his/her mentioned names
    for name in mentioned_name:
        #print(name['name'])
        #print(name['id'])
        #print(tweeter_name)
        if name['name'].casefold() != tweeter_name.casefold() and is_in_follower_list(name['id']):
            add_connection(tweeter_name.lower(), name['name'].lower())
            


nx.readwrite.gexf.write_gexf(GRAPH, NETWORK_FILE_NAME, encoding='utf-8',
                             version='1.2draft')
