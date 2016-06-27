editor.beginUndoAction()
s = editor.getSelText()
s1 = s.replace(",", "")
s1 = s1.replace(" ", "_")
s1 = s1.replace("-", "_")
if s1 == s:
    s1 = s.replace("_", " ")
editor.replaceSel(s1)
editor.endUndoAction()
