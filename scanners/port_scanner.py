import nmap
from lib.s3_helper import send_to_s3


class PortScanner():

    def __init__(self, hostname, arguments="-v -Pn -sT -sV --script=banner --top-ports 1000 --open -T4 --system-dns"):
        self.host = hostname
        self.arguments = arguments
        self.privileged = False
    
    def scanTCP(self, callback_function=None):
        nma = nmap.PortScannerAsync()
        if not callback_function:
            nma.scan(self.host, arguments=self.arguments, 
                     sudo=self.privileged, 
                     callback=self.callback_results
                     )
        else:
            nma.scan(self.host, arguments=self.arguments, 
                     sudo=self.privileged, 
                     callback=callback_function
                     )
        return nma

    def callback_results(self, hostname, scan_result):
        send_to_s3(self.host + "_tcpscan", scan_result)


