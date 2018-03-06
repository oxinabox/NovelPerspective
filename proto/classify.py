from feature_extraction import *
import numpy as np

from collections import Counter

from xgboost import XGBClassifier
import sklearn.metrics
from sklearn.model_selection import cross_val_score

from abc import *

###################################################
class AbstactCharacterSolver(ABC):

    def __init__(self, nicknames2name=dict()):
        self.nicknames2name = nicknames2name


    def choose_character(self, raw_text):
        return self.score_characters(raw_text)[0][-1]

    def choose_characters(self, raw_texts):
        return (self.choose_character(text) for text in raw_texts)

    def score_characters(self, raw_text)
        scores, names = self.calculate_character_scores(raw_text)
        assert(len(names) == len(scores))
        if len(names) > 0:
            self.merge_nicknames(scores,names)
            return sorted(zip(scores,names))
        else:
            return [(1.0, "[No Characters Detected]")]


    """
    Should return scores, names
    Higher score is better, scores should be nonnegative.
    Low-level, does not have to handle merging nicknames.
    """
    @abstractmethod
    def calculate_character_scores(self, raw_text):
        pass

    """
    Merge the scores of characters nicknames into the real name
    """
    def merge_nicknames(self, scores, names):
        for nickname,truename in self.nicknames2name.items():
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



    def train(self, raw_texts, reference_characters):
        pass; #Fall back for non-ML methods

    def test(self, raw_texts, reference_characters, metric=sklearn.metrics.accuracy_score):
        output_characters_gen = self.choose_characters(raw_texts)
        output_characters = list(output_characters_gen)
        return metric(output_characters, reference_characters)

##################################################

class MLCharacterSolver(AbstactCharacterSolver):

    def __init__(self, classifier=XGBClassifier(), nicknames2name=dict(), feature_extractor = get_feature_vectors):
        self.classifier = classifier
        self.feature_extractor = feature_extractor
        super().__init__(nicknames2name)


    def calculate_character_scores(self, raw_text):
        names, feature_vectors, vector_keys = self.feature_extractor(raw_text)
        assert(len(names) == len(feature_vectors))
        if len(names) > 0:
            scores = self.classifier.predict_proba(feature_vectors)[:,1] #second index is positive class
            return scores, names
        else:
            return [],[]



    def train(self, texts, reference_characters):
        Xs = [] # Feature vectors
        Ys = [] # Binary as to if this feature is the target
        for reference_name, raw_text in zip(reference_characters, texts):
            names, vectors, _ = self.feature_extractor(raw_text)
            Ys.extend([(name == reference_name) for name in names])
            Xs.extend(vectors)

        Xs = np.asarray(Xs)
        Ys = np.asarray(Ys)
        assert Xs.shape[0]==Ys.shape[0]
        assert len(Xs.shape)==2, "Xs.shape = "+str(Xs.shape)

        assert Xs.shape[1]>2, "Xs.shape[1] = "+str(Xs.shape[1])

        self.classifier.fit(Xs,Ys)
        return self


##################################################

class FirstMentionedSolver(AbstactCharacterSolver):
    def calculate_character_scores(self, raw_text):
        ne_words = ne_preprocess(raw_text)
        for cur in ne_words:
            if type(cur)==nltk.tree.Tree and cur.label()=='NE':
                name = get_name(cur)
                return [1.0], [name] # Just return the first one we find
        return [],[] # No named entities

class MostMentionedSolver(AbstactCharacterSolver):
    def calculate_character_scores(self, raw_text):
        ne_words = ne_preprocess(raw_text)

        total = 0
        mentions = Counter()
        for cur in ne_words:
            if type(cur)==nltk.tree.Tree and cur.label()=='NE':
                name = get_name(cur)
                mentions[name]+=1
                total+=1

        return np.fromiter(mentions.values(), dtype="float64")/total,  list(mentions.keys())
        # Score is equal to portion of times it is mentioned


