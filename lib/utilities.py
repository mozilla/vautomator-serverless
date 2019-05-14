import shlex
import time
import os
import subprocess
import tarfile


def sanitise_shell_cmd(command):
    return shlex.split(shlex.quote(command))


def uppath(filepath, n):
    return os.sep.join(filepath.split(os.sep)[:-n])


def package_results(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as targz:
        targz.add(source_dir, arcname=os.path.basename(source_dir))
        return targz
