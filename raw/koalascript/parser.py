import os
import sys
import time
import re
from expression import *
from namespaces.std import *
from namespaces.s import *
from namespaces.strconv import *
from namespaces.fs import *
from namespaces.lmn import *

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(HERE, "main.kls")

RESET = "\033[0m"
CYAN = "\033[36m"
RED = "\033[91m"

if len(sys.argv) < 4:
    print("What?")
    sys.exit()

if not os.path.exists(sys.argv[1]):
    print(f"{RED}Cannot find base program directory: {sys.argv[1]}{RESET}")
    sys.exit()

BASE = sys.argv[1]
MAIN = os.path.join(BASE, sys.argv[2])

arguments = None

if sys.argv[3] == "__NO-ARGUMENTS__":
    arguments = []
else:
    arguments = sys.argv[3:]

if not os.path.exists(MAIN):
    print(f"{RED}Cannot find program file: {MAIN}{RESET}")
    sys.exit()

def resolveValues(expr):
    result = []
    token = ""
    depth = 0
    inString = False
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == '"':
            inString = not inString
            token += ch
            i += 1
            continue
        if not inString:
            if ch == "<":
                depth += 1
                token += ch
                i += 1
                continue
            if ch == ">":
                depth -= 1
                token += ch
                i += 1
                continue
            if depth == 0:
                if i + 1 < len(expr):
                    op = expr[i:i+2]
                    if op in ("==", "!=", ">=", "<="):
                        if token.strip():
                            value = parseValue(token.strip())
                            if isinstance(value, str):
                                result.append(f'"{value}"')
                            else:
                                result.append(str(value))
                            token = ""
                        result.append(op)
                        i += 2
                        continue
                if ch in "+-*/":
                    if token.strip():
                        value = parseValue(token.strip())
                        if isinstance(value, str):
                            result.append(f'"{value}"')
                        else:
                            result.append(str(value))
                        token = ""

                    result.append(ch)
                    i += 1
                    continue
        token += ch
        i += 1
    if token.strip():
        value = parseValue(token.strip())
        if isinstance(value, str):
            result.append(f'"{value}"')
        else:
            result.append(str(value))
    return " ".join(result)

def getInner(line, start=["<"], end=[">"]):
    piece = ""
    recording = False
    inString = False
    depth = 0
    for char in line:
        if char == '"':
            if inString:
                inString = False
            else:
                inString = True
        if char in start and not inString:
            if depth == 0:
                recording = True
                depth = depth + 1
            else:
                if recording:
                    piece = piece + char
                depth = depth + 1
        elif char in end and not inString:
            if depth == 1:
                recording = False
            else:
                if recording:
                    piece = piece + char
                depth = depth - 1
        else:
            if recording:
                piece = piece + char
    return piece

res = "§"

def screwStrings(what):
    screw = "x"
    result = ""
    screwing = False
    for char in what:
        if char == '"':
            screwing = not screwing
        if screwing:
            result = result + screw
        else:
            result = result + char
    return result


def splitAt(word, start=["<"], end=[">"]):
    tokens = []
    gen = ""
    depth = 0
    for char in word:
        if char in end:
            if depth == 1:
                tokens.append(gen)
                gen = ""
            else:
                gen = gen + char
            depth = depth - 1
        elif char in start:
            if depth == 0:
                tokens.append(gen)
                gen = ""
            else:
                gen = gen + char
            depth = depth + 1
        else:
            gen = gen + char
    tokens = [t for t in tokens if t.strip()]
    if gen:
        tokens.append(gen)
    return tokens


def getInnerParams(what, splt=",", start=["<"], end=[">"]):
    line = []
    inString = False
    if what.strip() == "":
        return []
    for char in what:
        line.append(char)
    depth = 0
    for i in range(len(line)):
        char = line[i]
        if char == '"':
            if inString:
                inString = False
            else:
                inString = True
        if char == splt and depth == 0 and not inString:
            line[i] = res
        elif char in start and not inString:
            depth = depth + 1
        elif char in end and not inString:
            depth = depth - 1
    result = ""
    for l in line:
        result = result + l
    return result.split(res)

