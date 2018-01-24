import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import subprocess
import os.path

"""Returns path to book in epub format"""
def convert_book(filepath):
    basepath, ext = os.path.splitext(filepath)
    if ext == ".epub":
        return filepath
    else:
        targetpath = basepath+".epub"
        subprocess.check_call(['ebook-convert', filepath, targetpath, '--enable-heuristics'])
        return targetpath
    
        
        
def is_not_chapter(item):
    return item.get_type() != ebooklib.ITEM_DOCUMENT



def load_epub(book_filename):
    book = epub.read_epub(book_filename)
    indexes = []
    texts = []
    for (ii,ch) in enumerate(book.items):
        if is_not_chapter(ch):
            continue
               
        text = BeautifulSoup(ch.get_content(),"lxml").text
        if len(text)<2000:
            continue
               
        indexes.append(ii)
        texts.append(text)
    return texts, indexes


def load_book(filepath):
    return load_epub(convert_book(filepath))
    