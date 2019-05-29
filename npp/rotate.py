editor.beginUndoAction()

s = editor.getSelText()

editor.replaceSel(
    '\n'.join(
     ''.join(t) for t in zip(*reversed(s.splitlines()))
    )
)

editor.endUndoAction()
