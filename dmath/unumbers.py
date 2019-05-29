"""Basic operations with numbers
 Primes:
  get_primes: a pool of primes from 2 to 997
   Those are retrieved from a file:
   >>> p = get_primes()
   >>> p[-5:]
   [971, 977, 983, 991, 997]

  primes_product: product of consequent primes
   >>> primes_product(2, 8)
   1616615

  primes_prob: probability to be divisible by the indexed primes
   >>> primes_prob(2, 8)
   0.513072067251634

  fermat_test: Fermat primality test
   >>> x = 0x3473ab29; print(fermat_test(x), fermat_test(x, 3))
   True False

 gcd: for Python numbers
  >>> gcd(127*45, 127*101)
  127

 inverse(u, v, full=False): modular inverse.
 In full mode, returns coefficients for Bézout's identity
  >>> u = 127; v = 101
  >>> inverse(u, v) == 35
  True
  >>> a, b = inverse(u, v, True)
  >>> a*u + b*v
  1

 inv32: inverse mod 2**32; the argument shall be odd
  >>> hex(inv32(0x12345))[:10]
  '0xc678f78d'
  
 n2w: a Python integer -> C style WINT
  >>> n2w(0x4000000030000000200000001)
   {0x00000001, 0x00000002, 0x00000003, 0x00000004}
 
 n2a, a2n: a Python integer <-> list of words, LE
  >>> l = n2a(0x12345678abcd1234)
  >>> l == [0xabcd1234, 0x12345678] #LE array
  True
  >>> x = grb(86)
  >>> l = n2a(x)
  >>> a2n(l) == x
  True

  """
from os.path import exists, dirname, join
from struct import pack, unpack
from random import getrandbits as grb
from numba import jit

def sieve(N=1000):
    buf = list(range(N))
    buf[1] = 0
    for i in range(2, N):
        d = buf[i]
        if d:
            for j in range(2*i, N, i):
                buf[j] = 0
    return list(filter(None, buf))

def store_primes():
    with open(join(dirname(__file__), 'primes.dat'), 'wb') as f:
        for n in primes:
            f.write(pack('i', n))

primes = []
def get_primes():
    global primes
    if primes:
        return primes
        try:
            primes = []
            with open(join(dirname(__file__), 'primes.dat'), 'rb') as f:
                while True:
                    n = f.read(4)
                    if not n:
                        break
                    primes.append(unpack('i', n)[0])
        except IOError:
            print("Cannot find primes.dat, generating primes")
            primes = sieve()
            try:
                store_primes()
            except IOError:
                print("Cannot store primes.dat")
        return primes

def primes_product(n, m):
    if not primes:
        get_primes()
    res = 1
    for p in primes[n:m]:
        res *= p
    return res

def primes_prob(n, m):
    if not primes:
        get_primes()
    res = 1
    for p in primes[n:m]:
        res *= (1-1./p)
    return res
    
def fermat_test(p, a=2):
    return pow(a, p-1, p) == 1

@jit()
def gcd(x, y):
    x = abs(x)
    y = abs(y)
    if x > y: 
        x, y = y, x
    while x > 0:
        x, y = y % x, x
    return y

def inverse(u, v, full = False):
    'inverse of u mod v '
    a, b = 1, 0
    v_stored = v
    u_stored = u
    while v:
        q = u // v #uses truediv
        u, v = v, u - v*q
        a, b = b, a - b*q
    a %= v_stored
    if full: return a, -(a*u_stored-1)//v_stored
    return a
    
@jit("u4(u4)")
def inv32(b):
    "inverse of b mod 2**32" 
    assert(b & 1), "inverting an odd number"
    x = (((b + 2) & 4) << 1) + b
    x *= 2 - b * x
    x *= 2 - b * x
    x *= 2 - b * x
    return x & 0xffffffff

def prime30():
    first_primes = 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23 
    found = False
    while not found:
        candidate = grb(30) | 1
        d = gcd(candidate, first_primes)
        if d != 1:
            candidate += (first_primes // d) << 1
        if candidate >> 30:
            continue
        if fermat_test(candidate) and fermat_test(candidate, 3):
            found = True
    return candidate

def n2w(x, name="", printing=True):
    "Python integer ->  C style WINT"
    l = n2a(x)
    res = ', '.join(
        '0x{:08x}'.format(i) for i in l)
    res = name + ' {'+res+'}'
    if printing:
        print(res)
    return res
    
def n2f(f, *p):
    while p:
        (x, l), p = p[:2], p[2:]
        f.write(pack('{}I'.format(l), *n2a(x, l)))
        
def n2a(n, l=None):
    "LE array of words"
    res = []
    if not l:
        l = (n.bit_length() + 31) //32
    for _ in range(l):
        i, n = n & 0xffffffff, n >> 32
        res.append(i)
    return res

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

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h':
            print("Use -v  to run self-test")

