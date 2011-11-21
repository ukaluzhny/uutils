from re import *
r_word = compile(r'\b\w+\b')
def Word1(s):
    try:
        return r_word.search(s).group()
    except AttributeError:
        return ''
def Word2(s):
    try:
        pos = r_word.search(s).end()
        return r_word.search(s[pos + 1:]).group()
    except AttributeError:
        return ''

def Payload(l, after  = ' ', before = ''):
    offset = len(after)
    pos = l.find(after)
    pos_l = -1
    if before:
        pos_l = l.find(before)
    if pos_l == -1: 
        pos_l = len(l)
    return l[pos + offset:pos_l].strip() if pos != -1 else ''

def Word3(s):
    "Actually, returns everything after the second word"
    pos = r_word.search(s).end() + 1
    s = s[pos:].strip()
    return Payload(s)


class ReD(object):
    def __init__(self, defs = {}, flags= None):
        self.defs = defs
        self.re_defs = None
        self.flags = flags
    def __setitem__(self, key, val):
        self.defs[key] = val
        self.re_defs = None
    def __contains__(self, key):
        return key in self.defs
    def __delitem__(self, key):
        try:
            del self.defs[key]
            self.re_defs = None
        except KeyError:
            print "Tried to undef %s; " % key
    def __call__(self, text):
        if not self.re_defs and self.defs:
            v = '|'.join(self.defs.keys())
            v = r'\b(%s)\b' % v
            if self.flags:
                self.re_defs = compile(v, self.flags)
            else: 
                self.re_defs = compile(v)
        t = text[:]
        for i in range(100):
            if self.defs:
                t = self.re_defs.sub(lambda m: self.defs[m.group(0)], t)
            if t == text:
                break
            text = t[:]
        if i == 99:
            raise Exception("Possibly iterative definition in %s" % self.defs) 
        return text
    def __repr__(self):
        return repr(self.defs)

def splitter(keywords_list):
    return compile('(%s)'%'|'.join(keywords_list), 
        MULTILINE)
def Erase(s, *l):
    for i in l:
        r = compile(i, M)
        s = r.sub('', s)
    return s
def myhex(x, n):
    s = (hex(x)[2:]).replace("L", "")
    return '0x%s' % s.zfill(n)
 
 
if __name__ == "__main__":    
    text = '''
    a
    //ghgh   bb
    cc /*3c*/jkjk
    cc/*3c*/ jkjk
    a#c hkjh //new
    old
    /*
    ghgh
    klkjlk
    */ jkj;l
    '''
    print text
       
    d = {'a':'b', 'c':'d', 'b':'='}
    defs = ReD(d)
    print defs(text)
    defs['jkjk'] = 'dodo'
    print defs(text)
    print 'jkjk' in defs
    del defs['jkjk']
    print defs(text)
    
     
