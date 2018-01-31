from main import *

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

import os.path


##########################
# This is apparently threadsafe
# see list of atomic operations: 
# http://effbot.org/zone/thread-synchronization.htm
# modifying a list in place is fine

import time
import tempfile

to_expire=[]

def expiring_temp_file(name_base):
    ret = tempfile.NamedTemporaryFile(suffix=name_base, delete=False)
    to_expire.append((time.time(), ret))
    return ret

import atexit
@atexit.register
def check_expires(timeout = 2*60*60): # 2 hours
    # I don't have to really worry too much about how the deletion happens
    # User will be well and truely done with the files by the time it does
    # This is a bit hacky, but I got research work to do.

    now = time.time()
    keep_after = 0
    for ii,(create_time, fh) in to_expire:
        if create_time - now > timeout:
            fh.delete=True # let it auto delete
            keep_after = ii
        else:
            # Have found first that it not too old
            break
    for ii in range(0, keep_after):
        to_expire.pop(ii)


###################

class App:
    @cherrypy.expose
    def index(self):
        check_expires() # Someone openned the index page it is as good a time as any to check
        with open("./indexpage.html", "r") as fh:
            return fh.read()
   

    @cherrypy.expose
    @cherrypy.config(**{'response.stream': True})
    def upload(self, myFile):
        yield """<html>
        <head>
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        </head>
        <body>
        """
        #save it to disk for disk operations
        disk_fh = expiring_temp_file(myFile.filename)
        disk_fh.write(myFile.file.read())

        yield from main(disk_fh.name)
    
    
    @cherrypy.expose
    def generate_ebook(self, keep):
        if type(keep)==str:
            keep = [int(keep)] # if single argument then does not make lists

        book = cherrypy.session['book']
        outfile = expiring_temp_file(book.title + ".epub")
        rewrite_book(book, keep, outfile.name)
        return static.serve_file(outfile.name, "application/x-download", "attachment")


if __name__ == '__main__':
    cherrypy.quickstart(App())
