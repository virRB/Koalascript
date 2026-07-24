from expression import KoalascriptError

def removeAll(args):
    if len(args) < 2:
        raise KoalascriptError("Expected 2 arguments (line, character)")
    what = args[0]
    char = args[1]
    char = str(char)
    what = str(what)
    return what.replace(char, "")

def clean(args):
    if len(args) < 1:
        raise KoalascriptError("Expected argument (line)")
    what = args[0]
    what = str(what)
    return what.strip()

def contains(args):
    if len(args) < 2:
        raise KoalascriptError("Expected 2 arguments (line, text)")
    what = args[0]
    what = str(what)
    text = args[1]
    text = str(text)
    if text in what:
        return True
    else:
        return False
    
def length(args):
    if len(args) < 1:
        raise KoalascriptError("Expected argument (line)")
    what = args[0]
    what = str(what)
    return len(what)