import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import subprocess
import os.path
import copy
import shutil

"""
Converts the ebook at input_filepath, writing the output to output_filepath
If generate_output yields it one line at a time.
Otherwise returns None.
"""
def convert_book(input_filepath, output_filepath, reprocess_epub=False, heuristics=False, split_scenes=False, generate_output=False):
    input_ext = os.path.splitext(input_filepath)[1]
    output_ext = os.path.splitext(output_filepath)[1]
    assert (output_ext == ".epub")
    if input_ext == ".epub" and not(reprocess_epub):
        shutil.copyfile(input_filepath, output_filepath)
        if generate_output:
            yield "No conversion required"
        return
    else:
        cmd = ['ebook-convert', input_filepath, output_filepath]
        
        if heuristics:
            cmd.append('--enable-heuristics')

        if split_scenes:
            cmd.append("--chapter")
            cmd.append(""" "//*[((name()='h1' or name()='h2') and re:test(., '\s*((chapter|book|section|part)\s+)|((prolog|prologue|epilogue)(\s+|$))', 'i')) or @class = 'chapter' or @class = 'scenebreak']" """)
            # Default chapter break rules, but with '.scenebreak' added
            cmd.append("--chapter-mark none")
            # if we are spliting on scenes then don't want to add extra page breaks to for each scene
        
        if not(generate_output):
            subprocess.check_call(cmd)
        else:
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as proc:
                for line in proc.stdout:
                    yield line
            
        
    
        
        
def is_not_chapter(item):
    return item.get_type() != ebooklib.ITEM_DOCUMENT



def load_chapters(book):
    assert(type(book) == epub.EpubBook)
    
    indexes = []
    texts = []
    for (ii,ch) in enumerate(book.items):
        if is_not_chapter(ch):
            continue
  
        text = BeautifulSoup(ch.get_content(),"lxml").text
        indexes.append(ii)
        texts.append(text)
    return texts, indexes


def load_book(filepath):
    return epub.read_epub(convert_book(filepath))
    



def rewrite_book(book, keep_chapter_inds, new_filename):
    assert(type(book) == epub.EpubBook)
    new_book = copy.deepcopy(book)
    new_book.items = []
    for (ii,ch) in enumerate(book.items):
        if (is_not_chapter(ch)   # keep all non-chapters
            or ii in keep_chapter_inds):
           new_book.items.append(ch)
    
    new_book.title+=": (some chapters removed)"
    epub.write_epub(new_filename, new_book, {})
    return new_filename
