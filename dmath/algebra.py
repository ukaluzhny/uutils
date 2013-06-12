# -*- coding: utf-8 -*-
""" Vector Spaces, Finite Fields and Matrices
 PrimeField is defined by its base
 >>> class Z3(PrimeField):
 ...     base = 3
 >>> Z3(2)+Z3(2)
 Z3(1)
 >>> Z3(3)-Z3(1)
 Z3(2)
 >>> Z3(2)*Z3(2)
 Z3(1)
 >>> Z3(2).inv() #implemented by Fermat little theorem
 Z3(2)
 
 Z2, an optimized PrimeField, is predefined  
 >>> Z2(0)+Z2(1)
 Z2(1)
 >>> Z2(0)*Z2(1)
 Z2(0)
 
 class VectorSpace defines a vector space over a field 
 Any class derived from VectorSpace shall define its 
 'BaseF' and 'dimension'. E.g.
 >>> class Z16(VectorSpace):
 ...     dimension = 4
 ...     BaseF = Z2
 ... 
 >>> A =  Z16(4) + Z16(2)          #numbers represent bit vectors
 >>> A == Z16([Z2(0),Z2(1),Z2(1)]) #LE
 True
 >>> B =  Z16(7); print(B)         #BE bit-encoding
 0111
 >>> print (A == B, A != B, -A) 
 False True 0110
 >>> print (A*B, type(A*B).__name__) #Scalar product
 0 Z2
 
 class ExtentionField defines a general finite field
 Any class derived from ExtentionField shall define its 
 'BaseF' and the extention polinomial 'p', as in 
 >>> class F8(ExtentionField):
 ...     "Rijndael's Polynom X^8 = X^4 + X^3 + X + 1"
 ...     BaseF = Z2
 ...     p = [1,1,0,1,1,0,0,0]
  
 >>> a = F8(0x53); b = F8(0xca); c = a + b
 >>> print (a * b == F8(1), (a+F8(1)) * b == b + F8(1))
 True True
 >>> print (a == b.inv(), (a*c).inv() == b *c.inv())
 True True
"""
from __future__ import division, print_function, unicode_literals
from itertools import chain, repeat

class PrimeField(object):
    "Defined by a prime number"
    base = None #abstract class
    def __init__(self, v):
        if type(v) == type(self): 
            self.value = v.value
        else:
            self.value = v % self.base
    @classmethod
    def bit_capacity(self):
        return self.base.bit_length()
    @classmethod
    def overZ2(self):
        return self.base == 2
    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.value)
    def __str__(self):
        return str(self.value)
    def __add__(self, other):
        F = type(self)
        if type(other) == F:
            return F((self.value + other.value) % self.base)
        else:
            raise TypeError("Unsupported type addition")
    def __neg__(self):
        F = type(self) 
        if self.overZ2():
            return F(self.value)
        else:
            return F(self.base - self.value)
        return type(self)(self)
    def __sub__(self, other):
        return self + (-other)
    def __mul__(self, other):
        F = type(self)
        if type(other) == F:
            return F((self.value * other.value) % self.base)
        elif isVector(other):
            return type(other)(self*i for i in other)
        else:
            raise TypeError("Incompatible types in multiplication")
    def inv(self):
        if not self.value:
            raise ZeroDivisionError("Inverting 0?!")
        return type(self)(pow(self.value, self.base-2, self.base))
    def __truediv__ (self, other):
        return self * other.inv() 

        
class Z2(PrimeField):
    base = 2
    def __init__(self, v):
        if type(v) == type(self): 
            self.value = v.value
        else:
            self.value = v & 1
    @classmethod
    def bit_capacity(self):
        return 1
    def __add__(self, other):
        if type(other) == Z2:
            return Z2(self.value ^ other.value)
        else:
            raise TypeError("Unsupported type addition")
    def __mul__(self, other):
        if type(other) == Z2:
            return Z2(self.value & other.value)
        elif isVector(other):
            return type(other)(self*i for i in other)
        else:
            raise TypeError("Unsupported type multiplication")
    def inv(self):
        if not self.value:
            raise ZeroDivisionError("Inverting 0?!")
        return Z2(self.value)
        

