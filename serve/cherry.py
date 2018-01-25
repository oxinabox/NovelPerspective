from main import *

import cherrypy

cherrypy.config.update({
    'server.socket_port': 7778,
    'server.socket_host': '0.0.0.0'
})

cherrypy.log.screen = True

import cherrypy
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
        <body>
            myFile filename: %s<br />
            myFile mime-type: %s
        </body>
        </html>"""

        yield out % (myFile.filename, myFile.content_type)

        #save it to disk for disk operations
        disk_fh = tempfile.NamedTemporaryFile(suffix=myFile.filename, delete=False)
        disk_fh.write(myFile.file.read())
        yield "<br>... Processing...</br>"
        
        yield from main(disk_fh.name)
    


if __name__ == '__main__':
    cherrypy.quickstart(App())
