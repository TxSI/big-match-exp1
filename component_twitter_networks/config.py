# user id or screen name of the target user 
# from who the follower and their tweets will be collected
#id_or_screen_name = 'winterdamsel Roc_Yao zhangby2085'
id_or_screen_name = 'TampereUniTech TAMK_UAS UniTampere Tampere_3'

# project name
project_name = 'tampere3_May_recollect'

# the scope of the project, should be the same of the id_or_screen_name
# or a sub set of it
project_target_name = 'TampereUniTech TAMK_UAS UniTampere Tampere_3'

# mongoDB host
db_host = 'localhost'

# mongoDB port
db_port = 27017

# database name 
#db_name = 'tampere3_allinmongodb'
db_name = 'tampere3_May_recollect'

# tweet collection name
tweet_collection_name = 'tweets'

# follwers id collection name
followerID_collection_name = 'followerID'

# follower of followers collection name
followeroffollower_collection_name = 'followeroffollower'

# log collection name
log_collection_name = 'log'

# followers id:name mapping collection name
id_name_collection_name = 'id_name'

# the most number of tweets to collect for each follower
tweet_num = 500

# the least number of tweets to process for each follower
tweet_process_num = 500

# this setting is used in data filtering phase to filter out those who have 
# less tweets than this threshold
threshold_num = '50'

# set the target language of tweet to process (currently only support English)
lan = 'en'

# set the thread number in data clean process
# 0 will let the system detect the number of thread to use
# you can also assign a number here
thread_n = 0

# by default, the breakpoint is turn on to continue the previous data clean 
# processing which is, by accidant or purpose, interrupted
#
# NOTE: 
#     Please turn it off, If you have modified the data clean funcion and want 
# to re-apply it on the same database(tweet collection) 
# 
breakpoint = 0
