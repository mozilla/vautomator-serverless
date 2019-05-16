import shlex
import time
import os
import subprocess
import tarfile
import io


def sanitise_shell_cmd(command):
    return shlex.split(shlex.quote(command))


def uppath(filepath, n):
    return os.sep.join(filepath.split(os.sep)[:-n])


def package_results(source_dir, out_file=None):
    if out_file:
        # Write to file on disk

        return out_file
    else:
        targz = io.BytesIO()
        with tarfile.open(mode="w:gz", fileobj=targz) as tar:
            tar.add(source_dir, arcname=os.path.sep)
        return targz
