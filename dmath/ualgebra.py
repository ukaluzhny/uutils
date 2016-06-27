# -*- coding: utf-8 -*-
""" Vector Spaces, Finite Fields and Matrices
 class PrimeField is defined by its prime 'base'
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
 
 class VectorSpace - an abstract class.
  A derived vector space is defined by its 'BaseF' and 'dimension'.
  See the definition of the factory function V2   
  
  >>> V16 = V2(4)
  >>> A =  V16(4) + V16(2)          #numbers represent bit vectors
  >>> A == V16([Z2(0),Z2(1),Z2(1)]) #LE list of elements of the base field
  True
  >>> B =  V16(7); print(B)         #BE bit-encoding
  0111
  >>> print (A == B, A != B, -A) 
  False True 0110
  >>> print (A*B, type(A*B).__name__) #Scalar product
  0 Z2
 
 class ExtentionField  - an abstract class.
  A derived finite field is defined by its 'BaseF' 
  and the extention polinomial 'p',  s.t. x^dim + 'p' = 0,
  see the predefined Rijndael field F8 for an example 
  
  >>> a = F8(0x53); b = F8(0xca); c = a + b
  >>> print (a * b == F8(1), (a+F8(1)) * b == F8(1) + b)
  True True
  >>> print (a == b.inv(), (a*c).inv() == b *c.inv())
  True True
  
  A more complex example:
  >>> class F27(ExtentionField):
  ...     "Polynom 0 = X^3 + 2X + 1, over F3"
  ...     BaseF = Z3
  ...     p = [1,2,0]
  >>> a = F27(0x29); b = F27(0x10)
  >>> print (a == b.inv())
  True
 
 class Matrix, each matrix from a 'Domain' to a 'Range'
  is defined by a list of its rows (vectors of the Domain).
  the Range shall be defined, if different from the Domain, 
  and shall be over the same base field.
  >>> V9 =  V2(2, Z3)
  >>> V27 =  V2(3, Z3)
  >>> A = Matrix([[1,2],[0,1],[2,0]], V9, V27)
  >>> B = Matrix([[0,1],[1,2],[2,0]], V9, V27)
  >>> print (A)
  [0010,
   0100,
   1001]
  >>> print (B.transposed())
  [001001,
   100100]
  >>> print (A+B)
  [0001,
   0001,
   0001]
  >>> A = Matrix([[1,2,0],[0,1,2],[1,1,0]], V27)
  >>> B = Matrix([[2,0,0],[1,2,0],[1,2,2]], V27)
  >>> I = Matrix(V27.basis(), V27)
  >>> print(A*A.inv() == I, B*B.inv() == I)
  True True
  >>> import random as r
  >>> M = RandomMatrix(V16, r) #Random Invertible Matrix
"""
from itertools import chain, repeat, zip_longest
from operator import itemgetter, attrgetter
from uutils.dmath.unumbers import inverse

class PrimeField(object):
    "Defined by a prime number 'base'"
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
    @classmethod
    def iter(self):
        'all elements of the field'
        return xrange(self.base)
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
    def __iadd__(self, other):
        F = type(self)
        if type(other) == F:
            self.value += other.value
            self.value %= self.base
            return self
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
    def __isub__(self, other):
        self += (-other)
        return self
    def __mul__(self, other):
        F = type(self)
        if type(other) == F:
            return F((self.value * other.value) % self.base)
        else:
            return NotImplemented
    def inv(self):
        if not self.value:
            raise ZeroDivisionError("Inverting 0?!")
        return type(self)(inverse(self.value, self.base))
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
    def __iadd__(self, other):
        if type(other) == Z2:
            self.value ^= other.value
            return self
        else:
            raise TypeError("Unsupported type addition")
    def __mul__(self, other):
        if type(other) == Z2:
            return Z2(self.value & other.value)
        else: return NotImplemented 
    def inv(self):
        if not self.value:
            raise ZeroDivisionError("Inverting 0?!")
        return Z2(self.value)
    __sub__ = __add__
    __isub__ = __iadd__
    

