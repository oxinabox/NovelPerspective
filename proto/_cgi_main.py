from book import *
from sample_chapters import *
from feature_extraction import *
from classify import *
import sys
from sklearn.externals import joblib

def main(filepath):
    print("<li>Loading Book"); sys.stdout.flush()
    texts, _ = load_book(filepath)
    
    print("<li>Loading Model"); sys.stdout.flush()
    cls = joblib.load("trained_models/GoT-no-headings.pkl")
    
    print("<li>Running Classifier"); sys.stdout.flush()
    output_characters = run_classifier(texts, classifier=cls)
    print("<h2>Classification of Chapters</h2>"); sys.stdout.flush()
    
    print("<table>")
    for character, text in zip(output_characters[1:100], texts[1:100]):
        print("<tr><td>\t",character,"\t</td><td>\t",text[0:256],"...\t</td></tr>")
    print("</table>")
        