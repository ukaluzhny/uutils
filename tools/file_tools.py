from re import *
import warnings
from logbook import debug, notice, StreamHandler, FileHandler, NullHandler, DEBUG, NOTICE
from sys import stdout

from os         import listdir, mkdir, remove, chdir, getcwd
from os.path    import isdir, join, exists

def save_with_backup(fname, s):
    backup = "{}_backup{}".format(*splitext(fname))
    if exists(fname):
        if exists(backup): remove(backup)
        open(backup, 'w').write(open(fname).read())
    open(fname, 'w').write(s)

r_word = compile(r'\w+', U)
r_space = compile(r'\s+', U)

def level(s):
    return r_word.search(s).start() // 4

        
dest = []
current_level = -1

debugging = False
if not debugging: 
    dhandler = NullHandler(level = DEBUG)
    dhandler.push_application()
handler = StreamHandler(stdout, level = NOTICE)
handler.format_string = '{record.message}'
handler.push_application()


for s in open("todo.txt"):
    l = level(s)
    debug("levels {}, {}".format(current_level, l))
    s = s.strip()
    if not s: continue
    d = join(downloads_home,  *dest)
    if l > current_level:
        if not isdir(d): mkdir(d)
    if l <= current_level:  
        if current_level: 
            if '.' in d: store(d)
            else: 
                if not isdir(d): mkdir(d)
        dest = dest[:l]
        debug("reduce  to {}".format(dest))
    dest.append(s)
    if l != current_level:
        current_level = l
        continue
store(d)    
if debugging: dhandler.pop_application()
handler.pop_application()
        
            

