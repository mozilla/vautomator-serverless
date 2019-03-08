import nmap
import os
import time


class PortScanner():

    def __init__(self):
        os.environ['PATH'] = os.environ['PATH'] + ':' + os.environ['LAMBDA_TASK_ROOT'] + '/bin/nmap-standalone/'
        return None

    def scanUDP(self, host):
        # TODO: There is an async scan option in python-nmap, use that instead
        # Lambda does not run in the context of root & there is no sudo
        # So we won't be able to run UDP scans
        nm = nmap.PortScanner()
        isSudo = True
        udp_ports = (
            "17,19,53,67,68,123,137,138,139,"
            "161,162,500,520,646,1900,3784,3785,5353,27015,"
            "27016,27017,27018,27019,27020,27960"
        )
        nmap_arguments = "-v -Pn -sU --open -T4 --system-dns"
        results = nm.scan(host, ports=udp_ports, arguments=nmap_arguments, sudo=isSudo)
        time.sleep(120)
        
        return results
    
    def scanTCP(self, host):
        # TODO: There is an async scan option in python-nmap, use that instead
        nm = nmap.PortScanner()
        isSudo = False
        nmap_arguments = "-v -Pn -sT -sV --script=banner --top-ports 1000 --open -T4 --system-dns"
        results = nm.scan(host, arguments=nmap_arguments, sudo=isSudo)
        time.sleep(120)

        return results

