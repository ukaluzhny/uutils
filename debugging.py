from logbook import StreamHandler, NullHandler, info, debug, INFO, DEBUG
import sys
from random import seed as srand, getrandbits as grb
from struct import pack, unpack
from .dmath.ubits import n2words_le

silent_debug = NullHandler(level = DEBUG)
log = StreamHandler(sys.stdout, level = DEBUG, format_string = '{record.message}')
log.push_application()

def debug_on():
    log.push_application()
    
def debug_off():
    silent_debug.pop_application()

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
    log = StreamHandler(f, level = INFO, format_string = '{record.message}')
    try:
        for i in range(N):
            print(i, end = '')
            if indx != i:
                with NullHandler(level = DEBUG), log:
                    func(**keywargs)
            else:
                with StreamHandler(f, level = DEBUG, format_string = '{record.message}'):
                    func(**keywargs)
    except Exception as e:
        print('\n', repr(e))
    finally:
        if f != sys.stdout: f.close()
        print()
        return seed
        

def n2f(f, *p):
    while p:
        (x, l), p = p[:2], p[2:]
        f.write(pack('{}I'.format(l), *n2words_le(x, l)))
        
def a2n(l):
    res = 0
    for i in reversed(l): 
        res <<= 32
        res |= i
    return res
    
def f2n(f, *p):
    res = []
    for l in p:
        x = unpack('{}I'.format(l), f.read(4*l))
        res.append(a2n(x))
    return res

def read_ints(fname, *lens):
    return f2n(open(fname, 'rb'), *lens)
