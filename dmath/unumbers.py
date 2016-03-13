# -*- coding: utf-8 -*-
"""Basic operations with numbers
 Primes:
  primes: a pool of primes from 2 to 997
   Those are retrieved from a file:
   >>> p = get_primes()
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

 gcd: for Python numbers
  >>> gcd(127*45, 127*101)
  127

 inverse(u, v, full = False): modular inverse.
 In full mode, returns coefficients for Bézout's identity
  >>> u = 127; v = 101
  >>> inverse(u, v) == 35
  True
  >>> a, b = inverse(u, v, True)
  >>> a*u + b*v
  1

 inv32: inverse mod 2**32; the argument shall be odd
  >>> inv32(0x12345)
  3329816461
"""
from os.path import exists, dirname, join
from struct import pack, unpack

def sieve(N = 1000):
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

def get_primes():
    global primes
    try:
        return primes
    except NameError:
        try:
            primes = []
            with open(join(dirname(__file__), 'primes.dat'), 'rb') as f:
                while True:
                    n = f.read(4)
                    if not n: break
                    primes.append(unpack('i', n)[0])
        except IOError as e:
            # print (e)
            print ("Cannot find primes.dat, generating primes")
            primes = sieve()
            try:
                store_primes()
            except IOError:
                print ("Cannot store primes.dat")
        return primes

def primes_product(n, m):
    global primes
    try: primes
    except NameError: get_primes() 
    res = 1
    for p in primes[n:m]:
        res *= p
    return res

def primes_prob(n, m):
    global primes
    try: primes
    except NameError: get_primes() 
    res = 1
    for p in primes[n:m]:
        res *= (1-1./p)
    return res

def fermat_test (p, a = 2):
    return pow(a, p-1, p) == 1

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
        if candidate >> 30: continue
        if fermat_test(candidate) and fermat_test(candidate, 3):
            found = True
    return candidate


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h':
            print ("Use -v  to run self-test")

