# -*- coding: utf-8 -*-
import Tkinter as tk, Tkconstants
import tkMessageBox, tkFileDialog
def button_lists(*columns):
    root = tk.Tk()
    button_opt = {'fill': Tkconstants.BOTH, 
                  'padx': 5, 'pady': 5}
    for functions in columns:
        column = tk.Frame(root)
        column.pack(side=Tkconstants.LEFT)
        for f in functions:
            tk.Button(column, 
                text=f.__name__, command=f).pack(**button_opt)
    root.mainloop()
def clipboard_get():
    temp = tk.Tk()
    res = temp.clipboard_get()
    temp.destroy()
    return res
def clipboard_put(text):    
    temp = tk.Tk()
    temp.clipboard_clear()
    temp.clipboard_append(text)
    temp.destroy()
def info(*texts):
    tkMessageBox.showinfo('\n'.join(texts))
def clipboard_out():
    temp = tk.Tk()
    res = temp.clipboard_get()
    temp.destroy()
    info(res)
    