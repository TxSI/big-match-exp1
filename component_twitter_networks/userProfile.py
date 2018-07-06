from db import DB
import config
from gensim.corpora import Dictionary
from multiprocessing import Process
from helper import chunkFun
import psutil

class UserProfile:
    def __init__(self, user_list = []):
        self.threshold_num = config.threshold_num
        self.lan = config.lan


        self.user_list = user_list


    def getUserList(self):
        if not self.user_list:
            """
            find user list from mongodb who has at least 'self.threshold_num' 
            of tweets in language 'self.lan'
            """
            db = DB()

            result = db.db[config.id_name_collection_name].find({'tweet_lan_stats.en':{'$gte':int(self.threshold_num)}}, {'_id':0,'id':1})
            self.user_list = [x['id'] for x in result]
            print(len(self.user_list))
            db.close()

    def buildCorpProfile(self, user_list = []):
        """
        build corp profile on given users or on all users meet the requirement defined in config.py
        """
        if not user_list:
            if not self.user_list:
                print('user list is empty! will run getUserList')
                self.getUserList()
                print('get the user list')

            user_list = self.user_list

        if not user_list:
            print('user list is still empty!')
            return

        #self.doBuildCorpProfile(self.user_list)


        # number of CPU cores in the system
        cores = psutil.cpu_count(logical = False)

        # logical cpu include hyperthread in each cores
        threads = psutil.cpu_count(logical = True)

        # just in case, need to save another 1/2 number of threads for mongodb as we are running
        # mongodb locally. An config can be added in future if we can run mongodb on remote server
        if threads < 2:
            threads = 2

        # will make use of all the logical cpus
        all_threads = threads

        # thread_n is import from config.py, user can specifiy how many thread to use
        thread_n = int(config.thread_n)

        # because mongodb is running locally, and it will create a thread for each connection,
        # here we set the thread number to no larger than all_threads/2
        if thread_n > ( int(all_threads/2) ) or thread_n <= 0:
            thread_n = int(all_threads/2)

        if thread_n >= len(user_list):
            thread_n = len(user_list)

        print('{} threads out of {} will be used'.format(thread_n, all_threads))

        process_list = []

        # split the list of followers(userIDs) into chunks and start a process to deal with each chunk
        for i in range(thread_n):
            c = chunkFun(user_list, thread_n, i)
            p = Process(target=self.doBuildCorpProfile, args=(c,i,))
            p.start()
            process_list.append(p)

        for p in process_list:
            p.join()

        print('All Done!')





    def doBuildCorpProfile(self, user_list, worker_id):
        """
        split each tweet text and build a corpora for the user using his/all clean tweet text
        """
        count = 0
        total = len(user_list)

        db = DB()

        for user_id in user_list:
            result = db.db[config.tweet_collection_name].find({'user.id':user_id, 'tweet_lan':self.lan},{'_id':0,'tweet_clean':1})

            profile_corpora = []

            for doc in result:
                profile_corpora += doc['tweet_clean'].split()
            
            result = db.db[config.id_name_collection_name].update_one({'id':user_id},{'$set':{'corp_profile':profile_corpora}})
            
            count += 1
            print('process user: {}, {}/{} on worker {}'.format(user_id, count, total, worker_id))

        db.close()

    def getCorpProfile(self, user_list = []):
        """
        return the corp profile for a given user list or the list of users who meet the requirement defined in config.py
        """
        if not user_list:
            if not self.user_list:
                print('user list is empty! will run getUserList')
                self.getUserList()
                print('get the user list')

            user_list = self.user_list

        if not user_list:
            print('user list is still empty!')
            return []
        else:
            corp_profile = self.doGetCorpProfile(user_list)
            return corp_profile

    def doGetCorpProfile(self, user_list):
        """
        retrive the corp profile from mongodb in 'id_name' collection
        """
        user_corp_profile = {}

        db = DB()

        for user_id in user_list:
            result = db.db[config.id_name_collection_name].find_one({'id':user_id},{'corp_profile':1, 'screen_name':1})

            #user_corp_profile.append(result['corp_profile'])
            user_corp_profile[result['screen_name']] = result['corp_profile']

        db.close()
        return user_corp_profile
