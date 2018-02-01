import sys
sys.path.append("../proto")


import cherrypy
import traceback
import os.path

from book import *
from sample_chapters import *
from feature_extraction import *
from classify import *
from sklearn.externals import joblib



def handle_exception(err, msg):
    yield "<h3>Error: %s</h3>" % msg
    yield "<pre> str(err) \n\n\n"
    yield traceback.print_exc()
    raise(err)

def load_solver(solver_id):
    if solver_id == "FirstMentioned":
        return FirstMentionedSolver()
    elif solver_id == "MostMentioned":
        return MostMentionedSolver()
    else: # assume it is something we have serialized
        filename = os.path.basename(solver_id) # Avoid directory traversal attacks
        return joblib.load(os.path.join("../trained_models", filename))



def main(filepath, solver_id):
    try:
        book = load_book(filepath)
        cherrypy.session['book'] = book
        texts, indexes = load_chapters(book)
    except Exception as err:
        handle_exception(err, "Failed to Load Book")

    try:
        solver = load_solver(solver_id)
    except Exception as err:
        handle_exception(err, "Failed to Load Character Classifier '%s'" % solver_id)

    try:
        output_characters = solver.choose_characters(texts)
        yield from book_table(output_characters, texts, indexes)
    except Exception as err:
        handle_exception(err, "in Generating Character Classifications")


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
        chkbox = """<input type="checkbox" id="box%i" name="keep" value="%i" class="keepchapter"/>""" % (index,index)
        lbl = """<label for="box%i" id="ch%i" class="charactername">%s</label> """ % (index, index, character)
        yield tr(chkbox, lbl, text[0:512])

    yield("</table>")
    yield("""<input type="submit" value="Generate ebook with only selected chapters"/>""")
    yield("</form>")
    
