from main import *
from expiring_files import *

import os.path
import cherrypy
from cherrypy.lib import static


cherrypy.config.update({
    'server.socket_port': 7778,
    'server.socket_host': '0.0.0.0',
    'request.show_traceback': True,
    'tools.sessions.on': True,
    'tools.sessions.name' : "NovelPerspective_session_id",
    'tools.sessions.expire': 90, # 1.5 hours

})

cherrypy.log.screen = True

###################

class App:
    @cherrypy.expose
    def index(self):
        check_expires() # Someone openned the index page it is as good a time as any to check
        with open("./indexpage.html", "r") as fh:
            return fh.read()
   

    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def upload(self, myFile, solver_id):
        if myFile.filename=="":
            yield "You must upload a file. <br/> Go back and try again."
            raise StopIteration


        yield """<html>
        <head>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
            <title>NovelPerspective: Character Classifications</title>
        </head>
        <body>
        """
        #save it to disk for disk operations
        disk_fh = expiring_temp_file(myFile.filename)
        disk_fh.write(myFile.file.read())

        yield from main(disk_fh.name, solver_id)
    
    
    @cherrypy.expose
    def generate_ebook(self, keep=None):
        if keep==None:
            return "No chapters selected. <br/> Go back and select 1 or more chapters."

        if type(keep)==str: # if single argument then does not make lists
            keep = [int(keep)]
        if type(keep)==list: # it is a list of strings
            keep = [int(kk) for kk in keep]
        else:
            raise TypeError("Unxpected type for keep. keep=" + str(keep))


        book = cherrypy.session['book']
        safe_title = os.path.basename(book.title) # avoid directory traveral attacks
        outfile = expiring_temp_file(safe_title + ".epub")
        rewrite_book(book, keep, outfile.name)
        return static.serve_file(outfile.name, "application/x-download", "attachment")


if __name__ == '__main__':
    cherrypy.quickstart(App())
