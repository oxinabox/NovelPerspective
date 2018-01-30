import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import subprocess
import os.path
import copy


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
