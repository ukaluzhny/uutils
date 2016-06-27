"""Debugging utulities, especially for working with large integers

"""
from logbook import StreamHandler, NullHandler, INFO, DEBUG
import sys
from random import seed as srand, getrandbits as grb
from struct import pack, unpack
from .dmath.ubits import n2words_le

  
class ConciseLog(object):
    def __init__(self, f = sys.stdout, level = "info"):
        frmt = '{record.message}'
        if level == "info":
            self.debug = NullHandler(level = DEBUG)
            self.info = StreamHandler(f, level = INFO, format_string = frmt)
        else:    
            self.debug = StreamHandler(f, level = DEBUG, format_string = frmt)
            self.info = None
    def __enter__(self):
        self.debug.__enter__()
        if self.info: self.info.__enter__()
    def __exit__(self, exc_type, exc_value, traceback):
        if self.info: 
            self.info.__exit__(exc_type, exc_value, traceback)
        self.debug.__exit__(exc_type, exc_value, traceback)
    
def NullLog():
    return NullHandler(level = DEBUG)
    
# Example
# seed = t.tester(1, test, indx = 0, seed = None, fname = "")   
# seed = t.tester(20, test, indx = None, seed = None, fname = "t.log", L = 120)   
def tester(N, func, indx = None, seed = None, fname = "", **keywargs):
    """generic macro for testing, 
    runs the function N times with keywargs
    if indx given, then switches on the debug output for that run
    if seed given, uses it for random generation,
       otherwise generates and returns the random seed
    """
    print("running {} with {}".format(func.__name__, keywargs))
    if not seed:
        seed = grb(32)
    srand(seed)
    f = open(fname, 'w') if fname else sys.stdout
    try:
        for i in range(N):
            print(i, end = '')
            if indx != i:
                with NullLog():
                    func(**keywargs)
            else:
                with ConciseLog(f):
                    func(**keywargs)
    except Exception as e:
        print('\n', repr(e))
    finally:
        if f != sys.stdout: f.close()
        print()
        return seed
        
