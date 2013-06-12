# -*- coding: utf-8 -*-
"""tricks with bits
   For hamming_weight(x), x may be an object with a 'value' or a collection
 >>> hamming_weight(0x12345) == 7
 True
 >>> hamming_weight([0x1234, 5]) == 7
 True
 
 lb(x) returns the least significant set bit in x
 >>> lb(0x1230) == 0x10
 True
"""
from __future__ import division, print_function, unicode_literals


def hamming_weight(x):
    if not x: return 0
    if hasattr(x, 'value'):
        x = x.value
    if hasattr(x, '__iter__'):
        return sum([hamming_weight(i) for i in x])
    m2  = 0x3333333333333333
    m4  = 0x0f0f0f0f0f0f0f0f
    h01 = 0x0101010101010101
    num = x
    num -= (num >> 1) & 0x5555555555555555 #put count of each 2 bits
    num = (num & m2) + ((num >> 2) & m2) #put count of each 4 bits
    num = (num + (num >> 4)) & m4        #put count of each 8 bits
    return ((num * h01)>>56)& 0x7f
def lb(x):
    """The least significant set bit in x
        >>> lb(0x1230) == 0x10
        True"""
    return x & (-x)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: 
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h': 
            print ("Use -v  to run self-test")
