import spacy
import string

def preprocessor(sentence):
    nlp = spacy.load('en_core_web_sm')
    tokens = nlp(sentence)
    punctuations = string.punctuation
    tokens = [ token.lemma_.lower() for token in tokens if token.is_stop == False and token.like_url == False and token.text not in punctuations ]
    return tokens