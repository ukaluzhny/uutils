# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import os
try: import mp3play as mp3
except ImportError: pass
from Tkinter import *
from math import sqrt
from subprocess import Popen
from codecs import open as copen
def uopen(fname, mode = 'r'):
    return copen(fname, mode, encoding = "utf-8")
    
class option_button(Button):
    def __init__(self, master, data):
        ret_value = data
        try:
            ret_value, text2show = ret_value
        except (ValueError, TypeError):
            text2show  = ret_value
        def action(x = ret_value, master = master):
            master.action(x)
        Button(master, text = text2show, command = action).pack(
            side = master.direction, padx = 1, pady  = 1)
class exit_button(Button):
    def __init__(self, master, text2show = 'quit'):
        Button(master, text = text2show, command = master.destroy
                ).pack(side = 'bottom', fill = 'x')
class row_of_buttons(Frame):
    def __init__(self, master, buttons):
        self.direction = master.direction
        self.action = master.action
        Frame.__init__(self, master)
        for b in buttons:
            option_button(self, b)
        self.pack(side = 'top')
class table_of_buttons(Frame):
    def __init__(self, root, buttons, action,
            direction = 'left', row_len = None):
        Frame.__init__(self, root)
        self.action     = action
        self.direction  = direction
        if not row_len:
            row_len = int(sqrt(len(buttons)))
        while buttons:
            row_of_buttons(self, buttons[:row_len])
            buttons = buttons[row_len:]
        self.pack()

def get_option(options, title = "get_option", 
        header = None, direction = 'left'):
    root = Tk()
    root.wm_title(title)
    if header:
        Label(root, text = header).pack(side = 'top')
    def action(n, res = root):
        res.res = n
        res.destroy()
    gui = table_of_buttons(root, list(enumerate(options)),
        action, direction)
    gui.mainloop()
    return options[root.res]

def get_unicode(title = "get_unicode", header = None):
    root = Tk()
    root.wm_title(title)
    if header:
        Label(root, text = header).pack(side = 'top')
    gui = Entry()
    gui.pack()
    contents = StringVar()
    def action(event, res = root):
        res.res = contents.get()
        res.destroy()
    gui["textvariable"] = contents
    gui.bind('<Key-Return>', action)
    gui.mainloop()
    return root.res

def print_unicode(*l):
    root = Tk()
    for i in l:
        Label(root, text = unicode(i)).pack()
    exit_button(root)
    root.mainloop()

class gui_counter(object):
    def __init__(self, master, frmt, 
            side, val, font = '18pt'):
        self.label = Label(master, font = font)
        self.label.pack(side = side)
        self.value = 0
        self.frmt = frmt
        self.label['text'] = frmt.format(self.value)
    def __iadd__(self, val):
        self.value += val
        self.label['text'] = self.frmt.format(self.value)
        return self

class SlicedMp3(object):
    def __init__(self, name):
        self.name = name
        self.mp = mp3.load(name+".mp3")
        self.read_slicing()
    def fname (self):
        return "{}.slc".format(self.name)
    def read_slicing(self):
        try:
            slicing = open(self.fname()).read()
        except IOError:
            self.edit_slicing()
            raise Exception("Prepare a slicing for {}".format(self.name))
        slicing = "[0, {}]".format(slicing)
        slicing = eval(slicing)
        slicing = map(lambda x: int(float(x)*100), slicing)
        slicing.append(self.mp.milliseconds())
        self.slicing = slicing 
        self.mtime = os.stat(self.fname()).st_mtime
    def edit_slicing(self):
        audacity = r'"C:\Program Files\Audacity\audacity.exe" '
        notepad  = r'"C:\Program Files\Notepad++\notepad++.exe" '
        Popen(audacity + '{}.mp3'.format(self.name))
        Popen(notepad + self.fname())
    def __call__(self, ind):
        if self.mtime < os.stat(self.fname()).st_mtime:
            self.read_slicing()
        self.mp.play(*self.slicing[ind:ind+2])
        while self.mp.isplaying(): pass
    def __len__(self):
        return len(self.slicing)-1

class speak_button(Button):
    def __init__(self, master, audio_file, 
        side = 'top', font = '14pt'):
        self.mp = audio_file
        Button(master, font = font).pack(side = side, padx = 1, pady  = 1)
    def define (self, text2show, ind):
        def action(mp = self.mp, ind = ind):
            mp(ind)
        self["command"] = action
        self["text"] = text2show
        