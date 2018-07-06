from tweets import Tweets
from db import DB


tweets = Tweets()
tweets.getUserID()

# test run to clean tweets of 3 users
# tweets.textClean(tweets.userIDs[0:3])

# clean the tweets of all the users
# NOTE
#   Remember to check the 'breakpoint' setting in config.py 
# to ensure the operation is a continue clean process on previous one
# or an overwrite clean process all over again 
tweets.textClean()

