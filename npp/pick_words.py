from gui import clipboard_put
text1 = editor.getSelText()
text = exp_sel()#expands the selection to the word borders
if text == text1: #to bring the punctuation, select a whole word
    text = exp_sel(onlyWordCharacters = False)
clipboard_put(text)
if switch_view():
    editor.addText(text)
    editor.addText('\n')
    switch_view()
    

