# -*- coding: utf-8 -*-
from Tkinter import *
import winsound
class InputButton(Button):
    def __init__(self, text2show, input_value, 
            master, root = None):
        def f(x = input_value, myroot = master if not root else root):
            myroot.action(x)
        Button(master, text = text2show, command = f).pack(
            side = master.direction, padx = 1, pady  = 1) 
class ExitButton(Button):
    def __init__(self, master, root = None, show_text = 'quit'):
        #def f(myroot = master if not root else root):
            #myroot.destroy()
            #exit()
        if not root: root = master
        Button(master, command = root.destroy, 
            text = show_text).pack(
            side = master.direction, fill = 'x') 
class SoundButton(Button):
    def __init__(self, fname, master, my_text = 'לשמוע'):
        def f(name = fname):
            winsound.PlaySound(name, winsound.SND_FILENAME)
        Button(master, text = my_text, command = f).pack(
            side = master.direction) 
        
class RowOfButtons(Frame):
    def __init__(self, buttons, master, 
            direction = 'left', root = None):
        if not root: root = master
        self.direction = direction
        Frame.__init__(self, master)
        for text2show, input_value in buttons:
            InputButton(text2show, input_value, self, root)
        self.pack(side = master.direction)
        
class TableOfButtonInputs(Frame):
    def __init__(self, rows, master, 
            direction = 'left', root = None):
        if not root: root = master
        Frame.__init__(self, master)
        self.direction = 'top'
        for row in rows:
            RowOfButtons(row, self, direction, root)
        ExitButton(self, root)
        self.pack()
        

        
