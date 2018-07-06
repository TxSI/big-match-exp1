import sys
import config 
from db import DB
from mention_network import mention_network
from followershipNetwork import FollowershipNetwork

db = DB()

user_id_name_dict = {}
user_name_id_dict = {}
result = db.db[config.id_name_collection_name].find({'tweet_lan_stats.en':{'$gte':int(config.threshold_num)}}, {'_id':0,'screen_name':1, 'id':1})

for doc in result:
    user_id_name_dict[doc['id']] = doc['screen_name'].lower()
    user_name_id_dict[doc['screen_name']] = doc['id']

print(len(user_id_name_dict))

db.close()

PROJECT_DIRECTORY = 'output/project/' + config.project_name

MENTION_NETWORK_FILE = PROJECT_DIRECTORY + '/mention_network_ristrict.gexf'


name = sys.argv[1].lower()

print(name)

mn = mention_network(MENTION_NETWORK_FILE, partition_resolution=0.85)
results = mn.get_recommendations(name)

print('mentions of mentions: {}'.format(len(results['direct'])))

followership_net = FollowershipNetwork()

followingship_dict = followership_net.getFollowingship()

jnkka_id = user_name_id_dict[name]

print('number of account that you are following and also following tampere3: {}'.format(len(followingship_dict[jnkka_id])))

jnkka = followingship_dict[jnkka_id]

g1 = []

for follower_id in jnkka:
    follower_name = user_id_name_dict[follower_id]
    if follower_name not in results['direct']:
        g1.append(follower_name)

print(g1)
print('number of account you are following and not mentioned: {}'.format(len(g1)))