def interpolate(text):
    def repl(match):
        expr = match.group(1)
        return str(parseValue(expr))

    return re.sub(r"%%(.*?)%%", repl, text)

ver = "normal"
variables = {}
functions = {}
func = {
    "executing": "",
    "wasFuncHeader": False,
    "inFunc": False,
    "braceDepth": 0
}

def getArgument(args):
    index = int(args[0])
    if index >= len(arguments):
        raise KoalascriptError("Argument index out of range")
    return arguments[index]


def to_py(l):
    if not l.startswith("(") or not l.endswith(")"):
        raise KoalascriptError("Expected array")
    l = l.removeprefix("(").removesuffix(")")
    a = getInnerParams(l)
    output = []
    for param in a:
        output.append(parseValue(param))
    return output

def s_array(args):
    return "(" + ",".join(map(str, args)) + ")"

def s_len(args):
    if len(args) != 1:
        raise KoalascriptError("Expected argument")
    return len(to_py(args[0]))

def s_get(args):
    if len(args) != 2:
        raise KoalascriptError("Expected 2 arguments")
    arr = args[0]
    arr = to_py(arr)
    index = args[1]
    try:
        return arr[index]
    except IndexError:
        raise KoalascriptError("Invalid index")

modules = {
    "s": {
        "removeAll": removeAll,
        "clean": clean,
        "contains": contains,
        "length": length
    },
    "std": {
        "out": c_out,
        "in": c_in,
        "exit": c_exit,
        "clear": c_clear,
        "getArgument": getArgument,
        "array": s_array,
        "get": s_get,
        "length": s_len
    },
    "strconv": {
        "toI": toI,
        "toS": toS
    },
    "fs": {
        "exists": exists,
        "absolute": absolute,
        "writeInto": writeInto,
        "readFrom": readFrom,
        "create": create,
        "join": join
    },
    "lmn": {
        "drawf": draw
    }
}

ifs = {
    "in": False,
    "nest": -1,
    "body": [],
    "wasHeader": False
}

imported = []

def isInt(what):
    try:
        int(what)
        return True
    except ValueError:
        return False
    except:
        raise KoalascriptError("Failed to identify integer")
    
def getWordTil(word, t="<"):
    result = ""
    for char in word:
        if char == t:
            return result
        result += char
    return result
    
def parseFunction_m(what, args=None):
    if args is None:
        args = []
    for mod in modules:
        if what.startswith(f"{mod}::"):
            if mod not in imported:
                raise KoalascriptError(f"Namespace {mod} has not been added to script")
            what = what.removeprefix(f"{mod}::")
            f = getWordTil(what)
            args = getInnerParams(getInner(what))
            for i, arg in enumerate(args):
                args[i] = parseValue(arg)
            if f not in modules[mod]:
                raise KoalascriptError(f"Function {f} not found in namespace {mod}")
            try:
                return modules[mod][f](args)
            except IndexError:
                raise KoalascriptError(f"One or more arguments are missing")
    raise KoalascriptError(f"Unknown namespace used in {what}")

def parseValue(val):
    val = val.strip()
    if val.startswith('"') and val.endswith('"'):
        s = val.removeprefix('"').removesuffix('"')
        return interpolate(s)
    elif any(val.startswith(f"{mod}::") for mod in imported):
        return parseFunction_m(val)
    elif isInt(val):
        return int(val)
    elif val == "file":
        return os.path.dirname(os.path.abspath(__file__))
    elif (ver == "normal" and any(var == val for var in variables)) or (ver == "function" and any(var == val for var in functions[func["executing"]]["variables"])):
        if ver == "function" and any(var == val for var in functions[func["executing"]]["variables"]):
            return functions[func["executing"]]["variables"][val]
        else:
            return variables[val]
    elif any(op in val for op in OPERATORS):
        what = resolveValues(val)
        return evaluate(what)
    elif any(val.startswith(f + "<") for f in functions):
        name = getWordTil(val)
        params = [parseValue(p) for p in getInnerParams(getInner(val))]
        return parseFunction(name, params=params)
    elif val == "void":
        return None
    elif val == "true":
        return True
    elif val == "false":
        return False
    elif val == "cwd":
        return os.getcwd()
    elif val == "What do koala's like to eat?":
        return "Fried chicken"
    elif val == "ver":
        return ver
    else:
        raise KoalascriptError(f"Invalid value {val}")
    
