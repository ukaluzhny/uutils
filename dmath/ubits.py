# -*- coding: utf-8 -*-
"""tricks with bits
   hw(x), hamming_weight  
    x may be an object with 'value' or an iterable.
    >>> hw(0x12345) == 7
    True
    >>> hw([0x1234, 5]) == 7
    True
 
   lb(x), the least significant bit set in x
    >>> lb(0x1230) == 0x10
    True
  
   masks(m, n), iterates through numbers with m out of n bits set
    >>> list(masks(2, 3))
    [3, 5, 6]
    
   products(subdim, dim), iterates through all subdim subspaces 
    of the dim-dimensional cube.  Returns (mask, v), so
    that a subspace is defined as {x| x & mask == v}.
    >>> list(products(2,3))[:7]
    [(3, 0), (3, 1), (3, 2), (3, 3), (5, 0), (5, 1), (5, 4)]

    
# a = bit.Permutation([1,3,2,0])
# b = bit.Permutation([1,0,3,2])
# l = ['a','b','c','d']
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
        assert len(set(self.p)) == len(self.p)
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
    def shuffle(self, l):
        p = [None]* len(l)
        for i, x in enumerate(l):
            p[self[i]] = x
        for i, x in enumerate(p):
            l[i] = x
    def __mul__(self, other):
        p = list(self.p)
        other.shuffle(p)
        return Permutation(p)
    def __add__(self, other):
        l = len(self.p)
        res = Permutation(self.p)
        for i in other:
            res.p.append(l+i)
        return res
             
def Plain(n):
    'Permutation(0, 1, ..., n-1)'
    return Permutation(xrange(n))
def Flip(n):
    'Permutation(n-1, n-2, ..., 0)'
    p = xrange(n-1, -1, -1)
    return Permutation(p)
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
        for i in xrange(m):
            output_bit = 1 << i
            positive_points, neutral_points = [], []
            for i in xrange(1 << n):
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
        for i in xrange(self.output_width):
            output_bit = 1 << i
            sop = self.f[i]
            for p in sop:
                if i & p[0] == p[1]:
                    res |= output_bit
                    break
        return res

               
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: 
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h': 
            print ("Use -v  to run self-test")
