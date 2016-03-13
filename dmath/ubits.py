# -*- coding: utf-8 -*-
"""operations with bits
 hw(x): hamming weight of 32 LS bits of x  
  x may be an object with 'value' or an iterable.
  >>> hw(0x12345) == 7
  True
  >>> hw([0x1234, 5]) == 7
  True

 lsw(x): least significant word of x
  >>> lsw(0x123456789a) == 0x3456789a
  True
  
 msbits(x, x_bitlen = None, l = 32): l most significant bits of x
  >>> msbits(0xf23456789a) == 0xf2345678
  True
  >>> msbits(0x123456789a, 64) == 0x12
  True
  >>> msbits(0x123456789a, 37, 9) == 0x123
  True

 lb(x): the least significant bit set in x
  >>> lb(0x1230) == 0x10
  True

 Iterators:
  for a 32-bit integer, iterate:
   over bytes in BE order
    >>> [hex(b) for b in bytes_be(0x12345678)]
    ['0x12', '0x34', '0x56', '0x78']

   over bytes in LE order
    >>> [hex(b) for b in bytes_le(0x12345678)]
    ['0x78', '0x56', '0x34', '0x12']

   over nibbles in BE order
    >>> [hex(b) for b in nibbles_be(0x12345678)]
    ['0x1', '0x2', '0x3', '0x4', '0x5', '0x6', '0x7', '0x8']

   over nibbles in LE order
    >>> [hex(b) for b in nibbles_le(0x12345678)]
    ['0x8', '0x7', '0x6', '0x5', '0x4', '0x3', '0x2', '0x1']

  bytes2words(list_of_bytes): to list of words, both LE
   >>> it = bytes2words([0x44,0x5E,0x46,0x76,0x4A,0x05])
   >>> list(it) == [0x76465e44,0x0000054a]
   True
  
  n2words_le(n, lwords = None): split an integer into a LE list of words
   >>> it = n2words_le(0x1234567890, 3)
   >>> list(it) == [0x34567890,0x12,0]
   True
 
 masks(m, n): iterates through numbers with m out of n bits set
  >>> list(masks(2, 3))
  [3, 5, 6]
  
 products(subdim, dim): iterates through all subdim subspaces 
  of the dim-dimensional cube.  Returns (mask, v), so
  that a subspace is defined as {x| x & mask == v}.
  >>> list(products(2,3))[:7]
  [(3, 0), (3, 1), (3, 2), (3, 3), (5, 0), (5, 1), (5, 4)]

 class Permutation: for shuffling according to list-defined perm. 
    >>> a = Permutation([1,3,2,0])
    >>> b = Permutation([1,0,3,2])
    >>> l = ['a','b','c','d']    
    >>> list((a*b)(l)) == list(a(list(b(l))))
    True
    >>> a+b
    1,3,2,0,5,4,7,6
    >>> a*(~a)
    0,1,2,3
    
TBD: tests for Plain, Flip, Deal, Shuffler
"""

def hw(x):
    'hamming weight'
    if x == 0: return 0
    if hasattr(x, 'value'):
        x = x.value
    if hasattr(x, '__iter__'):
        return sum([hw(i) for i in x])
    m2  = 0x33333333
    m4  = 0x0f0f0f0f
    h01 = 0x01010101
    x -= (x >> 1) & 0x55555555 #put count of each 2 bits
    x =  (x & m2) + ((x >> 2) & m2) #put count of each 4 bits
    x =  (x + (x >> 4)) & m4        #put count of each 8 bits
    return ((x * h01)>>24) & 0x3f

def lsw(x, n = 0):
    "ls word"
    return (x >> (32*n)) & 0xffffffff
    
def msbits(x, x_bitlen = None, l = 32):
    "ms bits"
    if not x_bitlen:
        x_bitlen = x.bit_length()
        if x_bitlen <= l:
            return x
    return x >> (x_bitlen - l)

#iterators
def bytes_be(x):
    "iterate in BE order"
    for j in range(4):
        yield x >> 24
        x <<= 8
        x &= 0xffffffff

def nibbles_be(x):
    "iterate in BE order"
    for j in range(8):
        yield x >> 28
        x <<= 4
        x &= 0xffffffff

def n2words_le(n, lwords = None):
    "LE array of words"
    if not lwords: 
        lwords = (n.bit_length() + 31) //32
    for j in range(lwords):
        x, n = n & 0xffffffff, n >> 32
        yield x

def bytes_le(x):
    "iterate in LE order"
    for j in range(4):
        yield x & 0xff
        x >>= 8

def nibbles_le(x):
    "iterate in LE order"
    for j in range(8):
        yield x & 0xf
        x >>= 4

def bytes2words(list_of_bytes):
    'both in LE order'
    b, i, w, res = 0, 0, 0, []
    for b in list_of_bytes:
        w |= b << i
        i += 8
        if i == 32:
            yield w
            i, w = 0, 0
    if i: 
        yield w

def lb(x):
    "The least significant bit set in x"
    return x & (-x)
        
