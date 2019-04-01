import nmap
import pytest
import os
from scanners.port_scanner import PortScanner


class TestPortScanner():
    def test_defaults(self):
        host_name = "ssh.mozilla.com"
        scanner = PortScanner(host_name)
        assert not scanner.privileged
        assert scanner.arguments == ("-v -Pn -sT -sV --script=banner "
                                     "--top-ports 1000 --open -T4 --system-dns")

    def test_scan(self):
        # This is needed for nmap static library to be added to the path
        original_pathvar = os.environ['PATH']
        os.environ['PATH'] = original_pathvar \
            + ':' + os.path.dirname(os.path.realpath(__file__))  \
            + '/vendor/nmap-standalone/'
        host_name = "ssh.mozilla.com"
        scanner = PortScanner(host_name)
        nmap_scanner = scanner.scanTCP()
        while nmap_scanner.still_scanning():
            # Wait for 1 second after the end of the scan
            nmap_scanner.wait(1)
        scan_result = PortScanner.results
        print(PortScanner.results)

        # Check to see is some of the expected JSON elements
        # are in the scan result to ensure it's working
        assert 'scanstats' in scan_result['nmap']
        assert 'command_line' in scan_result['nmap']
        assert 'elapsed' in scan_result['nmap'] and \
            scan_result['nmap']['elapsed'] > 0.0

        # Set PATH to original value
        os.environ['PATH'] = original_pathvar
