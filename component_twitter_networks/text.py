from langdetect import detect
from langdetect import DetectorFactory
import re
import urllib.request as ur
import spacy

class Text:

    def __init__(self):
        # load the spacy english model
        self.nlp = spacy.load('en')

        # ensure everytime the lan detect result is consistent
        DetectorFactory.seed = 0
                                
        self.extrawords = ["'s", "st", "th", "’s", "-PRON-", "’", "htt", "ht", "km", "pm", "am","&amp"]
                                                
        # parse the latest emoji code
        html = str(ur.urlopen('http://www.unicode.org/Public/emoji/5.0/emoji-data.txt').read())
        codes=list(map(lambda x: '-'.join(['\\U'+a.zfill(8) for a in x.split('..')]).encode().decode('unicode-escape'),re.findall(r'(?<=\\n)[\w.]+',html)))
        self.emojiPattern = re.compile('['+','.join(codes)+']',flags=re.UNICODE)

    # detect punctions, space, stop words, extra meanless words and single characater
    def punct_space_misc(self, token):
        return token.is_punct or token.is_space or token.lemma_ in spacy.lang.en.STOP_WORDS or token.lemma_ in self.extrawords or len(str(token)) < 2


    def doClean(self, text):
        # detect the language of the text
        try:   
            lan = detect(text)
        except:
            lan = 'none'
        text = text.lower()
      
        text = text.replace('\n',' . ')
 
        myre = re.compile(u'('
                '@\S*\s?|#|'   # remove @ mention names and hastag sign
                'http[s]?[:…]\S*\s?|' # remove url
                '[-~\^\$\*\+\{\}\[\]\\\|\(\)/“"]|' # remove special characater
                'rt[:]? |'  # remove retweet sign
                '…'   # remove the ... sign, when tweet is too long the text collected by tweet API will be omited
                ')+', re.UNICODE)
        text = myre.sub(' ', text)
        # further remove the emoji
        text = self.emojiPattern.sub(' ', text)

        # futher clean the data using nlp package from spacy if the tweet is english
        if lan == 'en':
            text = self.nlp(text)
            tokens = []
            for token in text:
                if self.punct_space_misc(token):
                    continue
                tokens.append(token.lemma_)
        
            text = ' '.join(tokens)

        return (text,lan)
