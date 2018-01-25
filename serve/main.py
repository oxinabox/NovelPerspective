import sys
sys.path.append("../proto")


from book import *
from sample_chapters import *
from feature_extraction import *
from classify import *
from sklearn.externals import joblib
import cherrypy


def main(filepath):
    yield ("<li>Loading Book");
    cherrypy.log("************************", filepath)
    texts, _ = load_book(filepath)
    
    yield ("<li>Loading Model");
    cls = joblib.load("../trained_models/GoT-no-headings.pkl")
    
    yield ("<li>Running Classifier");
    output_characters = run_classifier(texts, classifier=cls)
    yield ("<h2>Classification of Chapters</h2>");
    
    yield("<table>")
    for character, text in zip(output_characters, texts):
#        print("<tr><td>\t",character,"\t</td><td>\t",text[0:256],"...\t</td></tr>"); sys.stdout.flush()
         yield " ".join(("<tr><td>\t",character,"\t</td><td>\t",text[0:256],"...\t</td></tr>"));
    yield("</table>")
        
