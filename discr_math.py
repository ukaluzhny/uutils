# -*- coding: utf-8 -*-
"""
    basic discrete math primitives
    Z2 Vector Space:
    >>> Z2(0)+Z2(1)
    Z2(1)
    
    Vector Space over Z2
    >>> Z16(4)+Z16(2)
    Z16([Z2(0), Z2(1), Z2(1)])
    >>> print(Z16(4)+Z16(2))
    0110
"""
from __future__ import division, print_function, unicode_literals
from text_tools import hex, bin
def GCD(x, y):
    """For numbers only
        >>> GCD(127*45, 127*101)
        127"""
    x = abs(x) ; y = abs(y)
    while x > 0:
        x, y = y % x, x
    return y
def inverse(u, v):
    """The inverse of u mod v (uses truediv)
        >>> inverse(127, 101) == 35
        True"""
    u1, v1, v2 = 1L, 0L, v
    while v:
        q = u // v
        u1, v1 = v1, u1 - v1*q
        u, v  = v, u - v*q
    return u1 % v2
def hamming_weight(x):
    """x may be an object with a 'value' or a collection
        >>> hamming_weight(0x12345) == hamming_weight([0x1234, 5])
        True"""
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


class VectorSpace(object):
    """A vector space with add being xor.
        A vector is a list of elements of its base field,
        encoded as a number 'value'. Any class derived from
        VectorSpace defines its 'BaseF' and 'dimension'"""
    BaseF = None
    def __init__(self, v, justify = True):
        """If justify is True, then the number of bits in v
            is verified not to overflow the capacity"""
        if hasattr(v, 'value'): v = v.value
        try: self.value = long(v)
        except TypeError, e:
            if hasattr(v, '__iter__'): self.seq2val(v)
            else: raise e
        if justify:
            if self.value.bit_length() > self.bit_capacity():
                raise OverflowError()
    @classmethod
    def dim(self):
        return self.dimension
    @classmethod
    def bit_capacity(self):
        return self.dim() * self.BaseF.bit_capacity()
    def __eq__(self, other):
        return self.value == other.value
    def __ne__(self, other):
        return not (self == other)
    def __add__(self, other):
        v = self.value ^ other.value
        return type(self)(v, False)
    def __neg__(self):
        return type(self)(self)
    def __iter__(self):
        """transforms a number value (bitstring) into
            a list of elements of cls.BaseF"""
        BF = self.BaseF
        n = BF.bit_capacity()
        m = (1<<n) - 1
        x = self.value
        while x:
            yield(BF(x & m))
            x >>= n
    def seq2val(self, l):
        """transforms a list of elements of self.BaseF
            into a number value (bitstring)"""
        BF = self.BaseF
        n = BF.bit_capacity()
        self.value, shift = 0, 0
        for i in l:
            self.value |= (BF(i).value << shift)
            shift += n
    def __getitem__(self, index):
        BF = self.BaseF
        b = BF.bit_capacity()
        m = (1 << b) - 1
        return BF((self.value >> (index*b)) & m)
    def __setitem__(self, index, val):
        BF = self.BaseF
        b = BF.bit_capacity()
        m = ((1<<b) - 1) << (index*b)
        self.value &= ~m
        val = BF(val).value
        self.value ^= (val << (index*b))
    def __repr__(self):
        res = ["{}({})".format(self.BaseF.__name__,
            hex(i.value)) for i in self]
        return '{}([{}])'.format(
            type(self).__name__, ', '.join(res))
    def __str__(self):
        return bin(self.value, self.bit_capacity(), True)
    def __mul__(self, other):
        "scalar product"
        if isinstance(other, VectorSpace):
            BF = self.BaseF
            if other.BaseF == BF and other.dim() == self.dim():
                return sum([i*j for i, j in zip(self, other)], BF(0))
            raise TypeError("Scalar Product of non-isomorphic spaces")
        raise TypeError("Unsupported Product")
    def __lshift__(self, i):
        b = self.BaseF.bit_capacity()
        return type(self)(self.value << (b * i), False)
    @classmethod
    def __lt__(self, other_cls):
        "A vector space over F is greater than F, transitive"
        if issubclass(other_cls, VectorSpace) and other_cls.BaseF:
            BF = other_cls.BaseF
            return self == BF or self < BF
        return False
    __xor__ = __add__
    __sub__ = __add__


