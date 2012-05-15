# -*- coding: utf-8 -*-
"""\
This module provides tools to work with text
including Unicode
>>> text_e = 'I said: "it should be easy"'
>>> Word1(text_e) == 'I'
True
>>> Word2(text_e) == 'said'
True
>>> Word3(text_e) == '"it should be easy"'
True
>>> Payload(text_e, '"', '"') == 'it should be easy'
True
>>> s = "0one23four5 8"
>>> t = ['', '0', 'one', '2', '', '3', 'four', '5', ' ', '8', '']
>>> splitted(s, ['\d']) == t
True
>>> Erase(s, '\d\d', ' ') == '0onefour58'
True
>>> myhex(576, 5) == '0x00240'
True
>>> myhex(576, 5, True) == '00240'
True
>>> text_h = 'כלומר, אין שום משמעות מיוחדת לביטוי "אין זו כריתות"'
>>> Word1(text_h) == 'כלומר'
True
>>> Word2(text_h) == 'אין'
True
>>> Word3(text_h)  == 'שום משמעות מיוחדת לביטוי "אין זו כריתות"'
True
>>> Payload(text_h, '"', '"') == 'אין זו כריתות'
True
>>> d = ReD({'אין': 'not', 'זה': 'it'}, U)
>>> d(text_h) == u'כלומר, not שום משמעות מיוחדת לביטוי "not זו כריתות"'
True
>>> del d['אין']
>>> d(text_h) == text_h
True
>>> d['אין'] = 'not'
>>> d(text_h) == u'כלומר, not שום משמעות מיוחדת לביטוי "not זו כריתות"'
True
>>> t = ['כלומר, א', 'ין', ' שום משמעות מ', 'יו', 'חדת לב', 'יט', 'ו', 'י ', '"א', 'ין', ' זו כר', 'ית', 'ות"']
>>> splitted(text_h, ['י.']) == t
True
"""
from __future__ import division, print_function, unicode_literals
from re import *
import warnings
r_word = compile(r'\w+', U)
heb_colon = u"\u05c3"

def Word1(s):
    try:
        return r_word.search(s).group()
    except AttributeError:
        return ''
def Word2(s):
    try:
        pos = r_word.search(s).end()
        return r_word.search(s[pos + 1:]).group()
    except AttributeError:
        return ''
def Payload(l, after  = ' ', before = ''):
    offset = len(after)
    pos = l.find(after)
    pos_l = -1
    if before:
        pos_l = l.find(before, pos+1)
    if pos_l == -1: 
        pos_l = len(l)
    return l[pos + offset:pos_l].strip() if pos != -1 else ''
def Word3(s):
    "Actually, returns everything after the second word"
    pos = r_word.search(s).end() + 1
    s = s[pos:].strip()
    return Payload(s)

def WordL(s): 
	last_word = compile(r'\w+$', U)
    try:
        return last_word.search(s).group()
    except AttributeError:
        return ''

class ReD(object):
    def __init__(self, defs = {}, flags = 0):
        self.defs = defs
        self.re_defs = None
        self.flags = flags
    def __setitem__(self, key, val):
        self.defs[key] = val
        self.re_defs = None
    def __contains__(self, key):
        return key in self.defs
    def __delitem__(self, key):
        try:
            del self.defs[key]
            self.re_defs = None
        except KeyError:
            warnings.warn("Tried to undef {}".format(key))
    def __call__(self, text):
        if not self.re_defs and self.defs:
            v = '|'.join(self.defs.keys())
            v = r'\b({})\b'.format(v)
            self.re_defs = compile(v, self.flags)
        if self.defs:
            for i in range(100):
                t = self.re_defs.sub(lambda m: self.defs[m.group(0)], text)
                if t == text:
                    break
                text = t
            if i >= 99:
                raise Exception("Possibly iterative definition in {}".format(self.defs)) 
        return text
    def __repr__(self):
        return repr(self.defs)

def splitted(s, keywords_list, flags = 0):
    r = compile('({})'.format('|'.join(keywords_list)), M|flags)
    return r.split(s)
    
def Erase(s, *l):
    for i in l:
        r = compile(i)
        s = r.sub('', s)
    return s
def myhex(x, n, bare = False):
    s = (hex(x)[2:]).replace("L", "")
    form = '{}' if bare else '0x{}'
    return form.format(s.zfill(n))
def reverse_word_order(w):
   return ' '.join(reversed(w.split()))
  
if __name__ == "__main__":
   import doctest
   doctest.testmod()
   raw_input("Press 'Enter'...")
 
