import logging
import os
from subprocess import run, PIPE
from lib.s3_helper import send_to_s3
from lib.utilities import sanitise_shell_cmd, wait_process_timeout


class DirectoryEnumScanner():

    def __init__(self, tool='dirb', arguments="-f -w -S -r", wordlist='short', logger=logging.getLogger(__name__)):
        self.tool = tool
        self.logger = logger
        self.arguments = "".join(sanitise_shell_cmd(arguments))
        self.wordlist = wordlist

    def scan(self, hostname):
        # Not very elegant, but for test purposes,
        # we need to know if we are running in Lambda
        if "LAMBDA_ENV" in os.environ and os.environ["LAMBDA_ENV"] == "true":
            path_prefix = os.environ['LAMBDA_TASK_ROOT']
        else:
            path_prefix = os.path.dirname(os.path.realpath(__file__))
        # Now decide on the wordlist
        wordlist_options = {
            'short': path_prefix + "/vendor/dirb/wordlists/custom/RobotsDisallowed-Top1000.txt",
            'medium': path_prefix + "/vendor/dirb/wordlists/custom/quickhits.txt",
            'long': path_prefix + "/vendor/dirb/wordlists/custom/common.txt"
        }
        # Currently no other tools other than dirb is supported,
        # but maybe we should explore gobuster here too
        if self.tool == "dirb":
            # Assume here that standalone dirb binary is in the PATH
            # This is done in the main handler file
            self.logger.info("[+] Running dirb scan on {}".format(hostname))

            results = {}
            direnum_results = []
            results['routes'] = direnum_results
            results['host'] = hostname
            
            p = run(
                ["dirb", hostname, wordlist_options[self.wordlist], self.arguments],
                check=True,
                stdout=PIPE
            )
            direnum_results = p.stdout
            try:
                # Even though a lambda function can only run for 15 mins max
                # We should probably kill a scan after approx. 12 mins to be safe
                wait_process_timeout(p, 720)
            except RuntimeError:
                p.kill()
                self.logger.warning("[!] Directory enum timed out, process killed")
                # TODO: Remove me later, for debug
                print("Dir enum output when killed because of timeout:" + direnum_results)
                return p.returncode, False
            else:
                return p.returncode, results
        else:
            self.logger.error("[-] Unrecognized/unsupported tool for scan.")
