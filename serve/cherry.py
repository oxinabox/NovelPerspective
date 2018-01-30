from main import *

import cherrypy

cherrypy.config.update({
    'server.socket_port': 7778,
    'server.socket_host': '0.0.0.0',
    'request.show_traceback': True,
})

cherrypy.log.screen = True

import tempfile
import os.path
class App:
    @cherrypy.expose
    def index(self):
        with open("./indexpage.html", "r") as fh:
            return fh.read()
   

    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def upload(self, myFile):
        out = """<html>
        <head>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        </head>
        <body>
        """

        yield out
        #yield "<li> Uploaded: " + myFile.filename
        #save it to disk for disk operations
        disk_fh = tempfile.NamedTemporaryFile(suffix=myFile.filename, delete=False)
        disk_fh.write(myFile.file.read())
        #yield "<li>... Processing..."
        
        yield from main(disk_fh.name)
    


if __name__ == '__main__':
    cherrypy.quickstart(App())
