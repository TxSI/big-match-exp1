from db import DB
from userProfile import UserProfile
import config
import os
import networkx as nx


class FollowershipNetwork:
    def __init__(self):

        self.GRAPH = nx.DiGraph()
        self.PROJECT_DIRECTORY = 'output/project/' + config.project_name

        self.NETWORK_FILE_NAME = self.PROJECT_DIRECTORY + '/followership_network_ristrict.gexf'

        if not os.path.exists(self.PROJECT_DIRECTORY):
            os.makedirs(self.PROJECT_DIRECTORY)

        self.follower_list = []
        self.followership_dict = {}
        self.followingship_dict = {}

    def addConnection(self, user_from, user_to):
        if not self.GRAPH.has_edge(user_from, user_to):
            # if connection does not yet exists, create one
            self.GRAPH.add_edge(user_from, user_to, weight=0)
        # add +1 to connection weight
        self.GRAPH[user_from][user_to]['weight'] += 1


    def getFollowership(self):
        if not self.followership_dict:
            self.buildFollowership()

        return self.followership_dict

    def buildFollowership(self):
        # get the follower list
        user_profile = UserProfile()
        user_profile.getUserList()
        self.follower_list = user_profile.user_list 

        #convert to set to speed up index
        follower_set = set(self.follower_list)
        print(len(follower_set))

        db = DB()

        
        result = db.db[config.followeroffollower_collection_name].find()

        for doc in result:
            if doc['user_id'] not in follower_set:
                continue
            if doc['user_id'] not in self.followership_dict:
                self.followership_dict[doc['user_id']] = []
            if doc['followerID'] not in follower_set:
                # this follower is not in the target comnunitiy, 
                # which is the followers of the target users defined in config.py
                continue

            self.followership_dict[doc['user_id']].append(doc['followerID'])

        db.close()


    def getFollowingship(self):
        if not self.followingship_dict:
            self.buildFollowingship()
        return self.followingship_dict

    def buildFollowingship(self):

        if not self.followership_dict:
            self.getFollowership()

        for user, followers in self.followership_dict.items():
            for follower in followers:
                if follower not in self.followingship_dict:
                    self.followingship_dict[follower] = []

                self.followingship_dict[follower].append(user)


    def buldNetwork(self):
        if not self.followership_dict:
            self.buildFollowership()


        db = DB()

        id_name_dict = {}
        result = db.db[config.id_name_collection_name].find({"id":{"$in":self.follower_list}},{'id':1, 'name':1, 'screen_name':1})
        for doc in result:
            id_name_dict[doc['id']] = (doc['name'],doc['screen_name'])

        db.close()

        for user, followers in self.followership_dict.items():
            for follower in followers:
                #self.addConnection(follower,user)
                self.addConnection(id_name_dict[follower][1],id_name_dict[user][1])

    def saveNetwork(self):
        nx.readwrite.gexf.write_gexf(self.GRAPH, self.NETWORK_FILE_NAME, encoding='utf-8', version='1.2draft')
