import nmap
import os
import time


class PortScanner():

    def __init__(self):
        # This is needed for nmap static library to be added to the path
        # os.environ['PATH'] = os.environ['PATH'] \
        #    + ':' + os.environ['LAMBDA_TASK_ROOT'] \
        #    + '/bin/nmap-standalone/'
        return None
    
    def scanTCP(self, host):
        # TODO: There is an async scan option in python-nmap, use that instead
        nm = nmap.PortScanner()
        isSudo = False
        nmap_arguments = ("-v -Pn -sT -sV --script=banner " +
                          "--top-ports 1000 --open -T4 --system-dns"
                          )
        results = nm.scan(host, arguments=nmap_arguments, sudo=isSudo)
        time.sleep(120)

        return results

