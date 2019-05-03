import shlex
import time


def sanitise_shell_cmd(command):
    return shlex.split(shlex.quote(command))


def wait_process_timeout(proc, seconds):
        """Wait for a process to finish, or raise exception after timeout"""
        start = time.time()
        end = start + seconds
        interval = min(seconds / 1000.0, 0.25)

        while True:
            result = proc.poll()
            if result is not None:
                return result
            if time.time() >= end:
                raise RuntimeError("Process timed out")
            time.sleep(interval)
