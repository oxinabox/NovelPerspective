import sys
sys.path.append("../proto")


import cherrypy
import traceback
from os.path import *

from book import *
from sample_chapters import *
from feature_extraction import *
from classify import *
from sklearn.externals import joblib

#################################################

def prepare_book(input_filepath, output_filepath, solver_id, reprocess_epub=False, heuristics=False, split_scenes=False):
    cherrypy.session['solver_id'] = solver_id

    yield ("<h2>Preparing Book</h2>");
    yield ("Performing any preprocessing/conversion required </br> <hr/> <pre>")
    print("outfp ", output_filepath)
    yield from convert_book(input_filepath, output_filepath,
                            generate_output=True,
                            reprocess_epub=reprocess_epub,
                            heuristics=heuristics,
                            split_scenes=split_scenes)

    cherrypy.session['book'] = load_book(output_filepath)
    yield "</pre><hr/>"
    yield """
    <form method="POST" action="classify">
        <input type="submit" value="Classify Characters">
    </form>
    """
    
    yield """<a href="classify"> Classify Characters</a>"""



###############################################

def classify_chapters():
    book = cherrypy.session['book']
    texts, indexes = load_chapters(book)

    solver_id = "solver unknown"
    solver_id = cherrypy.session['solver_id']
    solver = load_solver(solver_id)
    
    output_characters = solver.choose_characters(texts)
    yield from book_table(output_characters, texts, indexes)

########

def load_solver(solver_id):
    if solver_id == "FirstMentioned":
        return FirstMentionedSolver()
    elif solver_id == "MostMentioned":
        return MostMentionedSolver()
    else: # assume it is something we have serialized
        filename = os.path.basename(solver_id) # Avoid directory traversal attacks
        return joblib.load(os.path.join("../trained_models", filename))


#####################################################################
# Express it via a webpage

def tr(*xs):
    guts = " ".join("<td>"+str(x)+"</td>\t" for x in xs)
    return "<tr>"+guts+"</tr>"


def book_table(output_characters, texts, indexes):
    yield ("<h2>Classification of Chapters</h2>");
    import filter_script # small python module with a single string (import will only load once vs open-read every time)
    yield(filter_script.code)

    yield("""<form method="get" action="generate_ebook">""")
    yield("<table>")
    for index, character, text in zip(indexes, output_characters, texts):
        example_length = min(len(text)//2, 512)
        chkbox = """<input type="checkbox" id="box%i" name="keep" value="%i" class="keepchapter"/>""" % (index,index)
        lbl = """<label for="box%i" id="ch%i" class="charactername">%s</label> """ % (index, index, character)
        yield tr(chkbox, lbl, text[0:example_length])

    yield("</table>")
    yield("""<input type="submit" value="Generate ebook with only selected chapters"/>""")
    yield("</form>")
    
