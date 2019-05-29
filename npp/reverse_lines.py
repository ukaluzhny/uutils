editor.beginUndoAction()

s = editor.getSelText()
editor.replaceSel('\n'.join(reversed(s.splitlines())))

editor.endUndoAction()