def pushVar(name, val):
    global ver
    if ver == "normal":
        variables[name] = val
    elif ver == "function":
        functions[func["executing"]]["variables"][name] = val

def parseFunction(name, params=None):
        global ver
        r = None
        if params is None:
            params = []
        try:
            for i, p in enumerate(functions[name]["variables"]):
                if p in functions[name]["params"]:
                    functions[name]["variables"][p] = params[i]
        except IndexError:
            raise KoalascriptError("Expected argument")
        old = func["executing"]
        oldver = ver
        func["executing"] = name
        ver = "function"
        ifNest = 0
        for line in functions[name]["body"]:
            if line.startswith("return"):
                line = line.removeprefix("return")
                line = line.strip()
                if line == "":
                    r = None
                    break
                else:
                    line = parseValue(line)
                    r = line
                    break
            parse(line)
        ver = oldver
        func["executing"] = old
        for v in functions[name]["variables"]:
            functions[name]["variables"][v] = None
        return r


forLoops = {
    "depth": 0,
    "variable": "",
    "range": 0,
    "in": False,
    "body": [],
    "wasHeader": False
}

def parse(what, priority=False):
    global ver
    try:
        if ifs["in"] and not ifs["body"][ifs["nest"]] and what != "}" and not what.startswith("priority") and not priority:
            return
    except IndexError:
        raise KoalascriptError("Something went wrong while attempting to skip an if block")
    if what.startswith("//"):
        return
    if what == "{":
        if forLoops["wasHeader"]:
            forLoops["wasHeader"] = False
            forLoops["in"] = True
            forLoops["depth"] = 1
        elif ifs["wasHeader"]:
            ifs["wasHeader"] = False
            ifs["in"] = True
        elif func["wasFuncHeader"]:
            func["wasFuncHeader"] = False
            func["inFunc"] = True
    elif what == "}":
        if ifs["in"]:
            ifs["nest"] = ifs["nest"] - 1
            if ifs["nest"] <= -1:
                ifs["in"] = False
                ifs["nest"] = -1
        elif func["inFunc"]:
            func["inFunc"] = False
            func["executing"] = ""
    elif what.startswith("var "):
        what = what.removeprefix("var")
        what = what.strip()
        if "=" not in what:
            raise KoalascriptError("Expected seperator")
        var, val = what.split("=")
        var = var.strip()
        val = val.strip()
        val = parseValue(val)
        pushVar(var, val)
    elif (any(what.startswith(f"{var} =") for var in variables) and ver == "normal") or (ver == "function" and any(what.startswith(f"{var} =") for var in functions[func["executing"]]["variables"])):
        if "=" not in what:
            raise KoalascriptError("Expected seperator")
        name, val = what.split("=")
        name = name.strip()
        val = val.strip()
        if name not in variables:
            raise KoalascriptError(f"Variable {name} not found")
        val = parseValue(val)
        pushVar(name, val)
    elif what.startswith("with"):
        what = what.removeprefix("with")
        what = what.strip()
        what = parseValue(what)
        imported.append(what)
    elif what.startswith("for"):
        what = getInnerParams(getInner(what), splt=";")
        if len(what) != 2:
            raise KoalascriptError(f"Expected 2 arguments, recieved {len(what)}")
        if not what[0].startswith("init"):
            raise KoalascriptError("Expected initialisation")
        if not what[1].startswith("til"):
            raise KoalascriptError("Expected range")
        v = what[0].removeprefix("init")
        v = v.strip()
        r = what[1].removeprefix("til")
        r = r.strip()
        r = parseValue(r)
        if not isinstance(r, int):
            raise KoalascriptError(f"Expected integer, recieved {type(r).__name__}")
        forLoops["variable"] = v
        forLoops["range"] = r
        forLoops["wasHeader"] = True
    elif any(what.startswith(f"{mod}::") for mod in imported):
        parseFunction_m(what)
    elif what.startswith("fn") and (not func["inFunc"] or not func["wasFuncHeader"]):
        what = what.removeprefix("fn")
        func["braceDepth"] = 1
        what = what.strip()
        name = getWordTil(what)
        params = getInnerParams(getInner(what))
        functions[name] = {}
        functions[name]["variables"] = {}
        for param in params:
            functions[name]["variables"][param] = None
        functions[name]["params"] = params
        func["wasFuncHeader"] = True
        func["executing"] = name
        functions[name]["body"] = []
    elif what.startswith("if"):
        condition = getInner(what)
        shouldExec = parseValue(condition)
        ifs["wasHeader"] = True
        ifs["nest"] = ifs["nest"] + 1
        ifs["body"].append(shouldExec)
    elif any(what.startswith(f + "<") for f in functions):
        name = getWordTil(what)
        params = [parseValue(p) for p in getInnerParams(getInner(what))]
        parseFunction(name, params=params)
    elif what.startswith("global"):
        l = getInner(what)
        oldver = ver
        ver = "normal"
        parse(l)
        ver = oldver
    elif what.startswith("priority"):
        l = getInner(what)
        parse(l, priority=True)
    else:
        raise KoalascriptError(f"Invalid syntax: {what}")



