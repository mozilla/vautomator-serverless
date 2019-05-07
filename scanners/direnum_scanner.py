import logging
import os
import platform
import subprocess
from lib.s3_helper import send_to_s3
from lib.utilities import uppath


class DirectoryEnumScanner():

    def __init__(self, tool='dirb', arguments_list=['-f', '-w', '-S', '-r'], wordlist='short', logger=logging.getLogger(__name__)):
        self.tool = tool
        self.logger = logger
        self.arguments = arguments_list
        self.wordlist = wordlist

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
            if "Darwin" in platform.platform():
                dirb = "dirb-osx"
            elif "Linux" in platform.platform():
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
            self.logger.info("[+] Running dirb scan on {}".format(hostname))

            results = {}
            direnum_results = []
            results['host'] = hostname
            process_args = [dirb, "https://" + hostname, wordlist_options[self.wordlist]]
            process_args.extend(self.arguments)

            try:
                # Even though a lambda function can only run for 15 mins max
                # We should probably kill a scan after approx. 12 mins to be safe
                p = subprocess.run(
                    process_args,
                    check=True,
                    stdout=subprocess.PIPE,
                    encoding='utf-8',
                    timeout=720
                )
            except Exception as e:
                # If we are here, either the command did not run, or
                # it did run but got killed after the timeout period
                if isinstance(e, subprocess.TimeoutExpired):
                    self.logger.warning("[!] Directory enum timed out, process killed")
                    direnum_results = p.stdout
                    results['routes'] = direnum_results
                    return p.returncode, results
                elif isinstance(e, subprocess.CalledProcessError):
                    self.logger.error("[-] dirb could not run: {}".format(e))
                    direnum_results = p.stdout
                    results['routes'] = direnum_results
                    return p.returncode, results
                else:
                    self.logger.error("[-] Process ended unexpectedly: {}".format(e))
                    return p.returncode, False
            else:
                # No exception, dirb ran and finished on time
                direnum_results = p.stdout
                results['routes'] = direnum_results
                return p.returncode, results
        else:
            self.logger.error("[-] Unrecognized/unsupported tool for scan.")
