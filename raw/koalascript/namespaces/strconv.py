from expression import KoalascriptError

def toI(args):
    if len(args) < 1:
        raise KoalascriptError("Expected argument")
    try:
        return int(args[0])
    except ValueError:
        raise KoalascriptError(f"Cannot convert {args[0]} to integer")
    
def toS(args):
    if len(args) < 1:
        raise KoalascriptError("Expected argument)")
    return str(args[0])