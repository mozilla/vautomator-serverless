import nmap


class PortScanner():
    results = {}

    def __init__(self, hostname, arguments="-v -Pn -sT -sV --script=banner --top-ports 1000 --open -T4 --system-dns"):
        self.host = hostname
        self.arguments = arguments
        self.privileged = False
    
    def scanTCP(self):
        nma = nmap.PortScannerAsync()
        nma.scan(self.host, arguments=self.arguments, 
                 sudo=self.privileged, 
                 callback=self.callback_results
                 )
        return nma

    def callback_results(self, hostname, scan_result):
        results = scan_result
        return results
