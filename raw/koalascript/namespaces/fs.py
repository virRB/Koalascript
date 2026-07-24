import os
from expression import KoalascriptError 

def checkArgs(args, a):
    if len(args) < a:
        if a == 1:
            raise KoalascriptError(f"Expected argument")
        else:
            raise KoalascriptError(f"Expected {a} arguments")

def exists(args):
    checkArgs(args, 1)
    if not os.path.isabs(args[0]):
        raise KoalascriptError("Expected absolute file path")
    return os.path.exists(args[0])

def create(args):
    checkArgs(args, 1)
    if not os.path.isabs(args[0]):
        raise KoalascriptError("Expected absolute file path")
    if os.path.exists(args[0]):
        raise KoalascriptError("File already exists")
    with open(args[0], "w") as f:
        pass

def join(args):
    checkArgs(args, 2)
    return os.path.join(args[0], args[1])

def absolute(args):
    checkArgs(args, 1)
    return os.path.abspath(args[0])

def writeInto(args):
    checkArgs(args, 2)
    if not os.path.isabs(args[0]):
        raise KoalascriptError("Expected absolute file path")
    if not os.path.exists(args[0]):
        raise KoalascriptError(f"{args[0]} does not exist")
    with open(args[0], "w") as f:
        f.write(args[1])

def readFrom(args):
    checkArgs(args, 1)
    if not os.path.isabs(args[0]):
        raise KoalascriptError("Expected absolute file path")
    if not os.path.exists(args[0]):
        raise KoalascriptError(f"{args[0]} does not exist")
    with open(args[0], "r") as f:
        return f.read()