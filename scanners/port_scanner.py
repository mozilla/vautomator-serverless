import nmap
from util.s3_helper import send_to_s3


class PortScanner():

    def __init__(self, hostname):
        self._host = hostname
    
    def scanTCP(self):
        # TODO: There is an async scan option in python-nmap, use that instead
        nma = nmap.PortScannerAsync()
        isSudo = False
        nmap_arguments = ("-v -Pn -sT -sV --script=banner " +
                          "--top-ports 1000 --open -T4 --system-dns"
                          )
        nma.scan(self._host, arguments=nmap_arguments, sudo=isSudo, callback=self.callback_results)
        return nma

    def callback_results(self, hostname, scan_result):
        send_to_s3(self._host + "_tcpscan", scan_result)