class VectorSpace(object):
    """A vector space over a field.
       A vector is a list of elements of its base field.
       Any class derived from VectorSpace shall define
       its 'BaseF' and 'dimension'"""
    BaseF, dimension = None, None #abstract class
    def __init__(self, v):
        if hasattr(v, 'value'): 
            self.value = v.value
        else:
            try: self.value = int(v)
            except TypeError:
                BF = self.BaseF
                n = BF.bit_capacity()
                self.value, shift = 0, 0
                for i in v:
                    self.value |= (BF(i).value << shift)
                    shift += n
    @classmethod
    def dim(self):
        return self.dimension
    @classmethod
    def bit_capacity(self):
        return self.dim() * self.BaseF.bit_capacity()
    @classmethod
    def overZ2(self):
        return self.BaseF.overZ2()
    def __eq__(self, other):
        return type(self) == type(other) and\
            self.value == other.value
    def __ne__(self, other):
        return not (self == other)
    def __add__(self, other):
        F = type(self) 
        if self.overZ2():
            return F(self.value ^ other.value)
        else: #tricky
            BF = lambda x: x or self.BaseF(0)
            return F(i + j for i, j in zip(self, other))
    def __neg__(self):
        F = type(self) 
        if self.overZ2():
            return F(self)
        else:
            return F(-i for i in self)
        return type(self)(self)
    def __sub__(self, other):
        return self + (-other)
    def __iter__(self):
        """transforms a number value (bitstring) into an
            iterator over the list of elements of cls.BaseF followed by one zero"""
        BF = self.BaseF
        n = BF.bit_capacity()
        m = (1 << n) - 1
        x, i = self.value, 0
        while x or i <= self.dim():
            yield(BF(x & m))
            x >>= n
            i += 1
    # def __getitem__(self, index):
        # BF = self.BaseF
        # b = BF.bit_capacity()
        # m = (1 << b) - 1
        # return BF((self.value >> (index*b)) & m)
    # def __setitem__(self, index, val):
        # BF = self.BaseF
        # b = BF.bit_capacity()
        # m = ((1 << b) - 1) << (index*b)
        # self.value &= ~m
        # val = BF(val).value
        # self.value ^= (val << (index*b))
    def __repr__(self):
        return '{}({:#x})'.format(type(self).__name__, self.value)
    def __str__(self):
        return '{:b}'.format(self.value).zfill(self.bit_capacity())
    def __mul__(self, other):
        "scalar product"
        return sum((i*j for i,j in zip(self,other)), self.BaseF(0))
    __xor__ = __add__
    __sub__ = __add__
def isVector(x):
    return issubclass(type(x), VectorSpace)

def dstr(l):
    print( ''.join(str(i) for i in l))
class ExtentionField(VectorSpace):
    """An extention field is defined by its 
        base field 'BaseF', e.g., Z2 and 
        the extension polinomial 'p', padded with zeroes, 
            e.g, [1,1,0,1,1,0,0,0] for Rijndael's field """
    BaseF, p = None, None #abstract class
    def __init__(self, v, reduce = False):
        if reduce:
            self.reduct(v)
        VectorSpace.__init__(self, v)
    @classmethod
    def dim(self):
        return len(self.p)
    def __mul__(self,other):
        "can handle one operand of length self.dim()+1"
        F  = type(self)
        BF = self.BaseF
        if type(other) == F:
            res = [BF(0) for i in range(self.dim()*2+1)]
            for i, v in enumerate(self):
                for j, u in enumerate(other):
                    if v.value and u.value:
                        res[i+j] = res[i+j] + (v * u)
            return F(res, True)
        elif isVector(other):
            return type(other)(self*i for i in other)
        else:
            raise TypeError("Incompatible types in multiplication")
    @classmethod
    def reduct(self, l):
        F  = type(self)
        BF = self.BaseF
        p  = [BF(v) for v in chain(repeat(0, self.dim()), self.p)]
        while len(l) > len(self.p):
            u = l.pop()
            if u.value != 0:
                for i, v in enumerate(p):
                    if v.value:
                        v = v*u
                        l[i] = l[i] - v
            p.pop(0) 
    def inv(self):
        F = type(self)
        if self.value == 0:
            raise ZeroDivisionError("Inverting 0?!")
        
        BF = self.BaseF
        if self.value.bit_length() <= BF.bit_capacity():
            return F(BF(self.value).inv())
            
        x_inv  = F(self.p[1:]+[1]) #inverse of F(2)
        BFmask = (1 << BF.bit_capacity()) - 1
        u, v = F(self), F(self.p+[1])
        a, b = F(1),    F(0)
        while u.value > BFmask:
            u0 = u.value & BFmask
            v0 = v.value & BFmask
            if u0 == 0:
                u = u * x_inv
                a = a * x_inv
            if v0 == 0:
                v = v * x_inv
                b = b * x_inv
            if u0 and v0:
                if u.value > v.value:
                    u = BF(v0)*u - BF(u0)*v
                    a = BF(v0)*a - BF(u0)*b
                    u = u * x_inv
                    a = a * x_inv
                else:
                    v = BF(u0)*v - BF(v0)*u
                    b = BF(u0)*b - BF(v0)*a
                    v = v * x_inv
                    b = b * x_inv
        return BF(u.value).inv() * a        
    def __truediv__(self, other):
        return self*other.inv()
    def __pow__(self, power):
        'Right-to-left'
        F = type(self)
        a, res = F(self), F(1)
        while True:
            if power & 1: #multiply
                res *= a
            power >>= 1
            if not power:
                return res
            a  = a * a

