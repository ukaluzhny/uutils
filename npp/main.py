from Npp import *
from bs4 import BeautifulSoup as soup
from os.path import join
from os import getcwd
print(getcwd())

import english, download, gui
import json
from codecs import open

def download_to_notepad():
    r = download.get_link()[0]
    notepad.new()
    notepad.setLangType(LANGTYPE.HTML)
    editor.appendText(r.text)
    
def list_strings_for_URL():
    r, fname, ext = download.get_link()
    tree = soup(r.text, "html.parser")
    notepad.new()
    notepad.setLangType(LANGTYPE.TXT)
    for i, s in enumerate(tree.strings):
        if i == 10000: return
        s = s.strip(" \t\r\n")
        if s:  
            editor.appendText(s)
            editor.appendText('\n')
    
def anki(separator=None):
    d = get2(separator)
    f = open(join(download.home, 'mp3', 'new.txt'), 'w', 
        encoding = 'utf-8')
    json.dump(d, f)
    f.close()
    
   
def list_common_words():
    out(english.common_words, new_window = True)
def list_user_words():
    out(english.user_words, new_window = True)
def get_common_words():
    out(english.common_words, new_window = True)
def list_user_words():
    out(english.user_words, new_window = True)
    
gui.button_lists(
# [
# load_common_words, 
# list_common_words, 
# update_common_words], 
# [
# load_user_words,
# list_user_words,
# update_user_words],
[
download_to_notepad,
download.download_to_txt_file,
download.download_to_bin_file],
[
gui.clipboard_out,
list_strings_for_URL,
anki
]
) 
