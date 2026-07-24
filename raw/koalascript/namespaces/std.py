import sys
import subprocess

def c_out(what):
    what = what[0]
    what = str(what)
    if what.endswith(r"\n"):
        what = what.removesuffix(r"\n")
        print(what)
    else:
        print(what, end="")

def c_in(args):
    return input("> ")

def c_exit(args):
    sys.exit()

def c_clear(args):
    subprocess.run("cls", shell=True)