def executeLines(lines, ignoreSemi=False):
    global forLoops, func

    for i, line in enumerate(lines, start=1):
        line = line.strip()

        if "//" in line and not line.startswith("//"):
            line = line.split("//")[0]

        if not line:
            continue

        headers = ["fn", "if", "for"]

        if (
            not line.endswith(";")
            and not any(line.startswith(header) for header in headers)
            and line != "}"
            and line != "{"
            and not line.startswith("//")
            and not ignoreSemi
        ):
            print(f"{RED}Error in line {i}: Expected semicolon: {line}{RESET}")
            sys.exit()

        line = line.removesuffix(";")

        if forLoops["in"]:
            if line == "{":
                forLoops["depth"] += 1
            elif line == "}":
                forLoops["depth"] -= 1
                if forLoops["depth"] == 0:
                    forLoops["in"] = False

                    v = forLoops["variable"]
                    r = forLoops["range"]
                    b = forLoops["body"]

                    forLoops = {
                        "depth": 0,
                        "variable": "",
                        "range": 0,
                        "in": False,
                        "body": [],
                        "wasHeader": False
                    }

                    for j in range(r):
                        pushVar(v, j)
                        executeLines(b, ignoreSemi=True)
                    continue

            forLoops["body"].append(line)
            continue

        if func["inFunc"]:
            if line == "{":
                func["braceDepth"] += 1
            elif line == "}":
                func["braceDepth"] -= 1
                if func["braceDepth"] == 0:
                    func["inFunc"] = False
                    continue

            functions[func["executing"]]["body"].append(line)
            continue

        try:
            parse(line)

        except KoalascriptError as k:
            print(f"{RED}Error in line {i}: {k}{RESET}")
            sys.exit()

        except RecursionError:
            print(f"Infinite loop found at line {i}")

        except Exception as e:
            print(f"{RED}An unexpected error occoured{RESET}")
            choice = input("View original traceback? (y/n)>")

            if choice == "y":
                print(f"{RED}{e}{RESET}")
            else:
                print(f"{CYAN}Okay...{RESET}")

            sys.exit()

with open(MAIN, "r") as f:
    lines = f.readlines()
    start = time.perf_counter()
    executeLines(lines)
    end = time.perf_counter()
    elapsed = (end - start) * 1000
    print(f"\n\n{CYAN}Script ran in {elapsed:.3f} ms{RESET}")