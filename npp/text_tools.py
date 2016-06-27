_separator = '\t'

def split2lists(text, separator=None):
    "spits the text by the separator"
    if separator:
        global _separator
        _sep = _separator
        _separator = separator
    res = []
    for line in text.splitlines():
        while line.endswith(_separator):
            line = line[:-len(_separator)]
        line = [w.strip() for w in line.split(_separator)] 
        if len(line) == 1: line = line[0]
        if line: res.append(line)
    if len(res) == 1: res = res[0]
    if separator:
        _separator = _sep
    return res

def join2text(item, separator=None):
    "returns the text "
    if separator:
        global _separator
        _sep = _separator
        _separator = separator
    if item == str(item): #str, unicode
        res = item + _separator
    else:
        if type(item) == dict:
            item = item.items()
        try:
            res = '\n' + ''.join(join2text(i) for i in item) + '\n'
        except TypeError:
            res = str(item) + _separator
    if separator:
        _separator = _sep
    return res.replace('\n\n', '\n')

import re
r_word = re.compile(r'\w+', re.UNICODE)
def words(s):
    for m in r_word.finditer(s):
        yield m.group(0)        