class Z2(VectorSpace):
    def __init__(self, v, justify = True):
        self.value = int(v)
        if self.value.bit_length() > self.bit_capacity():
                raise OverflowError()
    @classmethod
    def bit_capacity(self):
        return 1
    def __repr__(self):
        return 'Z2({})'.format(self.value)
    def __str__(self):
        return str(self.value)
    def inv(self):
        if not self.value:
            raise ZeroDivisionError("Inverting 0?!")
        return self
    def __truediv__(self, other):
        if not self.value:
            raise ZeroDivisionError()
        return self
#example
class Z16(VectorSpace):
    dimension = 4
    BaseF = Z2


class Matrix(object):
    """Matrix is defined by a list of its rows (vectors
        of the Domain vector space , defined separately.
        Range, if different, shall be over the same field."""
    def __init__(self, rows, Domain, Range = None):
        self.Range = Range if Range else Domain
        self.Domain = Domain
        if  not hasattr(rows,'__iter__'):
            raise TypeError("wrong Matrix initialization")
        self.rows = [Domain(v) for v in rows]
        if len(self.rows) != self.Range.dim():
            raise ValueError("wrong number of rows")
    def size(self):
        return (self.Range.dim(), self.Domain.dim())
    def __getitem__(self, index):
        if isinstance(index, int):
            return self.rows[index]
        return self.rows[index[0]][index[1]]
    def __iter__(self):
        return iter(self.rows)
    def __repr__(self):
        res = [repr(r) for r in self.rows]
        res =  'Matrix([\n{}],{},{})'.format(',\n'.join(res),
            self.Domain.__name__,  self.Range.__name__)
        return res
    def __str__(self):
        rows = [str(r) for r in self.rows]
        return '\n\n{}\n\n'.format('\n'.join(reversed(rows)))
    def __setitem__(self, index, val):
        if isinstance(index, int):
            v = self.Domain(val) 
            self.rows[index] = v  
        else:
            self.rows[index[0]][index[1]] = val
    def transposed(self):
        m,n = self.size()
        M = Matrix([0]*n, self.Range, self.Domain)
        for i in range(n):
            for j in range(m):
                M[i,j] = self[j,i]
        return M
    def overZ2(self):
        N = self.Domain.bit_capacity()
        M = self.Range.bit_capacity()
        columns = [self*self.Domain(1<<i) for i in range(N)]
        class Z2Domain:
            BaseF = Z2
            dimension = N
        class Z2Range:
            BaseF = Z2
            dimension = M
        return Matrix(columns, Z2Range, Z2Domain).transposed()
    def __add__(self, other):
        v = [a+b for a,b in zip(self, other)]
        return Matrix(v, self.Domain, self.Range)
    def __neg__(self):
        v = [-a for a in self]
        return Matrix(v, self.Domain, self.Range)
    def __mul__(self, other):
        if isFieldElement(other):
            m,n = self.size()
            for i in range(m):
                self[i] *= other
        elif isVector(other):
            v = [row*other for row in self]
            return self.Range(v)
        elif type(other) == Matrix:
            M = other.transposed()
            rows = [self*v for v in M]
            N = Matrix(rows, self.Range, other.Domain)
            return N.transposed()
        else:
            raise TypeError("Unsupported type multiplication")
    def inv(self):
        l, n = self.size()
        if n != l:
            raise TypeError("Non-square Matrix cannot be inverted")
        F = self.Domain.BaseF
        M = Matrix(self, self.Domain)
        N = Matrix([0]*l, self.Domain)
        for i in range(l): 
            N[i,i] = 1
        for col in range(l):
            if M[col, col] == F(0):
                try:
                    for row in range(col+1, l+1):
                        if M[row, col] != F(0):
                            M[col] += M[row]
                            N[col] += N[row]
                            break
                except IndexError:
                    return
            a = M[col, col].inv()
            M[col] *= a 
            N[col] *= a
            for row in range (col+1, l):
                a = M[row, col]
                if M[row, col] != F(0):
                    M[row] -= M[col]*a
                    N[row] -= N[col]*a
        for col in range(l-1, -1 , -1):
            for row in range(col-1, -1, -1):
                a = M[row, col]
                if M[row, col] != F(0):
                    M[row] -= M[col]*a
                    N[row] -= N[col]*a
        return N

if __name__ == "__main__":
   import doctest
   doctest.testmod()

