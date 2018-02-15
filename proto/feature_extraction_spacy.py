import spacy
from collections import *
import numpy as np

en_nlp = spacy.load('en_core_web_sm', disable=['parser'])


# TODO: to go really face with spacy need to use pipe,
# that is applied to a bunch of documents at a time,
# and returns their enriched forms using a generator

from functools import reduce, lru_cache 
@lru_cache(maxsize=10^5)
def enrich_text(raw_text):
    return en_nlp(str(raw_text)) #Have to convert because numpy.str_ and str are different types

def is_character_NE(ent, even_more_generous=False):
    # Spacy seems to often think that '’s' and pure whitespace is a GPE
    # Manually knock those out
    if ent.text=='’s' or ent.text.strip()=='':
        return False
    
    
    lbl = ent.label_
    # Fantasy names are hard to classify as the correct named enity
    # because they are often "Exotic"
    # So we checked the sameple_chapters, and picked out all the classes they were commenly labelled as.
    return lbl=='ORG' or lbl=='PERSON' or lbl=='GPE' or \
            (even_more_generous and (lbl=='LOC' or lbl=='FAC' or lbl=='EVENT'))
    
    
spacy_tagset = ('',*en_nlp.tagger.labels) #some things apprently have no tag
def SpacyFeatureVec():
    vec=OrderedDict()
    vec["occur_count"]=0
    vec["occur_percent"]=0.0
    vec["first_occur_position"]=0
    vec["first_occur_percent"]=0.0
    vec["last_occur_position"]=0
    vec["last_occur_percent"]=0.0
    vec["occur_rank"]=0
    vec["occur_rank_percent"]=0
    for tag in spacy_tagset:
        vec["before_POS_was_"+tag]=0
        vec["after_POS_was_"+tag]=0
        vec["before_POS_was_percent_"+tag]=0.0
        vec["after_POS_was_percent_"+tag]=0.0
    return vec

SpacyFeatureVec_keys = list(SpacyFeatureVec().keys())


def get_spacy_feature_vectors(raw_text):
    
    enriched_doc = enrich_text(raw_text)
    
    feature_vecs = defaultdict(SpacyFeatureVec)
    overall_counts = Counter()
    
    for ent in enriched_doc.ents:
        if not(is_character_NE(ent)):
            continue
            
        name = ent.text.strip()

        overall_counts[name]+=1
        vec = feature_vecs[name]
        vec["occur_count"]+=1 #should be equal to overall_counts
        
        vec["last_occur_position"] = ent.start #update last seen to this sent
        if not("first_occur_position" in vec): #if not set then this sent must be first time
            vec["first_occur_position"] = ent.start
        
        if ent.start > 0:
            before = enriched_doc[ent.start-1]
            vec["before_POS_was_"+before.tag_]+=1
        if ent.end < len(enriched_doc): #end is index of first token outside the named entity
            after = enriched_doc[ent.end]
            vec["after_POS_was_"+after.tag_]+=1



    ###Basic data collected
    number_named_entities = len(overall_counts)

    #Final Percent processing, and flattening
    vectors=[]
    names=[]
    
    for rank,(name, count) in enumerate(overall_counts.most_common(),1):
        
        vec = feature_vecs[name]
        assert(count==vec["occur_count"])
        vec["occur_percent"] = 100*count/sum(overall_counts.values())
        
        vec["occur_rank"] = rank
        vec["occur_rank_percent"] = 100*rank/number_named_entities
        vec["first_occur_percent"] = 100*vec["first_occur_position"] / len(enriched_doc)
        vec["last_occur_percent"] = 100*vec["last_occur_position"] / len(enriched_doc)
        
        for tag in spacy_tagset:
            vec["before_POS_was_percent_"+tag]=100*vec["before_POS_was_"+tag]/count
            vec["after_POS_was_percent_"+tag]=100*vec["after_POS_was_"+tag]/count
        
        
        vectors.append(list(vec.values()))
        assert len(vectors[-1])==len(SpacyFeatureVec_keys), "%i != %i" % (len(vectors[-1]), len(vector_keys) )#Make sure I have everything
        names.append(name)
    
    return names, np.asarray(vectors), SpacyFeatureVec_keys
