from expression import KoalascriptError

codes = {
    "G": "\033[30m",  # Gray
    "r": "\033[31m",  # Red
    "g": "\033[32m",  # Green
    "y": "\033[33m",  # Yellow
    "b": "\033[34m",  # Blue
    "m": "\033[35m",  # Magenta
    "c": "\033[36m",  # Cyan
    "w": "\033[37m",  # White
    "RESET": "\033[0m"
}

def checkArgs(args, a):
    if len(args) < a:
        if a == 1:
            raise KoalascriptError(f"Expected argument")
        else:
            raise KoalascriptError(f"Expected {a} arguments")

def draw(args):
    checkArgs(args, 1)
    if not all(char in "Grgybmcw/" for char in args[0]):
        raise KoalascriptError("Expected character code.\ncodes: Grgybmcw/")
    for char in args[0]:
        end = ""
        if char == "/":
            end = "\n"
            char = ""
        else:
            char = f"{codes[char]}██{codes['RESET']}"
        print(char, end=end)