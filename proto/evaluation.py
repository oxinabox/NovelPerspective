import numpy as np

from collections import Counter, defaultdict

import json
from xgboost import XGBClassifier
from sklearn.metrics import *
from sklearn.model_selection import cross_val_score, KFold
from sklearn.externals import joblib

from feature_extraction import *
from classify import *
from book import *


def extract_texts_and_characters(annotated_data):
    full_characters = np.asarray([datum['character'] for datum in annotated_data])
    full_texts = np.asarray([datum['text'] for datum in annotated_data])
    return full_texts, full_characters




def xval_evaluate(annotated_data, solver, n_splits=10, metric=accuracy_score, mute=True):
    
    full_texts, full_characters = extract_texts_and_characters(annotated_data)
    
    scores = []
    for train_inds, test_inds in KFold(n_splits=n_splits).split(annotated_data):        
        train_ann_data = annotated_data[train_inds]
        test_ann_data = annotated_data[test_inds]

        score = evaluate(train_ann_data, test_ann_data, solver, metric)
        if not(mute):
            print(score)
            
        scores.append(score)
    return np.mean(scores, axis=0)


def evaluate(train_ann_data, test_ann_data, solver, metric=accuracy_score):   
    train_texts, train_characters = extract_texts_and_characters(train_ann_data)
    test_texts, test_characters = extract_texts_and_characters(test_ann_data)

    solver.train(train_texts, train_characters)
    score = solver.test(test_texts, test_characters, metric=metric)
    return score

##########################################################################
#Just load this stuff directly


nicknames2name_comb = {
    # Make one list, because conviently none of the names overlap between books
    # Honestly that is kinda surprising, but fantasy boooks with their exotic names
    
    #ASOIF
    "Dany":"Daenerys",
    "Ned" : "Eddard",
    "Sam" : "Samwell",
    #SOC
    "Rollins" : "Pekka",
    #SA
    'Kal' : 'Kaladin',
    'Veil' : 'Shallan',
    
}

with open("../flat_data/SA.json","r") as fh:
    ann_SA = np.asarray(json.load(fh), dtype='object')
    

    
with open("../flat_data/asoif01-04.json","r") as fh:
    ann_ASOIAF = np.asarray(json.load(fh), dtype='object')
    
    
with open("../flat_data/dregs01.json","r") as fh:
    ann_SOC = np.asarray(json.load(fh), dtype='object')
with open("../flat_data/dregs02.json","r") as fh:
    ann_SOC = np.hstack([ann_SOC, np.asarray(json.load(fh), dtype='object')])

ann_comb = np.hstack([ann_SOC, ann_ASOIAF, ann_SA])

np.random.shuffle(ann_SA)
np.random.shuffle(ann_ASOIAF)
np.random.shuffle(ann_SOC)
np.random.shuffle(ann_comb)
print("ann_comb, ann_SOC, ann_ASOIAF, ann_SA")
print("lengths: ", list(map(len, (ann_comb, ann_SOC, ann_ASOIAF, ann_SA))))
print("POVs: ", *[len(np.unique(extract_texts_and_characters(ann)[1])) for ann in (ann_comb, ann_SOC, ann_ASOIAF, ann_SA)])
