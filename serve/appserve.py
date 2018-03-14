#! /usr/bin/python3
import sys
from os.path import *
app_path   = abspath(dirname(__file__))
sys.path.append(app_path)

from main import *
from expiring_files import *

import cherrypy
from cherrypy.lib import static

cherrypy.config.update({
#    'server.socket_port': 7778,
    'server.socket_host': '0.0.0.0',
    'request.show_traceback': True,
    'tools.sessions.on': True,
    'tools.sessions.name' : "NovelPerspective_session_id",
    'tools.sessions.timeout': 90, # 1.5 hours
    'tools.sessions.locking': 'early',
    'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
    'tools.sessions.storage_path' : "/tmp",
})
app_conf = {
    '/':
        { 'tools.staticdir.on':True,
          'tools.staticdir.dir': app_path,
          'tools.staticdir.index' : "indexpage.html"
        }
}

cherrypy.log.screen = True

###################

def header(title, extra=""):
    return ("""<html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width">
            <title>NovelPerspective: """ + title + """</title>
            <link rel="stylesheet" href="main.css" type="text/css" />

            <script
            src="https://code.jquery.com/jquery-3.3.1.slim.min.js"
            integrity="sha256-3edrmyuQ0w65f8gfBsqowzjJe2iM6n0nKciPUp8y+7E="
            crossorigin="anonymous"></script>
        """
        + extra
        + """
        </head>
        <body>
        """
        + 1024*" " # add extra data to help encourage chunked rendering
        )

footer = """<footer> Made by <a href="http://white.ucc.asn.au"> Lyndon White<a>. You can find the <a href="https://github.com/oxinabox/NovelPerspective"> source on Github</a>. </footer>"""


class App:
    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def upload(self, myFile, **kwargs):
        yield header("Preparing Book")
        yield """<div class="infopage">"""

        check_expires() # Someone added something new, is as good a time as any to check

        if myFile.filename == "":
            yield "You must upload a file. <br/> Go back and try again."
            raise StopIteration


        # save it to disk for disk operations
        safe_filename = os.path.basename(myFile.filename) # avoid directory traversal attacks
        disk_fh = expiring_temp_file(safe_filename)
        disk_fh.write(myFile.file.read())

        out_fh = expiring_temp_file(splitext(safe_filename)[0] + ".epub")

        yield from prepare_book(disk_fh.name, out_fh.name, **kwargs)
        yield footer


    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def classify(self):
        yield header(
            "Character Classifications",
            """<link rel="stylesheet" href="classifications.css" type="text/css" />"""
        )
        yield """<div class="infopage">"""
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
        book_filename = basename(book.title)+".epub" # avoid directory traveral attacks
        outfile = expiring_temp_file(book_filename)
        rewrite_book(book, keep, outfile.name)
        return static.serve_file(
            outfile.name,
            "application/x-download",
            "attachment",
            book_filename
        )


##############

def application(environ, start_response):
    cherrypy.tree.mount(App(), "/", app_conf)
    return cherrypy.tree(environ, start_response)

if __name__ == '__main__':
    cherrypy.quickstart(App(), '/', app_conf)