class VectorSpace(object):
    """An abstract class for vector spaces over various fields.
     A vector is a LE list of elements of its base field.
     Any derived class shall define its 'BaseF' and 'dimension'"""
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
    def basis(self):
        'iterator'
        v = 1
        for i in range(self.dimension):
            yield self(v)
            v <<= self.BaseF.bit_capacity()
    @classmethod
    def overZ2(self):
        return self.BaseF.overZ2()
    def __eq__(self, other):
        return (type(self) == type(other) and
            self.value == other.value)
    def __ne__(self, other):
        return not (self == other)
    def __add__(self, other):
        F = type(self) 
        if self.overZ2():
            return F(self.value ^ other.value)
        else:
            return F(i + j for i, j in zip_longest(self, other, 
                        fillvalue = self.BaseF(0)))
    def __iadd__(self, other):
        F = type(self) 
        if self.overZ2():
            self.value ^= other.value
        else:
            self.value = F(i+j for i, j in zip_longest(self, other, 
                        fillvalue = self.BaseF(0))).value
        return self
    def __neg__(self):
        F = type(self) 
        if self.overZ2():
            return F(self)
        else:
            return F(-i for i in self)
    def __sub__(self, other):
        return self + (-other)
    def __isub__(self, other):
        self += -other
        return self
    def __iter__(self):
        """transforms a number value (bitstring) into an
            iterator over the list of elements of BaseF"""
        BF = self.BaseF
        n = BF.bit_capacity()
        m = (1 << n) - 1
        i = 0
        while True:
            v = self.value >> (n*i)
            if i < self.dim() or v:
                yield(BF(v & m))
                i += 1
            else: return
    def __repr__(self):
        return '{}({:#x})'.format(type(self).__name__, self.value)
    def __str__(self, mode = 'HW'):
        if mode == 'HW':
            return '{:b}'.format(self.value).zfill(self.bit_capacity())
        return ' '.join(str(i) for i in self)
    def __mul__(self, other):
        "scalar product"
        return sum((i*j for i,j in zip(self,other)), self.BaseF(0))
    def __rmul__(self, other):
        if type(other) == self.BaseF:
            return type(self)(other*i for i in self)
        else: 
            return NotImplemented
    def __imul__(self, other):
        self.value = type(self)(
            other*i for i in self).value
        return self

    
class ExtentionField(VectorSpace):
    """An extention field is defined by its 
     base field 'BaseF', e.g., Z2 and the extension polinomial
     e.g, [1,1,0,1,1,0,0,0] for Rijndael's field """
    BaseF, p = None, None #abstract class
    def __init__(self, v):
        VectorSpace.__init__(self, v)
    @classmethod
    def dim(self):
        return len(self.p)
    def __mul__(self,other):
        """can handle one operand of length self.dim()+1
        as used in inv"""
        F  = type(self)
        if type(other) == F:
            BF = self.BaseF
            res = [BF(0) for i in range(self.dim()*2+1)]
            for i, v in enumerate(self):
                for j, u in enumerate(other):
                    if v.value and u.value:
                        res[i+j] = res[i+j] + (v * u)
            return F(F.reduct(res))
        else:
            return NotImplemented
    @classmethod
    def reduct(self, l):
        "l is a list of self.dim()*2+1 BF elements"
        F  = type(self)
        BF = self.BaseF
        p  = [BF(v) for v in chain(repeat(0, self.dim()), self.p)]
        while len(l) > len(self.p):
            u = l.pop()
            if u.value != 0:
                for i, v in enumerate(p):
                    if v.value:
                        l[i] = l[i] - v*u
            p.pop(0)
        return l
    def inv(self):
        F = type(self)
        if self.value == 0:
            raise ZeroDivisionError("Inverting 0?!")
        BF = self.BaseF
        BFmask = (1 << BF.bit_capacity()) - 1
        x_inv  = F(self.p[1:]+[1]) #inverse of F([0,1])
        
        u, v = F(self), F(self.p+[1])
        a, b = F(1),    F(0)
        Bv = BF(self.p[0])
        while True:
            while u.value & BFmask == 0:
                u = u * x_inv
                a = a * x_inv
            if u.value <= BFmask:    
                break
            Bu = BF(u.value & BFmask)
            if v.value > u.value:
                u, v = v, u
                a, b = b, a
                Bu, Bv = Bv, Bu
            u = Bv*u - Bu*v
            a = Bv*a - Bu*b
        return BF(u.value).inv() * a        
    def __truediv__(self, other):
        return self*other.inv()
    def __pow__(self, power):
        'Right-to-left'
        F = type(self)
        a, res = F(self), F(1)
        while True:
            if power & 1: #multiply
                res = a*res
            power >>= 1
            if not power:
                return res
            a  = a * a


