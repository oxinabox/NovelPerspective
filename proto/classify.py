from feature_extraction import *
import numpy as np

from xgboost import XGBClassifier
import sklearn.tree
import sklearn.metrics
from sklearn.model_selection import cross_val_score


def character_scores(classifier, raw_text, feature_extractor = get_feature_vectors):
    names, feature_vectors, vector_keys = feature_extractor(raw_text)
    assert(len(names) == len(feature_vectors))
    scores = classifier.predict_proba(feature_vectors)[:,1] #second index is positive class
    return scores, names

"""
Merge the scores of characters nicknames into the real name
"""
def sanitize_name_scores(scores,names, nicknames2name):
    assert(len(names) == len(scores))
    for nickname,truename in nicknames2name.items():
        try:
            ind_nick = names.index(nickname)
            try:
                ind_true = names.index(truename)

                #transfer scores over
                scores[ind_true]+=scores[ind_nick]
                scores[ind_nick]=0
            except ValueError:
                    # truename not found, rename nick
                    names[ind_nick]=truename
        except ValueError:
            #nick not found in names
            #no worries
            pass       
    

def choose_character(classifier, raw_text, nicknames2name=dict(), feature_extractor = get_feature_vectors):
    scores, names = character_scores(classifier, raw_text, feature_extractor)
    sanitize_name_scores(scores,names, nicknames2name)
    
    return names[np.argmax(scores)]


def get_binary_choice_feature_vectors(raw_text, reference_name, nicknames2name):
    names, vectors, vector_keys = get_feature_vectors(raw_text, nicknames2name)
    return vectors, 

def train_classifier(texts, reference_characters, classifier, nicknames2name=dict()):
    Xs = [] # Feature vectors
    Ys = [] # Binary as to if this feature is the target
    for reference_name, raw_text in zip(reference_characters, texts):
        names, vectors, _ = get_feature_vectors(raw_text, nicknames2name)
        Ys.extend([(name == reference_name) for name in names])
        Xs.extend(vectors)
        
    Xs = np.asarray(Xs) 
    Ys = np.asarray(Ys)

    classifier.fit(Xs,Ys)
    return classifier

def run_classifier(texts, classifier, nicknames2name=dict()):
    return [choose_character(classifier, text, nicknames2name)
            for text in texts]
    
        
def test_classifier(texts, reference_characters, classifier, nicknames2name=dict()):
    output_characters = run_classifier(texts, classifier)
    return sklearn.metrics.accuracy_score(output_characters, reference_characters)