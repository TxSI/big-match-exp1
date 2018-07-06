# ABOUT
This repository contains the code to collect the followers and followers's tweets of the target(s) account. Then performan a people recommendation for a given user who is one of the followers.  
The tasks include:
1. collect followers and their tweets, save into MongoDB
2. Language detection for each tweet
3. Identity classification for each follower ( person or organisation)
4. Create mention network (not following network) for Gephi network analysis
5. Perform people recommendation using basic TF-IDF features on English-only tweets

# Environment
Dev and test on:  
OS: OSX Version 10.12.6  
    Debian 9

Python:  
- Python 3.5.4

conda: 4.3.21  
langdetect: 1.0.7  

# HOW TO
### System Configuration
Before you run the system, please check the config.py to make sure database setting are correct and also set the twitter data collecting and cleaning related field
### Collect Data
Install and run MongoDB in background
https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/
First get the followers ID
```python
python get_followers.py
```
Collect followers's tweets and save into MongoDB
```python
python get_followers_tweets_mongodb.py
```
### Data Clean & Preprocess 

Clean all the tweets
```python
python clean_tweets.py
```

Build the user corpus profile
```python
python build_profile.py
```

Create follower-follwee network
```python
python create_followship_network.py
```
Create mention network
```python
python create_mention_network.py
```

### Run the recommendation
Run the recommendation system for a given user and output the result
Example code is given in make_LDA_rec.py. You can modify the example to run LDA in unigram, bigram or trigram corpus

```python
python make_LDA_rec.py
```