class F8(ExtentionField):
    "Rijndael's Polynom 0 = X^8 + X^4 + X^3 + X + 1"
    BaseF = Z2
    p = [1,1,0,1,1,0,0,0]

def bits(val, l):
    res = [0]*l
    for i in range(l):
        res[i] = val & 1
        val >>= 1
    return res
  

class Matrix(object):
    """Matrix is defined by a list of its rows (vectors
     of the Domain vector space , (shall be defined separately).
     Range, if different, shall be defined over the same field."""
    def __init__(self, rows, Domain, Range = None):
        self.Range = Range if Range else Domain
        if Domain.BaseF != self.Range.BaseF:
            raise TypeError("BaseF mismatch")
        self.Domain = Domain
        if  not hasattr(rows,'__iter__'):
            raise TypeError("wrong Matrix initialization")
        self.rows = [Domain(v) for v in rows]
        if len(self.rows) != self.Range.dim():
            raise ValueError("wrong number of rows")
    def size(self):
        return (self.Range.dim(), self.Domain.dim())
    def __iter__(self):
        return iter(self.rows)
    def __eq__(self, other):
        return (self.Domain == other.Domain and
            self.Range == other.Range and
            self.rows == other.rows)
    def __ne__(self, other):
        return not (self == other)
    def __getitem__(self, r):
        return self.rows[r]
    def __setitem__(self, r, v):
        self.rows[r] = v
    def columns(self):
        return zip(*self)
    def __repr__(self):
        res = (repr(r) for r in self.rows)
        res =  'Matrix([\n{}],{},{})'.format(',\n'.join(res),
            self.Domain.__name__,  self.Range.__name__)
        return res
    def __str__(self, mode = 'HW'):
        rows = [str(r) for r in self.rows]
        if mode == 'HW': rows.reverse()
        return '[{}]'.format(',\n '.join(rows))
    def transposed(self):
        m,n = self.size()
        M = Matrix(self.columns(), self.Range, self.Domain)
        return M
    def __add__(self, other):
        v = (a+b for a,b in zip(self, other))
        return Matrix(v, self.Domain, self.Range)
    def __neg__(self):
        v = (-a for a in self)
        return Matrix(v, self.Domain, self.Range)
    def __sub__(self, other):
        return self + (-other)
    def __mul__(self, other):
        if isinstance(other, self.Domain):
            v = (row*other for row in self)
            return self.Range(v)
        elif isinstance(other, Matrix):
            if self.Domain != other.Range:
                raise TypeError("Wrong Matrix multiplication")
            M = other.transposed()
            rows = (self*v for v in M)
            N = Matrix(rows, self.Range, other.Domain)
            return N.transposed()
        else: 
            return NotImplemented
    def __rmul__(self, other):
        if type(other) == Domain.BaseF:
            rows = (other*v for v in M)
            N = Matrix(rows, self.Domain, self.Range)
        else: 
            return NotImplemented
    def inv(self):
        if self.Domain != self.Range:
            raise TypeError("Non-square Matrix cannot be inverted")
        V = self.Domain
        F = V.BaseF
        M = Matrix(self, V)
        N = Matrix(V.basis(), V)
        used = set()
        for c in M.columns():
            r = None
            for i, a in enumerate(c):
                if (i not in used) and a.value:
                    r = i
                    used.add(r)
                    if a.value != 1:
                        b = a.inv()
                        M[r] *= b
                        N[r] *= b
                    break
            if r == None: 
                raise ZeroDivisionError
            for i, a in enumerate(c):
                if a.value and i != r:
                    a = -a
                    M[i] += a*M[r]
                    N[i] += a*N[r]
        v = sorted(zip(M, N), key=lambda p: p[0].value)
        N.rows = list(map(itemgetter(1), v))
        return N

def V2(n, F = Z2):
    class V(VectorSpace):
        dimension = n
        BaseF = F
    return V
    
def RandomMatrix(V, r):
    '''Random Invertible Matrix over V,
        r is used for shuffle'''
    I = Matrix(V.basis(), V)
    X = I + Matrix([0]+I.rows[:-1], V)
    M = I
    for i in range(3):
        r.shuffle(M.rows)
        M = X*M
    return M.inv()
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: 
        if   sys.argv[1] == '-v':
            import doctest
            doctest.testmod()
        elif sys.argv[1] == '-h': 
            print ("Use -v  to run self-test")
     
     