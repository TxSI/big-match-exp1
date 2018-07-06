from db import DB
import config
from userProfile import UserProfile
from gensim.corpora import Dictionary
from gensim.models.ldamulticore import LdaMulticore
from sklearn.metrics import pairwise_distances
import numpy as np

class LdaRecsys:
    def __init__(self):
        self.user_corp = {}
        self.corp_dict = {}
        self.corp_bow = []
        self.user_profile = UserProfile()
        self.user_profile.getUserList()
        self.user_list = self.user_profile.user_list
        self.cosine_distance_dict = {}
        self.lda_vect_dict = {}

    def loadCorpDict(self, user_list = []):
        return

    def saveCorpDict(self):
        return

    def buildCorpDict(self, user_list = [], no_blow_doc = 10, no_above_doc = 0.5):

        if not user_list:
            if not self.user_list:
                print('user list is empty! will run getUserList')
                self.user_profile.getUserList()
                self.user_list = self.user_profile.user_list
                print('get the user list')

            user_list = self.user_list

        if not user_list:
            print('user list is still empty!')
            return []

        self.user_corp = self.user_profile.getCorpProfile(self.user_list)

        self.corp_dict = Dictionary([corp for corp in list(self.user_corp.values())])
        
        # Keep tokens which are contained in at least no_below documents
        # Keep tokens which are contained in no more than no_above documents
        # (fraction of total corpus size, not an absolute number)
        self.corp_dict.filter_extremes(no_below = no_blow_doc, no_above = no_above_doc)
        self.corp_dict.compactify()


    def buildCorpBow(self):
        if not self.user_corp or not self.corp_dict:
            self.buildCorpDict()
        
        self.corp_bow = {}
        for user,corp in self.user_corp.items():
            self.corp_bow[user] = self.corp_dict.doc2bow(corp)

    def saveCorpBow(self):
        return
    def loadCorpBow(self):
        return
    def trainLDA(self, topics_num, iter_num = 50):
        # reset the cosine_distance_dict in every training
        self.cosine_distance_dict = {}

        self.topics_num = topics_num
        corp_bow = [bow for bow in list(self.corp_bow.values())]
        self.lda = LdaMulticore(corp_bow,
                                num_topics = topics_num,
                                id2word = self.corp_dict,
                                iterations = iter_num,
                                workers = 4) 

    def runLDA(self, user_name):
        if user_name in self.corp_bow:
            user_bow = self.corp_bow[user_name]
        else:
            print('no such user! Please check the screen name')
            return

        user_lda = self.lda[user_bow]

        return user_lda

    def buildLdaVect(self):

        for user, bow in self.corp_bow.items():
            vect = np.zeros(self.topics_num)
            user_lda = self.lda[bow]

            for i in user_lda:
                vect[i[0]] = i[1]

            self.lda_vect_dict[user] = vect

    def ldaCosineDistance(self, user_name):
        
        if not self.lda_vect_dict:
            self.buildLdaVect()
            
        if user_name not in self.lda_vect_dict:
            print('no such user')
            return

        cosine_distance_dict = {}
        user_vect = self.lda_vect_dict[user_name]

        for user, lda_vect in self.lda_vect_dict.items():
            cosine_distance = pairwise_distances(np.array(user_vect).reshape(1,-1),np.array(lda_vect).reshape(1,-1), metric='cosine')[0][0]
            cosine_distance_dict[user] = cosine_distance

        
        self.cosine_distance_dict[user_name] = cosine_distance_dict


    def makeRecommendation(self, user_name, topn_recommendation = 10):

        if user_name not in self.cosine_distance_dict:
            self.ldaCosineDistance(user_name)
            
        user_recommendations = self.cosine_distance_dict[user_name]

        n = 0
        for recommendation, cosine_distance in sorted(user_recommendations.items(), key=lambda x:x[1]):
            print((recommendation, cosine_distance))
            n += 1
            if n == topn_recommendation:
                break

        return user_recommendations

    def showTopic(self, topic_number, topn_word = 5):
        """
        topic_numer:
            which topic to show
        topn_word:
            show top n words in this topic
        """
                                                
        print(u'{:20} {}'.format(u'term', u'frequency') + u'\n')

        for term, frequency in self.lda.show_topic(topic_number, topn_word):
            print(u'{:20} {:.3f}'.format(term, round(frequency, 3)))


    def showUserTopic(self, user_name, topn_word = 10):
        if user_name not in self.corp_bow:
            print('no such user! please check the screen name')
            return

        user_bow = self.corp_bow[user_name]

        user_lda = self.lda[user_bow]

        user_lda = sorted(user_lda, key=lambda x:-x[1])

        for topic_number, freq in user_lda:

            print('topic number {}  {}'.format(topic_number, freq))
            print('|____')
            self.showTopic(topic_number,topn_word)
            print('\n')
