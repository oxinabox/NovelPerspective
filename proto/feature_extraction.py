import numpy as np
import nltk
from collections import Counter, defaultdict, OrderedDict
import itertools as it
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)

def triplewise(iterable):
    "s -> (s0,s1,s2), (s1,s2,s3), (s2, s3,s4), ..."
    a, b = it.tee(iterable)
    b, c = it.tee(b)
    next(b, None)
    next(c, None)
    next(c, None)
    return zip(a, b,c)




from functools import reduce, lru_cache



##############

@lru_cache(maxsize=None)
def ne_preprocess(raw_text):
    sents = nltk.sent_tokenize(raw_text)
    tokenised_sents = [nltk.word_tokenize(sent) for sent in sents]
    tagged_sents = nltk.pos_tag_sents(tokenised_sents)
    ne_sents = nltk.ne_chunk_sents(tagged_sents, binary=True)
    return list(it.chain(*ne_sents))
    

def get_name(ne_tree):
    return " ".join([tagged_leaf[0] for tagged_leaf in ne_tree.leaves()])
    
def get_named_entities(sent):
    for subsent in sent.subtrees(lambda ss:ss.label()=='NE'):
        yield get_name(subsent)

        
        
        
def get_tag(item):
    if type(item)==nltk.tree.Tree:
        return item.label()
    elif type(item)==tuple:
        return item[1]
    else:
        assert(type(item) in [tuple, nltk.tree.Tree])

#########################

from nltk.data import load
tagset = list(load('help/tagsets/upenn_tagset.pickle').keys())
tagset.append('NE')
tagset.append('PAD')
tagset.append('#')

def FeatureVec():
    vec=OrderedDict()
    vec["occur_count"]=0
    vec["occur_percent"]=0.0
    vec["first_occur_position"]=0
    vec["first_occur_percent"]=0.0
    vec["last_occur_position"]=0
    vec["last_occur_percent"]=0.0
    vec["rank"]=0
    vec["rank_percent"]=0
    for tag in tagset:
        vec["before_POS_was_"+tag]=0
        vec["after_POS_was_"+tag]=0
        vec["before_POS_was_percent_"+tag]=0.0
        vec["after_POS_was_percent_"+tag]=0.0
    return vec


"""
Returns a list of names, feature_vectors, and a definition of the feature vector keys
"""
def get_feature_vectors(raw_text, nickname2name=dict()):
    
    ne_words = [("PAD","PAD")] + ne_preprocess(raw_text) + [("PAD","PAD")]
    
    feature_vecs = defaultdict(FeatureVec)
    overall_counts = Counter()
    
    for ii, (before, cur, after) in enumerate(triplewise(ne_words)):
        if type(cur)==nltk.tree.Tree and cur.label()=='NE':
            name = get_name(cur)
            if name in nickname2name:
                name=nickname2name[name]
            
            overall_counts[name]+=1
            vec = feature_vecs[name]
            vec["occur_count"]+=1 #should be equal to overall_counts
            vec["before_POS_was_"+get_tag(before)]+=1
            vec["after_POS_was_"+get_tag(after)]+=1
            
            vec["last_occur_position"] = ii #update last seen to this sent
            if not("first_occur_position" in vec): #if not set then this sent must be first time
                vec["first_occur_position"] = ii
    
    ###Basic data collected
    number_named_entities = len(overall_counts)

    #Final Percent processing, and flattening
    vectors=[]
    names=[]
    vector_keys = list(FeatureVec().keys())
    for rank,(name, count) in enumerate(overall_counts.most_common(),1):
        
        vec = feature_vecs[name]
        assert(count==vec["occur_count"])
        vec["occur_percent"] = 100*count/sum(overall_counts.values())
        
        vec["rank"] = rank
        vec["rank_percent"] = 100*rank/number_named_entities
        vec["first_occur_percent"] = 100*vec["first_occur_position"] / len(ne_words)
        vec["last_occur_percent"] = 100*vec["last_occur_position"] / len(ne_words)
        
        for tag in tagset:
            vec["before_POS_was_percent_"+tag]=100*vec["before_POS_was_"+tag]/count
            vec["after_POS_was_percent_"+tag]=100*vec["after_POS_was_"+tag]/count
        
        
        vectors.append(list(vec.values()))
        assert len(vectors[-1])==len(vector_keys), "%i != %i" % (len(vectors[-1]), len(vector_keys) )#Make sure I have everything
        names.append(name)
    
    return names, np.asarray(vectors), vector_keys       