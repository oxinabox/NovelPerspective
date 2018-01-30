import sys
sys.path.append("../proto")


from book import *
from sample_chapters import *
from feature_extraction import *
from classify import *
from sklearn.externals import joblib
import cherrypy


def main(filepath):
    #yield ("<li>Loading Book");
    cherrypy.log("************************", filepath)
    texts, indexes = load_book(filepath)
    # Note: indexes are no sequential as no chapter items are skipped
    
    #yield ("<li>Loading Model");
    cls = joblib.load("../trained_models/GoT-no-headings.pkl")
    
    #yield ("<li>Running Classifier");
    output_characters = run_classifier(texts, classifier=cls)
    yield ("<h2>Classification of Chapters</h2>");
    
    yield from book_table(output_characters, texts, indexes)


#####################################################################
# Express it via a webpage

def tr(*xs):
    guts = " ".join("<td>"+str(x)+"</td>\t" for x in xs)
    return "<tr>"+guts+"</tr>"


filter_code = """
<script>
function selectchapters(filterstring) {
    if (typeof(filterstring)==='undefined') filterstring = $("#txt_filter").val();

    var filterregex = new RegExp(filterstring);

    // uncheck everything
    $('.keepchapter')
        .each(function(index) {
            $(this).attr("checked", false);
        });

    // check thjose with matching regex
    $(".charactername")
        .filter(function() {
            return $(this).text().match(filterregex);
        })
        .each(function(index) {
            checkbox_id = $(this).attr('for');
            console.log('#' + checkbox_id);
            $('#' + checkbox_id)[0].checked =  true;
        });
}
</script>
<input type="text" id="txt_filter"
    onkeydown = "if (event.keyCode == 13) selectchapters()"/>
<button type="button" onclick="selectchapters()">Filter by Regex</button>
"""

def book_table(output_characters, texts, indexes):
    yield(filter_code)

    yield("""<form method="get" action="generate_ebook">""")
    yield("<table>")
    for index, character, text in zip(indexes, output_characters, texts):
        chkbox = """<input type="checkbox" id="box%i" name="keep" value="%i" class="keepchapter"/>""" % (index,index)
        lbl = """<label for="box%i" id="ch%i" class="charactername">%s</label> """ % (index, index, character)
        yield tr(chkbox, lbl, text[0:256])

    yield("</table>")
    yield("""<input type="submit" value="Generate ebook with only selected chapters"/>""")
    yield("</form>")
    
