import logging
from subprocess import run, PIPE
from lib.s3_helper import send_to_s3
from lib.utilities import sanitise_shell_cmd, wait_process_timeout


class DirectoryEnumScanner():

    def __init__(self, tool="dirb", arguments="-f -w -S -r", logger=logging.getLogger(__name__)):
        self.tool = tool
        self.logger = logger
        self.arguments = "".join(sanitise_shell_cmd(arguments))

    def scan(self, hostname):
        if self.tool == "dirb":
            # Assume here that standalone dirb binary is in the PATH
            # This is done in the main handler file
            self.logger.info("[+] Running dirb scan on {}".format(hostname))
            
            # TODO: Change the wordlist path
            p = run(
                ["dirb", hostname, "/app/vendor/dirb222/wordlists/common.txt", self.arguments],
                check=True,
                stdout=PIPE
            )
            scan_result = p.stdout
            try:
                # Even though a lambda function can only run for 15 mins max
                # We should probably kill a scan after 10 mins to be safe
                wait_process_timeout(p, 600)
            except RuntimeError:
                p.kill()
                self.logger.warning("[!] Directory enum timed out, process killed")
                return p.returncode, False
            else:
                return p.returncode, scan_result
        else:
            self.logger.error("[-] Unrecognized/unsupported tool for scan.")
