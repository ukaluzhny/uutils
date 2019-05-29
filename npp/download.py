# -*- coding: utf-8 -*-
from gui import *
from bs4 import BeautifulSoup as soup
import requests as rg
from codecs import open
from random import getrandbits as grb 

home = r"C:\Users\ukaluzhn\Downloads"
def get_link():
    "returns the file, the file name and the file name extension"
    link = clipboard_get()
    if not link.startswith("http://") and not link.startswith("https://"):
        link = "http://" + link
    fname = link[link.rfind('/') + 1:]
    pos = fname.find('.')
    fname, ext = fname[:pos], fname[pos:]
    return rg.get(link), fname, ext

def download_to_file(mode):
    r, fname, ext = get_link()
    d = tkFileDialog.asksaveasfilename(title = "Saving {} file".format(ext),
        initialdir=home, defaultextension=ext, initialfile=fname)
    if d: 
        gui.info(d, r.encoding)    
        if mode == 'bin':
            open(d, 'wb').write(r.content)
        else: 
            open(d, 'w', encoding = r.encoding).write(r.text)
        clipboard_put(d)
    else: 
        tkMessageBox.showerror(ext, "No file chosen")
    
def download_to_bin_file():
    download_to_file("bin")
def download_to_txt_file():
    download_to_file("txt")

def get_mp3(text, fname=None):
    url  = ("[InternetShortcut]\nURL=http://translate.google.com/translate_tts?ie=UTF-8&q=" + 
        "{}&tl=en&client=me" + hex(grb(16))[2:])
    response  = rg.get(url.format("+".join(text.split())))
    if response.status_code == 503: 
        print("503")
        return False
    if( fname==None ):
        fname = "_".join(text.split())
    open("{}.mp3".format(fname),"wb").write(response.content)
    return True
        
        
# requests
# Passing Parameters In URLs
# >>> payload = {'key1': 'value1', 'key2': 'value2'}
# >>> r = requests.get("http://httpbin.org/get", params=payload)
# POST requests
# >>> payload = {'key1': 'value1', 'key2': 'value2'}
# >>> r = requests.post("http://httpbin.org/post", data=payload)

# BS iterators
# .contents: tag’s direct children list.
# .children: iterator over tag’s direct children
# .descendants: iterator over all tag’s children
# .string: if a tag has only one child, which is a NavigableString
# .strings and stripped_strings generators
    
# BS Searching by filters
# A string:
    # soup.find_all('b')
    # # [<b>The Dormouse's story</b>]
# 2. A regular expression
    # import re
    # for tag in soup.find_all(re.compile("^b")):
        # print(tag.name)
    # # body
    # # b
# A list: match against any item in that list.
    # soup.find_all(["a", "b"])
    # # [<b>The Dormouse's story</b>,
    # #  <a class="sister" href="http://example.com/elsie" id="link1">Elsie</a>,
    # #  <a class="sister" href="http://example.com/lacie" id="link2">Lacie</a>,
    # #  <a class="sister" href="http://example.com/tillie" id="link3">Tillie</a>]
# True
    # for tag in soup.find_all(True):
        # print(tag.name)
# A function
    # def has_class_but_no_id(tag):
        # return tag.has_attr('class') and not tag.has_attr('id')
    # soup.find_all(has_class_but_no_id)
    # # [<p class="title"><b>The Dormouse's story</b></p>,
    # #  <p class="story">Once upon a time there were...</p>,
    # #  <p class="story">...</p>]