def masks(m, n):
    "masks with m out of n bits set"
    if m > n:
        raise ValueError("Inconsistent parameters for mask_generator")
    mask = (1<<m) - 1
    n = 1 << n
    while mask < n:
        yield mask
        smallest = lb(mask)
        ripple  = mask + smallest
        ones = mask ^ ripple
        ones = (ones >> 2) // smallest 
        mask = ripple | ones

def products(subdim, dim):
    """iterates through all subdim subspaces 
    of the dim-dimensional cube.  Returns (mask, v), so
    that a subspace is defined as {x| x & mask == v}."""
    for mask in masks(subdim, dim):
        v, vbit = 0, lb(mask)
        while True:
            yield (mask, v)
            if v & vbit: 
            #the current bit in v is already lit
                #bits to vary in v, MS than vbit
                m = (v ^ mask) & (-vbit << 1)
                vbit = lb(m)
                if vbit: 
                    v ^= vbit
                    v &= -vbit
                    vbit = lb(mask)
                else:
                    break
            else:
                v ^= vbit

class Permutation(object):
    'Invertible permutation'
    def __init__(self, p):
        self.p = list(p)
        assert len(set(self.p)) == len(self.p), "true permutation"
    def __getitem__(self, value):
        try: return self.p[value]
        except IndexError: return None
    def __repr__(self):
        l = (len(self.p).bit_length()+3)//4
        f = '{{:{:d}d}}'.format(l)
        return ','.join(f.format(i) for i in self.p)
    def __iter__(self):
        return iter(self.p)
    def __invert__(self):
        res = [None]* len(self.p)
        for i, v in enumerate(self.p):
            res[v] = i
        return Permutation(res)
    def __call__(self, l):
        return (l[i] for i in self.p)
    def __mul__(self, other):
        return Permutation(self(other.p))
    def __add__(self, other):
        l = len(self.p)
        res = Permutation(self.p)
        for i in other:
            res.p.append(l+i)
        return res
    def shuffle(self, l):
        for i, x in enumerate(self(l)):
            l[i] = x
        

def Plain(n):
    'Permutation(0, 1, ..., n-1)'
    return Permutation(range(n))

def Flip(n):
    'Permutation(n-1, n-2, ..., 0)'
    return Permutation(range(n-1, -1, -1))

def Deal(n, step):
    'Permutation(0, 2, ..., 1, 3, ...)'
    p = []
    for i in range(step):
        p += range(i, n, step)
    return Permutation(p)
    
class Shuffler(object):
    def __init__(self, *l):
        self.l = list(l)
    def shuffle(self, l):
        p = self.l.pop(0)
        p.shuffle(l)
    
""" #TBD                
class PartialFunction(object):
    def __init__(self, p):
        self.p = dict(p)
    def __getitem__(self, value):
        return self.p.get(value)
    def __repr__(self):
        return repr(self.p)
    def __iter__(self):
        return self.p.iterkeys()
    def range(self):
        return self.p.itervalues()
    def __mul__(self, other):
        p = dict()
        for i in other:
            p[i] = self[other[i]]
        return PartialFunction(p)

def Logic(object):
    '''logical representation of a (partial) function f
       from n bits to m bits'''
    def __init__(self, func, n, m):
        self.f = []
        self.input_width = n
        self.output_width = m
        for i in range(m):
            output_bit = 1 << i
            positive_points, neutral_points = [], []
            for i in range(1 << n):
                p = func[i]
                if p == None: neutral_points.append(i)
                elif output_bit & p: 
                    positive_points.append(i)
            n2cover = len(positive_points)
            if n2cover == 0:
                self.f.append([])
            else:
                points = positive_points + neutral_points
                self.f.append(self.build(points, n2cover))
    def build(self, points, n2cover):
        sop = []
        for j in range(1, self.input_width): 
            if n2cover == 0: break
            capacity = 1 << (self.input_width - j)
            for g in products(j, self.input_width):
                g_contains = lambda p: (g[0] & p) == g[1]
                if not any(g_contains(p) for p in points[:n2cover]):
                    continue
                if sum (g_contains(p) for p in points) != capacity:
                    continue #this product is not full
                sop.append(g)
                i = 0
                n2cover -= 1
                while True:
                    while not g_contains(points[i]) and i < n2cover: 
                        i += 1
                    while g_contains(points[n2cover]) and i < n2cover:
                        n2cover -= 1
                    if i == n2cover:
                        if not g_contains(points[i]): n2cover += 1
                        break
                    points[n2cover], points[i] = points[i], points[n2cover]
                    i += 1
                    n2cover -= 1
                if n2cover == 0: break
        return sop
    def __call__(self, arg):
        res = 0
        for i in range(self.output_width):
            output_bit = 1 << i
            sop = self.f[i]
            for p in sop:
                if i & p[0] == p[1]:
                    res |= output_bit
                    break
        return res
"""
               
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: 
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h': 
            print ("Use -v  to run self-test")
