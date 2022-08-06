import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import pickle
from ml_utils import preprocessor

def initialise():
  data = pd.read_csv("cyberbullying_tweets.csv")
  data = data[data['cyberbullying_type'] != 'other_cyberbullying']
  data = data.sample(frac = 0.10, random_state = 50)
  train_features, test_features, train_labels, test_labels = train_test_split(data['tweet_text'].values, data['cyberbullying_type'].values, test_size = 0.3, random_state = 50)
  
  vectorizer = TfidfVectorizer(tokenizer = preprocessor, lowercase = True)
  train_features = vectorizer.fit_transform(train_features)
  test_features = vectorizer.transform(test_features)
  pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
  
  train_features = train_features.toarray()
  test_features = test_features.toarray()

  clf = RandomForestClassifier()
  clf.fit(train_features, train_labels)
  pickle.dump(clf, open("model.pkl", "wb"))

def predict(sentence):
  v = pickle.load(open("vectorizer.pkl", "rb"))
  clf = pickle.load(open("model.pkl", "rb"))
  bow = v.transform([sentence]).toarray()
  return clf.predict(bow)[0]
