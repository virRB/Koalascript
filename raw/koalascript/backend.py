import sys
import os
import shutil
import subprocess

RESET = "\033[0m"
CYAN = "\033[36m"
RED = "\033[91m"

HERE = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    print(f"{CYAN}KoalaScript v1.0\nCopyright (c) VirRB{RESET}")
    sys.exit()

if sys.argv[1] == "run":
    if len(sys.argv) < 3:
        print(f"{CYAN}kls run <script name>{RESET}")
        sys.exit()
    project = os.getcwd()
    file = os.path.join(HERE, "parser.py")
    if len(sys.argv) >= 4:
        subprocess.run([sys.executable, file, project, sys.argv[2], *sys.argv[3:]])
    else:
        subprocess.run([sys.executable, file, project, sys.argv[2], "__NO-ARGUMENTS__"])
elif sys.argv[1] == "version":
    print(f"{CYAN}KoalaScript v1.0\nCopyright (c) VirRB{RESET}")
elif sys.argv[1] == "build":
    TEMPLATE = os.path.join(HERE, "template")
    directory = os.getcwd()
    if len(sys.argv) < 3:
        print(f"{CYAN}kls build <project name>{RESET}")
        sys.exit()
    DEST = os.path.join(directory, sys.argv[2])
    if os.path.exists(DEST):
        print(f"{RED}Folder {DEST} already exists{RESET}")
        sys.exit()
    shutil.copytree(TEMPLATE, DEST)