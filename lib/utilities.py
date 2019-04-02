import shlex


def sanitise_shell_cmd(command):
    return shlex.split(shlex.quote(command))
    