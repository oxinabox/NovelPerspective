import numpy as np
import nltk
from collections import Counter, defaultdict, OrderedDict
import itertools as it
import os.path

PADDING_TOKEN = ("", "<PAD>") #word,Tag

def pairwise(iterable):
    return nwise(2, iterable)

def triplewise(iterable):
    return nwise(3, iterable)

def nwise(n, iterable):
    "s -> (s0,s1,...,sn), ((s1,s2,...,sn+1), ((s2,s3,...,sn+2), ..."
    cur_iter = iterable
    iters = []
    for ii in range(0,n): #exluces last
        ii_iter, cur_iter = it.tee(cur_iter)
        iters.append(ii_iter)
        next(cur_iter, None)

    assert(len(iters) == n)
    return zip(*iters)


from functools import reduce, lru_cache



##############

@lru_cache(maxsize=10^5)
def ne_preprocess(raw_text, flatten=True):
    sents = nltk.sent_tokenize(raw_text)
    tokenised_sents = [nltk.word_tokenize(sent) for sent in sents]
    tagged_sents = nltk.pos_tag_sents(tokenised_sents)
    ne_sents = nltk.ne_chunk_sents(tagged_sents, binary=True)
    return list(it.chain(*ne_sents)) if flatten else ne_sents


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

def get_word(item):
    if type(item)==nltk.tree.Tree:
        return get_name(item)
    elif type(item)==tuple:
        return item[0]
    else:
        assert(type(item) in [tuple, nltk.tree.Tree])

#########################

from nltk.data import load
tagset = list(load('help/tagsets/upenn_tagset.pickle').keys())
tagset.append('NE')
tagset.append(PADDING_TOKEN[1])
tagset.append('#')

def FeatureVec():
    vec=OrderedDict()
    vec["occur_count"]=0
    vec["occur_percent"]=0.0
    vec["first_occur_position"]=0
    vec["first_occur_percent"]=0.0
    vec["last_occur_position"]=0
    vec["last_occur_percent"]=0.0
    vec["occur_rank"]=0
    vec["occur_rank_percent"]=0
    for tag in tagset:
        vec["before_POS_was_"+tag]=0
        vec["after_POS_was_"+tag]=0
        vec["before_POS_was_percent_"+tag]=0.0
        vec["after_POS_was_percent_"+tag]=0.0
    return vec


"""
Returns a list of names, feature_vectors, and a definition of the feature vector keys
"""
#@lru_cache(maxsize=10^5)
def get_feature_vectors(raw_text):

    ne_words = 2*[PADDING_TOKEN] + ne_preprocess(raw_text) + 2*[PADDING_TOKEN]

    feature_vecs = defaultdict(FeatureVec)
    overall_counts = Counter()

    for ii, (before, cur, after) in enumerate(triplewise(ne_words)):
        if type(cur)==nltk.tree.Tree and cur.label()=='NE':
            name = get_name(cur)

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

        vec["occur_rank"] = rank
        vec["occur_rank_percent"] = 100*rank/number_named_entities
        vec["first_occur_percent"] = 100*vec["first_occur_position"] / len(ne_words)
        vec["last_occur_percent"] = 100*vec["last_occur_position"] / len(ne_words)

        for tag in tagset:
            vec["before_POS_was_percent_"+tag]=100*vec["before_POS_was_"+tag]/count
            vec["after_POS_was_percent_"+tag]=100*vec["after_POS_was_"+tag]/count


        vectors.append(list(vec.values()))
        assert len(vectors[-1])==len(vector_keys), "%i != %i" % (len(vectors[-1]), len(vector_keys) )#Make sure I have everything
        names.append(name)

    return names, np.asarray(vectors), vector_keys


##################################

import fastText # from https://github.com/facebookresearch/fastText/


_fasttext_embedding_dim = 300
_fasttext_path = os.path.join(os.path.dirname(__file__), "wiki.en.bin")
_fasttext_model=None #Lazy load
def fasttext_model():
    global _fasttext_model
    if _fasttext_model==None:
        _fasttext_model = fastText.load_model(_fasttext_path)
    return _fasttext_model


def word_embedding(word):
    return fasttext_model().get_word_vector(word)

#@lru_cache(maxsize=10^5)
def get_embedding_features(raw_text,
                           half_window_len=1,
                           include_NE_embedding=False,
                           include_occur_count_statistics=False):


    full_window_len = 2*half_window_len+1
    ne_words = (half_window_len*[PADDING_TOKEN]
                +ne_preprocess(raw_text)
                + half_window_len*[PADDING_TOKEN])

    overall_counts = Counter()
    vec_len = (2*half_window_len+include_NE_embedding) * _fasttext_embedding_dim
    feature_vecs = defaultdict(lambda: np.zeros(vec_len))
    for window in nwise(full_window_len, ne_words):
        cur=window[half_window_len] # center
        if type(cur)==nltk.tree.Tree and cur.label()=='NE':
            name = get_name(cur)
            overall_counts[name]+=1

            wembs = [word_embedding(get_word(ww))
                                  for (wi,ww) in enumerate(window)
                                  if include_NE_embedding or wi!=half_window_len
                                  #i.e. if should skip cur, then skip based on its index
                              ]

            vec = feature_vecs[name]
            vec += np.hstack(wembs)


    #Final Percent processing, and flattening
    names=[]
    vectors=[]
    number_named_entities = len(overall_counts)
    if number_named_entities==0:
        return [],[],[]

    for rank,(name, count) in enumerate(overall_counts.most_common(),1):

        vec = feature_vecs[name]
        mowe_vec = feature_vecs[name]/count

        if include_occur_count_statistics:
            occur_stats = [
                count, #vec["occur_count"]
                100*count/sum(overall_counts.values()), #vec["occur_percent"]
                rank, #vec["occur_rank"]
                100*rank/number_named_entities #vec["occur_rank_percent"]
            ]
            mowe_vec = np.hstack([occur_stats, mowe_vec])


        vectors.append(mowe_vec)
        names.append(name)


    return names, np.vstack(vectors), vec_len*["WordEmbeddings"]


####
def hybrid_features(x):
    cl_names, cl_vecs, cl_features = get_feature_vectors(x)
    emb_names, emb_vecs, we_features = get_embedding_features(x)
    assert cl_names == emb_names
    if len(cl_names)==0:
        return [], [], []
    
    vecs = np.hstack([cl_vecs, emb_vecs])
    assert vecs.shape[0]==len(cl_names)
    assert vecs.shape[1]>2
    return cl_names, vecs, cl_features +  we_features