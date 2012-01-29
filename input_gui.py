﻿# -*- coding: utf-8 -*-
from Tkinter import *
import winsound
class OptionButton(Button):
    def __init__(self, data,
            row, table):
        try:
            text2show, value = data
        except (ValueError, TypeError):
            text2show  = data
            value = data
        def f(x = value, table = table):
            table.action(x)
        Button(row, text = text2show, command = f).pack(
            side = row.direction, padx = 1, pady  = 1)
class ExitButton(Button):
    def __init__(self, master, root,
            text2show = 'quit'):
        Button(master, text = text2show,
                command = root.destroy).pack(side = 'bottom', fill = 'x')
class SoundButton(Button):
    def __init__(self, fname, master, text2show = 'sound'):
        def f(name = fname):
            winsound.PlaySound(name, winsound.SND_FILENAME)
        Button(master, text = text2show,
            command = f).pack(side = master.direction)

class RowOfButtons(Frame):
    def __init__(self, buttons, master):
        self.direction = master.direction
        Frame.__init__(self, master)
        for b in buttons:
            OptionButton(b, self, master)
        self.pack(side = 'top')

class TableOfButtonOptions(Frame):
    def __init__(self, rows, action, root,
            direction = 'left'):
        Frame.__init__(self, root)
        self.action = action
        self.direction = direction
        for row in rows:
            RowOfButtons(row, self)
        ExitButton(self, root)
        self.pack()

class Result(object):
    def __init__(self, root):
        self.root = root
        self.val = None
    def __call__(self, x):
        self.val = x
        self.root.destroy()

def get_option(table):
    root = Tk()
    res = Result(root)
    gui = TableOfButtonOptions(table, res, root)
    gui.mainloop()
    return res.val

class StrInputWindow(Frame):
    def __init__(self, res, master=None):
        self.res = res
        Frame.__init__(self, master)
        self.pack()

        self.entrythingy = Entry()
        self.entrythingy.pack()
        self.contents = StringVar()
        self.entrythingy["textvariable"] = self.contents
        self.entrythingy.bind('<Key-Return>',
                              self.return_value)
        ExitButton(master)
    def return_value(self, event):
        self.res.val = self.contents.get()
def StrInput():
    root = Tk()
    res = Result()
    app = StrInputWindow(res, master=root)
    app.mainloop()
    return res

def rw(w):
   return ' '.join(reversed(w.split()))
       