from main import *
from expiring_files import *

import os.path
import cherrypy
from cherrypy.lib import static

app_path   = os.path.abspath(os.path.dirname(__file__))
cherrypy.config.update({
    'server.socket_port': 7778,
    'server.socket_host': '0.0.0.0',
    'request.show_traceback': True,
    'tools.sessions.on': True,
    'tools.sessions.name' : "NovelPerspective_session_id",
    'tools.sessions.timeout': 90, # 1.5 hours
    'tools.sessions.locking': 'early',
#    'tools.sessions.storage_type': "file",
#    'tools.sessions.storage_path' : "/tmp/sessions",
})
app_conf = {
    '/':
        { 'tools.staticdir.on':True,
          'tools.staticdir.dir': os.path.join(app_path),#, "main.css")
          'tools.staticdir.index' : "indexpage.html"
        }
}

cherrypy.log.screen = True

###################

footer = """<footer> Made by <a href="http://white.ucc.asn.au"> Lyndon White <a>. You can find the <a href="https://github.com/oxinabox/NovelPerspective"> source on Github</a>. </footer>"""


class App:
#    @cherrypy.expose
#    def index(self):
#        with open("./indexpage.html", "r") as fh:
#            return fh.read()
   

    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def upload(self, myFile, **kwargs):
        yield """<html>
            <head>
                <title>NovelPerspective: Preparing Book</title>
                <link rel="stylesheet" href="main.css" type="text/css" />
            </head>
            <body class="infopage">
        """
        check_expires() # Someone added something new, is as good a time as any to check
        
        if myFile.filename == "":
            yield "You must upload a file. <br/> Go back and try again."
            raise StopIteration


        #save it to disk for disk operations
        safe_filename = os.path.basename(myFile.filename) # avoid directory traversal attacks
        disk_fh = expiring_temp_file(safe_filename)
        disk_fh.write(myFile.file.read())
        
        out_fh = expiring_temp_file(splitext(safe_filename)[0] + ".epub")

        yield from prepare_book(disk_fh.name, out_fh.name, **kwargs)
        yield footer


    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def classify(self):
        yield """<html>
                <head>
                    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
                    <link rel="stylesheet" href="main.css" type="text/css" />
                    <title>NovelPerspective: Character Classifications</title>
                </head>
                <body>
        """
        yield from classify_chapters()
        yield footer

    @cherrypy.expose
    def generate_ebook(self, keep=None):
        # No need for HTML output here, it is a download dialog, unless it is an error
        if keep==None:
            return "No chapters selected. <br/> Go back and select 1 or more chapters."

        if type(keep)==str: # if single argument then does not make lists
            keep = [int(keep)]
        if type(keep)==list: # it is a list of strings
            keep = [int(kk) for kk in keep]
        else:
            raise TypeError("Unxpected type for keep. keep=" + str(keep))


        book = cherrypy.session['book']
        safe_title = basename(book.title) # avoid directory traveral attacks
        outfile = expiring_temp_file(safe_title + ".epub")
        rewrite_book(book, keep, outfile.name)
        return static.serve_file(outfile.name, "application/x-download", "attachment")


if __name__ == '__main__':
    cherrypy.quickstart(App(), '/', app_conf)
