import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import subprocess
import os.path
import copy
import shutil
import shlex

"""
Converts the ebook at input_filepath, writing the output to output_filepath
Lazy/Async, yields outputs one line at a time til done.
"""
def convert_book(input_filepath, output_filepath, reprocess_epub=False, heuristics=False, split_scenes=False):
    input_ext = os.path.splitext(input_filepath)[1]
    output_ext = os.path.splitext(output_filepath)[1]
    assert (output_ext == ".epub")
    reprocess_epub = reprocess_epub or heuristics or split_scenes
    # if others selected then must reprocess epub
    if input_ext == ".epub" and not(reprocess_epub):
        shutil.copyfile(input_filepath, output_filepath)
        yield "No conversion required"
        return
    else:
        cmd = ['ebook-convert',
               shlex.quote(input_filepath),
               shlex.quote(output_filepath)]

        if heuristics:
            cmd.append('--enable-heuristics')


        extra_split_rules = ""
        if split_scenes:
            extra_split_rules = "  or @class = 'scenebreak'"

        cmd.append("--chapter")  # Default chapter break rules, but with '.scenebreak' added :
        cmd.append(""" "//*[ """
                        + """((name()='h1' or name()='h2' or name()='h3' or name()='h4' or name()='h5' or name()='h6') """
                             + """and re:test(., '\s*((chapter|book|section|part)\s+)|((prolog|prologue|epilogue)(\s+|$))', 'i')) """
                        + """ or @class = 'chapter' %s ]" """ % extra_split_rules)

        # Don't use shlex.quote as that breaks other things so calibre can not parse the above


        cmd =  " ".join(cmd)
        yield cmd + "\n\n"
        with subprocess.Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, #use same stream
                bufsize=1,
                universal_newlines=False,
                shell=True,
                ) as proc:
            for line in proc.stdout:
                yield line.decode(encoding='UTF-8',errors='replace')
            if proc.wait() != 0:
                raise subprocess.CalledProcessError(proc.returncode, cmd)
            yield ""





def is_not_chapter(item):
    return item.get_type() != ebooklib.ITEM_DOCUMENT



"""Given a book, returns a function which will return a key such than when sorted"""
def get_spine_order_key(book):
    assert(type(book) == epub.EpubBook)
    spine_keys = {id:(ii,id) for (ii,(id,show)) in enumerate(book.spine)}
    past_end = len(spine_keys)
    return lambda itm: spine_keys.get(itm.get_id(), (past_end,itm.get_id()))


def load_chapters(book):
    assert(type(book) == epub.EpubBook)

    spine_key = get_spine_order_key(book)
    indexed_items= sorted(
        enumerate(book.items),
        key=lambda x: spine_key(x[1])) # x = (true_ind, item)

    indexes = []
    texts = []
    for (ii,ch) in indexed_items:
        if is_not_chapter(ch):
            continue

        text = BeautifulSoup(ch.get_content(),"lxml").text
        indexes.append(ii)
        texts.append(text)
    return texts, indexes


def load_book(filepath):
    return epub.read_epub(filepath)




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
