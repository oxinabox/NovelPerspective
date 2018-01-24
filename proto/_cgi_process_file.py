#!/usr/bin/env python3


from _cgi_main import *

import cgi, os
import cgitb; cgitb.enable()

import sys
import traceback
import io

import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)
print("Content-Type: text/html; charset=utf-8\n")
sys.stderr = sys.stdout

try:
    
    print("<html><body>")

    def get_filepath():
        form = cgi.FieldStorage()

        # A nested FieldStorage instance holds the file
        fileitem = form['file']
        if fileitem.filename:# Test if the file was uploaded
            fn = os.path.basename(fileitem.filename) # strip leading path from file name to avoid directory traversal attacks
            uploaded_file_path = os.path.join('uploads/' + fn)
            with open(uploaded_file_path, 'wb') as fout:
                while True:
                    chunk = fileitem.file.read(100000)
                    if not chunk:
                        break
                    fout.write (chunk)

            print('The file "' + fn + '" was uploaded successfully\n')
            sys.stdout.flush()
            return uploaded_file_path
##########################################
    filepath = get_filepath()
    if filepath:
        main(filepath)
    else:
        print("Error: file upload failed")
    

except:
    print("\n\n<PRE>")
    traceback.print_exc()
