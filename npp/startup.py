# The lines up to and including sys.stderr should always come first
import sys
from Npp import *
# Set the stderr to the normal console as early as possible, in case of early errors
sys.stderr = console

# Define a class for writing to the console in red
class ConsoleError(object):
	def __init__(self):
		global console
		self._console = console;
		
	def write(self, text):
		self._console.writeError(text);
		
# Set the stderr to write errors in red
sys.stderr = ConsoleError()
# This imports the "normal" functions, including "help"
import site
# This sets the stdout to be the currently active document,
sys.stdout = editor

from text_tools import split2lists, join2text
from itertools import izip_longest

def out(item, separator=None, new_window=False):
    "prints the item to a (new) notepad window"
    if new_window: 
        notepad.new()
        notepad.setLangType(LANGTYPE.TXT)
    editor.appendText(join2text(item, separator))

def get(separator=None):
    text = editor.getSelText()
    if text == '': 
        text = editor.getText()
    return split2lists(text, separator)

def error(item):
    sys.stderr.write(item)

def switch_view():
    c = 1 - notepad.getCurrentView() 
    a = notepad.getCurrentDocIndex(c)
    if a == 0xffffffffL: return False
    notepad.activateIndex(c, a)
    return True
    
def exp_sel(onlyWordCharacters = True):
    "expands the selection to the word borders"
    a = editor.getAnchor()
    b = editor.getCurrentPos()
    if b < a: a, b = b, a
    a = editor.wordStartPosition(a, onlyWordCharacters)
    b = editor.wordEndPosition(b, onlyWordCharacters)
    editor.setCurrentPos(a)
    editor.setAnchor(b)
    return editor.getSelText()
    
def get2(separator=None):
    a = get(separator)
    if switch_view():
        b = get(separator)
        if len(keys) != len(values):
            error('Different lengths for keys and values.')
        else: 
            return izip_longest(a, b, fillvalue=' ')
    else: return a

