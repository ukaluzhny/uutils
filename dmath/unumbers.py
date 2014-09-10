# -*- coding: utf-8 -*-
"""Basic operations with numbers
 ri: random integer
 
 Primes: 
  retrieve_primes: a pool of primes from 2 to 997
   Those are retrieved from a file:
   >>> p = retrieve_primes()
   >>> p[-5:]
   [971, 977, 983, 991, 997]
  
  primes_product: product of consequent primes
   >>> primes_product(2, 8)
   1616615
   
  primes_prob: probabiity to be devisible by the indexed primes 
   >>> primes_prob(2, 8)
   0.513072067251634
  
  fermat_test: Fermat primality test
   >>> x = 0x3473ab29; print(fermat_test(x), fermat_test(x, 3))
   True False
   
 GCD: for Python numbers 
  >>> GCD(127*45, 127*101)
  127
 
 inverse: modular. In full mode, returns coefficients for Bézout's identity
  >>> u = 127; v = 101
  >>> inverse(u, v) == 35
  True
  >>> a, b = inverse(u, v, 1)
  >>> a*u + b*v
  1

 inv32: inverse mod 2**32; the argument shall be odd 
  >>> inv32(0x12345)
  3329816461
"""
from random import getrandbits
from os.path import exists, dirname, join
from struct import pack, unpack
import array as arr

#random integer
def ri(n = 96):
    return int(getrandbits(n))
#primes
def sieve(N = 1000):
    buf = list(range(N))
    buf[1] = 0
    for i in range(2, N):
        d = buf[i]
        if d: 
            for j in range(2*i, N, i):
                buf[j] = 0
                
    buf = filter(None, buf)
    return buf
def store_primes(primes):
    with open(join(dirname(__file__), 'primes.dat'), 'wb') as f:
        for n in primes:
            f.write(pack('i', n))
def retrieve_primes():
    try:
        primes = []
        with open(join(dirname(__file__), 'primes.dat'), 'rb') as f:
            while True:
                n = f.read(4)
                if not n: break
                primes.append(unpack('i', n)[0])  
    except IOError as e:
        print (e)
        print ("Cannot find primes.dat, generating primes")
        primes = sieve()
        try: 
            store_primes(primes)
        except IOError:
            print ("Cannot store primes.dat")
    return primes
__primes = retrieve_primes()
def primes_product(n, m):
    res = 1
    for i in range(n, m):
        res *= __primes[i]
    return res
def primes_prob(n, m):
    res = 1
    for i in range(n, m):
        res *= (1-1./__primes[i])
    return res
def fermat_test (p, a = 2):
    return pow(a, p-1, p) == 1
    
def GCD(x, y):
    x = abs(x) 
    y = abs(y)
    while x > 0:
        x, y = y % x, x
    return y
def inverse(u, v, full = 0):
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

def inv32(b):
    "inverse of b mod 2**32"
    assert(b & 1)
    x = (((b + 2) & 4) << 1) + b
    x *= 2 - b * x             
    x *= 2 - b * x             
    x *= 2 - b * x             
    return x & 0xffffffff
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: 
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h': 
            print ("Use -v  to run self-test")
     
     