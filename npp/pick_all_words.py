text1 = editor.getSelText()
text = exp_sel()#expands the selection to the word borders
if text == text1: #to bring the punctuation, select a whole word
    text = exp_sel(onlyWordCharacters = False)
text = text.replace('', ' ')
res = set()

import re
r_word = re.compile(r'\w+', re.UNICODE)
def words(s):
    for m in r_word.finditer(s):
        yield m.group(0)  
        
if switch_view():
    for w in words(text):
        editor.addText(w)
        editor.addText('\n')
    switch_view()
    