class F8(ExtentionField):
    "Rijndael's Polynom X^8 = X^4 + X^3 + X + 1"
    BaseF = Z2
    p = [1,1,0,1,1,0,0,0]

a = F8(0x53)
b = F8(0xca) 
print (a * b)
print (a.inv())
 
# class Matrix(object):
    # """Matrix is defined by a list of its rows (vectors
        # of the Domain vector space , defined separately.
        # Range, if different, shall be over the same field."""
    # def __init__(self, rows, Domain, Range = None):
        # self.Range = Range if Range else Domain
        # self.Domain = Domain
        # if  not hasattr(rows,'__iter__'):
            # raise TypeError("wrong Matrix initialization")
        # self.rows = [Domain(v) for v in rows]
        # if len(self.rows) != self.Range.dim():
            # raise ValueError("wrong number of rows")
    # def size(self):
        # return (self.Range.dim(), self.Domain.dim())
    # def __getitem__(self, index):
        # if isinstance(index, int):
            # return self.rows[index]
        # return self.rows[index[0]][index[1]]
    # def __iter__(self):
        # return iter(self.rows)
    # def __repr__(self):
        # res = [repr(r) for r in self.rows]
        # res =  'Matrix([\n{}],{},{})'.format(',\n'.join(res),
            # self.Domain.__name__,  self.Range.__name__)
        # return res
    # def __str__(self):
        # rows = [str(r) for r in self.rows]
        # return '\n\n{}\n\n'.format('\n'.join(reversed(rows)))
    # def __setitem__(self, index, val):
        # if isinstance(index, int):
            # v = self.Domain(val) 
            # self.rows[index] = v  
        # else:
            # self.rows[index[0]][index[1]] = val
    # def transposed(self):
        # m,n = self.size()
        # M = Matrix([0]*n, self.Range, self.Domain)
        # for i in range(n):
            # for j in range(m):
                # M[i,j] = self[j,i]
        # return M
    # def overZ2(self):
        # N = self.Domain.bit_capacity()
        # M = self.Range.bit_capacity()
        # columns = [self*self.Domain(1<<i) for i in range(N)]
        # class Z2Domain:
            # BaseF = Z2
            # dimension = N
        # class Z2Range:
            # BaseF = Z2
            # dimension = M
        # return Matrix(columns, Z2Range, Z2Domain).transposed()
    # def __add__(self, other):
        # v = [a+b for a,b in zip(self, other)]
        # return Matrix(v, self.Domain, self.Range)
    # def __neg__(self):
        # v = [-a for a in self]
        # return Matrix(v, self.Domain, self.Range)
    # def __mul__(self, other):
        # if isFieldElement(other):
            # m,n = self.size()
            # for i in range(m):
                # self[i] *= other
        # elif isVector(other):
            # v = [row*other for row in self]
            # return self.Range(v)
        # elif type(other) == Matrix:
            # M = other.transposed()
            # rows = [self*v for v in M]
            # N = Matrix(rows, self.Range, other.Domain)
            # return N.transposed()
        # else:
            # raise TypeError("Unsupported type multiplication")
    # def inv(self):
        # l, n = self.size()
        # if n != l:
            # raise TypeError("Non-square Matrix cannot be inverted")
        # F = self.Domain.BaseF
        # M = Matrix(self, self.Domain)
        # N = Matrix([0]*l, self.Domain)
        # for i in range(l): 
            # N[i,i] = 1
        # for col in range(l):
            # if M[col, col] == F(0):
                # try:
                    # for row in range(col+1, l+1):
                        # if M[row, col] != F(0):
                            # M[col] += M[row]
                            # N[col] += N[row]
                            # break
                # except IndexError:
                    # return
            # a = M[col, col].inv()
            # M[col] *= a 
            # N[col] *= a
            # for row in range (col+1, l):
                # a = M[row, col]
                # if M[row, col] != F(0):
                    # M[row] -= M[col]*a
                    # N[row] -= N[col]*a
        # for col in range(l-1, -1 , -1):
            # for row in range(col-1, -1, -1):
                # a = M[row, col]
                # if M[row, col] != F(0):
                    # M[row] -= M[col]*a
                    # N[row] -= N[col]*a
        # return N


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: 
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h': 
            print ("Use -v  to run self-test")
     
     