from __future__ import print_function
from os.path import join
from shutil import copyfile
from random import getrandbits as grb 

# from projectoxford.speech import SpeechClient
# sc = SpeechClient("f59d2eac74004563b7edddcea5ad1abc", 
    # gender='Female', locale='en-US')
# wav = sc.say_to_wav(e, filename)

def ws(d):
    'd is (word, meaning, example, hmeaning, hexample)'
    s = "[sound:{}]"
    w = "{}.mp3"
    m = "{}_meaning.mp3"
    e = "{}_example.mp3"
    source = r"C:\Users\ukaluzhn\Documents\Anki\test_User\collection.media"
    dest = r"C:\Users\ukaluzhn\Dropbox\English\anki.mp3"
    for l in d: # word, meaning, example, hmeaning, hexample
        word = l[0]
        for frmt in [w, m, e]:
            f = frmt.format(word)
            copyfile(join(source, f), join(dest, f))
            l.append(s.format(f))

            
def anki_notes():
    from anki import ws
    for i in d:
        i += h[:2]
        h = h[2:]
    ws(d)    
            