from gui import clipboard_put
text1 = editor.getSelText()
text = exp_sel()
if text == text1:
    text = exp_sel(onlyWordCharacters = False)
clipboard_put(text)
if switch_view():
    editor.addText(text)
    editor.addText('\n')
    switch_view()

