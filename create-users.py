# Allows all following functions to work based on running this script
from os.path import dirname, abspath
from os import chdir
from sys import path
from modules.classes import User

# Set the root directory as the working directory
script_root = dirname(abspath(__file__))
print(f"Changing working dir to {script_root}")
chdir(script_root)

hello = User()
hello.CreateRandom()
print(hello.ToString())
hello.ToJSON(f"{script_root}\\tests\\users\\json")