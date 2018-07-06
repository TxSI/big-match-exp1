from text import Text
import codecs
import config
from db import DB
from pymongo import MongoClient
import psutil
import os
from multiprocessing import Process
import datetime
from helper import chunkFun

class Tweets:

    def __init__(self):
        self.db_host = config.db_host
        self.db_name = config.db_name
        self.tweet_collection_name = config.tweet_collection_name
        self.followerID_collection_name = config.followerID_collection_name
        self.id_name_collection_name = config.id_name_collection_name
        self.breakpoint = config.breakpoint

        self.userIDs = []

        self.thread_n = config.thread_n

        # text class for text clean
        self.text = Text()


    def textCleanWorker(self, chunk, worker_ID):
        
        # by default, DB class will connect to the database defined in the config.py
        # if by any chance you want to use different database, use db.useDB('db_name')
        db = DB()

        count = 0
        total = len(chunk)

        for follower in chunk:
            print('process follower:{} on worker {}'.format(follower, worker_ID))
            count += 1
            
            # stats of the number of tweets for each lan
            tweet_lan_stats = {}

            try:
                result = db.db[self.tweet_collection_name].find({"user.id":follower},\
                                 {\
                                  "text":1, "created_at":1, "retweeted_status.text":1,\
                                  "quoted_status.text":1, "_id":1, "tweet_lan":1, "tweet_clean":1\
                                 } \
                    )

                totalresult = result.count()
                if totalresult ==  0:
                    print('Done for follower: {} (no tweets) {} out of {} on worker {}'.format(follower, count, total, worker_ID))
                    continue
            except:
                print('Exception occurred in finding user tweets!')
                db.close()
                return

            # number of tweets already done
            num_done = 1
            for doc in result:
                # chck if it is already done and if a breakpoint is turn on
                # if breakpoint is on, then ignor those already done,
                # otherwise, all the operation will start all over again 
                if 'tweet_lan' not in doc and 'tweet_clean' not in doc and self.breakpoint == 1:
                    print('done for this one {}/{} of follower: {}'.format(num_done, totalresult, follower))
                    num_done += 1
                    continue 
                
                tweet = doc['text']
                # use the objectId in mongodb to speed up the following update operation
                tweet_id = doc['_id']

                tweet = tweet.replace('\n', ' ')

                # it is a retweet, the text is the same with the orignial text in retweeted_status
                if tweet[0:2] != 'RT':
                    # if is a comment, then the orignial tweet text is also taken into account
                    if 'retweeted_status' in doc:
                        tweet = tweet + ' ' + doc['retweeted_status']['text'].replace('\n', ' ')
                    # if it is a reply, then the orignial tweet text is also taken into account
                    if 'quoted_status' in doc:
                        tweet = tweet + ' ' + doc['quoted_status']['text'].replace('\n', ' ')
             
                # clean the raw tweet text to get a clean text and detect the language also
                newtweet, lan = self.text.doClean(tweet)

                if lan in tweet_lan_stats:
                    tweet_lan_stats[lan] = tweet_lan_stats[lan] + 1
                else:
                    tweet_lan_stats[lan] = 1

                # convert datetime string to timestampt
                datetime_str = doc['created_at']
                datetime_timestamp = datetime.datetime.strptime(datetime_str, "%a %b %d %H:%M:%S %z %Y").timestamp()

                # update this collection with cleaned tweet and its language.
                # use the mongodb Objectid(_id) to speed up the operation
                try:
                    update = db.db[self.tweet_collection_name].update_one({'_id':tweet_id},
                            {'$set': {'tweet_lan':lan, 'tweet_clean':newtweet, 'created_at_timestamp':datetime_timestamp}}) 
                except:
                    print('Exception occurred in updating tweet!')
                    db.close()
                    return

            # update the id_name collection with the stats of the user
            try:
                update = db.db[self.id_name_collection_name].update_one({'id':follower},
                        {'$set': {'tweet_num':totalresult,'tweet_lan_num':len(tweet_lan_stats), 'tweet_lan_stats':tweet_lan_stats}}) 
            except:
                print('Exception occurred in updating tweet stats!')
                db.close()
                return

            print('num of lan: {}'.format(len(tweet_lan_stats)))
            print('Done for follower: {} {} out of {} on worker {}'.format(follower, count, total, worker_ID))


        # close the connection
        db.close()



    def getUserID(self):

        db = DB()

        # create index for 'user.id' in collection 'tweets', we are going to multithread process those tweets by chunks indexing by 'user.id'
        # API ref: http://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.create_index
        # it won't hurt to call this everytime as the API will check if the index is already created or not
        try:
            result = db.db[self.tweet_collection_name].create_index('user.id')
            print('Done for create index')
            # get all the tweet users
            uniq_followers = db.db[self.followerID_collection_name].distinct("followerID")
        except:
            print('Cannot perform database operation')
            return

        uniq_followers = list(uniq_followers)

        self.userIDs = uniq_followers

        # close the connection
        db.close()

    def textClean(self, userIDs = []):

        if not userIDs:
            if not self.userIDs:
                print('no tweet to clean')
            else:
                userIDs = self.userIDs

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
        thread_n = int(self.thread_n)

        # because mongodb is running locally, and it will create a thread for each connection,
        # here we set the thread number to no larger than all_threads/2
        if thread_n > ( int(all_threads/2) ) or thread_n <= 0:
            thread_n = int(all_threads/2)

        if thread_n >= len(userIDs):
            thread_n = len(userIDs)

        print('{} threads out of {} will be used'.format(thread_n, all_threads))

        process_list = []

        # split the list of followers(userIDs) into chunks and start a process to deal with each chunk
        for i in range(thread_n):
            c = chunkFun(userIDs, thread_n, i)
            p = Process(target=self.textCleanWorker, args=(c,i,))
            p.start()
            process_list.append(p)

        for p in process_list:
            p.join()

        print('All Done!')

