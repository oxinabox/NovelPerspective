import sys
import os.path
from os.path import basename, abspath, dirname
sys.path.append(os.path.join(dirname(dirname((abspath(__file__)))), "proto"))

import cherrypy
import traceback

from book import *
from feature_extraction import *
from classify import *
from sklearn.externals import joblib


################################################

def handle_exception(context_msg, exc_info):
    print("session_id: ", cherrypy.session.id)
    traceback.print_exception(*exc_info)
    print(traceback.print_exc())
    yield "\n\n<h3>Error: %s</h3>" % context_msg
    yield """<a href="/">Return to start page<a> <br> <hr>"""
    yield """<pre class="errorlog">"""
    yield "\n".join(traceback.format_exception(*exc_info))
    yield "</pre>"
    err = exc_info[1]
    raise(err)

#################################################

def prepare_book(input_filepath, output_filepath, solver_id, reprocess_epub=False, heuristics=False, split_scenes=False):
    cherrypy.session['solver_id'] = solver_id

    yield "<h2>Preparing Book</h2>"
    yield "Performing any preprocessing/conversion required </br>"
    yield """<pre class="readout">"""
    try:
        yield from convert_book(input_filepath, output_filepath,
                                reprocess_epub=reprocess_epub,
                                heuristics=heuristics,
                                split_scenes=split_scenes)
    except Exception:
        yield from handle_exception("when preparing book", sys.exc_info())

    yield "</pre>"

    try:
        cherrypy.session['book'] = load_book(output_filepath)
        cherrypy.session.save()
        assert(cherrypy.session['book'] != None)
        print("session_id: ", cherrypy.session.id)

    except Exception:
        yield from handle_exception("when loading book", sys.exc_info())

    yield """
    <form method="POST" action="classify">
        <input class="mainbutton" type="submit" value="Classify Characters">
    </form>
    """


###############################################

def classify_chapters():
    try:
        book = cherrypy.session['book']
        texts, indexes = load_chapters(book)

        solver_id = "solver unknown"
        solver_id = cherrypy.session['solver_id']
        solver = load_solver(solver_id)

        output_characters = solver.choose_characters(texts)
        yield from book_table(output_characters, texts, indexes)

    except Exception:
        yield from handle_exception("when classifying chapters", sys.exc_info())

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
    yield "<h2>Classification of Chapters</h2>"
    yield """<a href="/">Return to start page<a> <br> <hr>"""

    import filter_script # small python module with a single string (import will only load once vs open-read every time)
    yield(filter_script.code)

    yield("""<form method="get" action="generate_ebook">""")
    yield("<table>")
    for index, character, text in zip(indexes, output_characters, texts):
        disp_name = character[:64] # For keeping the display vaguely sane
        text_segment = text[:512]

        chkbox = """<input type="checkbox" id="box%i" name="keep" value="%i" class="keepchapter"/>""" % (index,index)
        lbl = """<label for="box%i" id="ch%i" class="charactername">%s</label> """ % (index, index, disp_name)
        yield tr(chkbox, lbl, text_segment)

    yield("</table>")
    yield("""<input type="submit" value="Generate ebook with only selected chapters"/>""")
    yield("</form>")
