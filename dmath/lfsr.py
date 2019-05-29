def parity(w):
    "xor of all bits of a 64-bit word"
    w ^= w >> 32
    w ^= w >> 16
    w ^= w >> 8
    w ^= w >> 4
    w ^= w >> 2
    w ^= w >> 1
    return w & 1

def mult_table(lfsr):
    r = lfsr(1)
    table = [r.value]
    for i in range(2 * r.deg):
        r.shift('r')
        table.append(r.value)
    return table

class LFSR(object):
    def __init__(self, value):
        self.value = value
        self.deg  = self.p.bit_length() - 1
        self.msbit = 1 << self.deg
    def __str__(self):
        return "{{:0{}b}}".format(self.deg).format(self.value)
    def shift(self, direction):
        if direction == 'r':
            self.value <<= 1
            if self.value & self.msbit:
                self.value ^= self.p
        elif direction == 'l':
            if self.value & 1:
                self.value ^= self.p
            self.value >>= 1
        else: raise ValueError("Unrecognized shift direction")
    def reverse_bits(self):
        res, res_bit, val = 0, 1, self.value
        for i in range(self.deg):
            val <<= 1
            if val & self.msbit: res ^= res_bit
            res_bit <<= 1
        return res
    def __mul__(self, other):
        res = 0
        val = self.value << self.deg
        other = other.reverse_bits()
        for i in range(2*self.deg):
            val >>= 1    
            if parity(val & other):
                res ^= self.mult_table[i]
            # print('{:32b}\n{:32b}, {:16b}'.format(val, other, res))
        res = type(self)(res)
        res.mult_table = self.mult_table
        return res
    def __pow__(self, power):
        'secure self**power by Montgomery ladder'
        x = type(self)(1)
        x.mult_table = self.mult_table
        y = self
        for i in range(self.deg):
            power <<= 1    
            if power & self.msbit: 
                x = x*y
                y = y*y
            else: 
                y = x*y
                x = x*x
        return x


class LFSR16(LFSR):
    p = (1<<16)|(1<<12)|(1<<3)|(1<<1)|1


from random import getrandbits as grb
def test():
    F = LFSR16
    mtable = mult_table(F)
    X = grb(F.p.bit_length() - 1)        
    a = F(1)
    a.shift('r')
    a.mult_table = mtable
    a = a ** X

    b = F(1)
    b.shift('l')
    b.mult_table = mtable
    b = b ** X

    assert (a*b).value == 1
test_pow()
