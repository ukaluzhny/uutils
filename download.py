from re import *
import requests
import warnings
from logbook import debug, notice, StreamHandler, FileHandler, NullHandler, DEBUG, NOTICE
from sys import stdout

from os         import listdir, mkdir, remove, chdir, getcwd
from os.path    import isdir, join, exists

r_word = compile(r'\w+', U)
r_space = compile(r'\s+', U)

def Item1(s):
    if s.startswith('"'):
        return s[1:s.find('"', 1)].strip()
    try:
        pos = r_space.search(s).start()
        return s[:pos]
    except AttributeError:
        return s
def Item2(s):
    w = Item1(s)
    s = s[len(w):].strip()
    return Item1(s)

def level(s):
    return r_word.search(s).start() // 4

downloads_home = r"C:\Users\ukaluzhn\Downloads"    
def store():
    debug("store {}, {}".format(source,dest))
    s = 'http://' + "/".join(source)
    d = join(downloads_home, *dest)
    notice("downloading {} -> {}".format(s, d))
    r = requests.get(s)
    mode = "txt"
    ext = dest[-1][ -4:]
    if ext in [".mp3", ".pdf"]: 
        mode = "bin"
    if mode == "txt":
        open(d, 'w', encoding = r.encoding).write(r.text)
    else: 
        open(d, 'wb').write(r.content)
        
source, dest = [], []
current_level = -1

debugging = False
if debugging: 
    dhandler = NullHandler(level = DEBUG)
    dhandler.format_string = '{record.message}'
    dhandler.push_application()
handler = StreamHandler(stdout, level = NOTICE)
handler.format_string = '{record.message}'
handler.push_application()


for s in open("todo.txt"):
    l = level(s)
    debug("levels {}, {}".format(current_level, l))
    s = s.strip()
    if not s: continue
    if l > current_level:
        d = join(downloads_home,  *dest)
        if not isdir(d): mkdir(d)
    if l <= current_level:  
        if current_level: store()
        source = source[:l]
        dest = dest[:l]
        debug("reduce  to {}, {}".format(source,dest))
    w1 = Item1(s)    
    source.append(w1)
    w2 = Item2(s)
    dest.append(w2 if w2 else w1)
    debug("got {}, {}".format(source, dest))
    if l != current_level:
        current_level = l
        continue
store()    
if debugging: dhandler.pop_application()
handler.pop_application()
        
            

