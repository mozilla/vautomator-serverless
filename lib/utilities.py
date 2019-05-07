import shlex
import time
import os
import subprocess


def sanitise_shell_cmd(command):
    return shlex.split(shlex.quote(command))
    

def uppath(filepath, n):
    return os.sep.join(filepath.split(os.sep)[:-n])
