# -*- coding: utf-8 -*-
"""This module provides tools to work with (Unicode) text
   Word1, Word2, Word3etc and Payload
    >>> text_e = 'I said: "it should be easy"'
    >>> Word1(text_e) == 'I'
    True
    >>> Word2(text_e) == 'said'
    True
    >>> Word3etc(text_e) == ': "it should be easy"'
    True
    >>> Payload(text_e, '"', 'easy') == 'it should be'
    True

    >>> text_h = 'כלומר, אין שום משמעות מיוחדת לביטוי "אין זו כריתות"'
    >>> Word1(text_h) == 'כלומר'
    True
    >>> Word2(text_h) == 'אין'
    True
    >>> Word3etc(text_h)  == 'שום משמעות מיוחדת לביטוי "אין זו כריתות"'
    True
    
    >>> s = "0one23four5 8"
    >>> t = ['', '0', 'one', '23', 'four', '5 ', '', '8', '']
    >>> Splitted(s, ['\d+']) == t
    True
    >>> Erase(s, '\d+') == 'onefour'
    True
    
    ### hexstr(576, 5) == '0x00240'
    True
    ### hexstr(576, 5, True) == '00240'
    True
    ### d = ReD({'אין': 'not', 'זה': 'it'}, U)
    ### d(text_h) == u'כלומר, not שום משמעות מיוחדת לביטוי "not זו כריתות"'
    True
    ### del d['אין']
    ### d(text_h) == text_h
    True
    ### d['אין'] = 'not'
    ### d(text_h) == u'כלומר, not שום משמעות מיוחדת לביטוי "not זו כריתות"'
    True
    ### t = ['כלומר, א', 'ין', ' שום משמעות מ', 'יו', 'חדת לב', 'יט', 'ו', 'י ', '"א', 'ין', ' זו כר', 'ית', 'ות"']
    ### splitted(text_h, ['י.']) == t
    True
"""
import re
import warnings
r_word = re.compile(r'\w+', re.UNICODE)
heb_colon = u"\u05c3"

def Word1(s):
    try:
        return r_word.search(s).group()
    except AttributeError:
        return ''
def Word2(s):
    try:
        pos = r_word.search(s).end()
        return r_word.search(s[pos:]).group()
    except AttributeError:
        return ''
def Payload(l, after  = ' ', before = ''):
    pos = l.find(after)
    if pos == -1: return ""
    offset = len(after)
    pos_l = -1
    if before:
        pos_l = l.find(before, pos + offset)
    if pos_l == -1: 
        pos_l = len(l)
    return l[pos + offset : pos_l].strip()
def Word3etc(s):
    "Returns everything after the second word"
    pos1 = r_word.search(s).end()
    pos2 = r_word.search(s[pos1:]).end()
    return s[pos1 + pos2:].strip()

def Splitted(s, separator_list, flags = 0):
    # S: without this flag, '.' will match anything except a newline
    separators = '|'.join(r'\s*{}\s*'.format(i) 
        for i in separator_list)
    separators = "({}|\s+)".format(separators)
    r = re.compile(separators, re.DOTALL | re.MULTILINE | flags)
    return r.split(s)
def Erase(s, *l):
    words = '|'.join(r'\s*{}'.format(i) for i in l)
    r = re.compile(words, re.MULTILINE)
    s = r.sub('', s)
    return s

"""
class ReD(object):
    def __init__(self, defs = None, flags = 0):
        self.d = defs if defs else dict()
        self.re_defs = None
        self.flags = flags
    def __setitem__(self, key, val):
        self.d[key] = val
        self.re_defs = None
    def __getitem__(self, key):
        return self.d[key]
    def __iter__(self):
        return iter(self.d)
    def __contains__(self, key):
        return key in self.d
    def __delitem__(self, key):
        try:
            del self.d[key]
            self.re_defs = None
        except KeyError:
            warnings.warn("Tried to undef {}".format(key))
    def __call__(self, text):
        if not self.re_defs and self.d:
            v = '|'.join(self.d.keys())
            v = r'\b({})\b'.format(v)
            self.re_defs = compile(v, self.flags)
        if self.d:
            for i in range(100):
                t = self.re_defs.sub(lambda m: self.d[m.group(0)], text)
                if t == text:
                    break
                text = t
            if i >= 99:
                raise Exception("Possibly iterative definition in {}".format(self.d)) 
        return text
    def __repr__(self):
        return repr(self.d)

def hexstr(x, n = 0, bare = False):
    s = '{:x}'.format(x)
    s = s.zfill(n)
    if not bare: s = '0x' + s
    return s
def binstr(x, n = 0, bare = False):
    s = '{:b}'.format(x)
    s = s.zfill(n)
    if not bare: s = '0b' + s
    return s
def reverse_word_order(w):
   return ' '.join(reversed(w.split()))
"""
    
if __name__ == "__main__":
   import doctest
   doctest.testmod()
 
