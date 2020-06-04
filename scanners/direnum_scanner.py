import logging
import os
import sys
import subprocess
from lib.s3_helper import send_to_s3
from lib.utilities import uppath


class DirectoryEnumScanner():

    def __init__(self, tool='dirb', arguments_list=['-f', '-w', '-S', '-r'], wordlist='short', logger=logging.getLogger(__name__)):
        self.tool = tool
        self.logger = logger
        self.arguments = arguments_list
        assert self._valid_wordlist(wordlist)
        self.wordlist = wordlist

    @classmethod
    def _valid_wordlist(self, wordlist_candidate):
        # It must be a str
        if isinstance(wordlist_candidate, str):
            # It must not be empty
            if wordlist_candidate:
                valid_types = ['short', 'medium', 'long']
                if wordlist_candidate in valid_types:
                    return True
        return False

    def scan(self, hostname):
        # Not very elegant, but for test purposes,
        # we need to know if we are running in Lambda
        if "LAMBDA_ENV" in os.environ and os.environ["LAMBDA_ENV"] == "true":
            path_prefix = os.environ['LAMBDA_TASK_ROOT']
            # We know we are in Amazon Linux
            dirb = "dirb"
        else:
            path_prefix = uppath(os.path.realpath(__file__), 2)
            # Here we also need to check the local platform we are
            # running. This is because we have 2 vendored binaries
            # for dirb, one for OSX and one for Linux
            if sys.platform.startswith('darwin'):
                dirb = "dirb-osx"
            elif sys.platform.startswith('linux'):
                dirb = "dirb"
            else:
                self.logger.error("[-] Unable to run dirb, unidentified or unsupported architecture.")

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
            self.logger.info("Running dirb scan on {}...".format(hostname))

            results = {}
            lines = []
            trimmed_results = []
            results['output'] = trimmed_results
            results['host'] = hostname
            process_args = [dirb, "https://" + hostname, wordlist_options[self.wordlist]]
            process_args.extend(self.arguments)

            try:
                p = subprocess.Popen(
                    process_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    shell=False
                )
            except Exception as e:
                self.logger.error("[-] File/executable not found, or an unexpected error occurred: {}".format(e))
                return False, False
            else:
                try:
                    # Even though a lambda function can only run for 15 mins max
                    # # We should probably kill a scan after 10 mins to be safe
                    dirb_out, dirb_err = p.communicate(timeout=600)
                except subprocess.TimeoutExpired:
                    # If we are here, the command did run but got
                    # killed after the timeout period
                    self.logger.warning("[!] Directory enum timed out, killing process.")
                    p.kill()
                    dirb_out, dirb_err = p.communicate()
                    lines = dirb_out.split('\n')
                    for line in lines:
                        if line.startswith("URL") or line.startswith("WORDLIST") or "http" in line:
                            results['output'].append(line)
                    results['errors'] = dirb_err.join(' (TIMEDOUT)')
                else:
                    # No exception, dirb ran and finished on time
                    lines = dirb_out.split('\n')
                    for line in lines:
                        if line.startswith("URL") or line.startswith("WORDLIST") or "http" in line:
                            results['output'].append(line)
                    results['errors'] = dirb_err
                finally:
                    return p.returncode, results
        else:
            self.logger.error("[-] Unrecognized/unsupported tool for scan.")
