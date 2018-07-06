from LdaRecsys import LdaRecsys
from gensim.models.phrases import Phrases

lda = LdaRecsys()

lda.buildCorpDict(no_blow_doc = 10, no_above_doc = 0.4)

unigram_corp = list(lda.user_corp.values())
bigram_model = Phrases(unigram_corp)

bigram_corp_dict = {}

for user,profile in lda.user_corp.items():
    bigram_corp_dict[user] = bigram_model[profile]

bigram_corp = list(bigram_corp_dict.values())
trigram_model = Phrases(bigram_corp)

trigram_corp_dict = {}

for user,profile in bigram_corp_dict.items():
    trigram_corp_dict[user] = trigram_model[profile]

lda.user_corp = trigram_corp_dict

lda.buildCorpBow()

lda.trainLDA(85,200)

while True:

    input_name = input("input user name: ")
    jnkka_recommendations = lda.makeRecommendation(input_name)
    lda.showUserTopic(input_name)


