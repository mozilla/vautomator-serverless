import pytest
import os
from scanners.direnum_scanner import DirectoryEnumScanner


class TestDirectoryEnumScanner():

    def test_defaults(self):
        scanner = DirectoryEnumScanner()
        assert scanner.tool == 'dirb'
        assert scanner.arguments == '-f -w -S -r'
        assert scanner.wordlist == 'short'

    # This will never succeed in Travis, because
    # it relies on dirb being installed/available
    # locally, therefore adding a condition
    @pytest.mark.skipif("TRAVIS" in os.environ
                        and os.environ["TRAVIS"] == "true",
                        reason="Skipping this test on Travis CI.")
    def test_scan_no_timeout(self):
        # This is needed for nmap static library to be added to the path
        original_pathvar = os.environ['PATH']
        os.environ['PATH'] = os.path.dirname(os.path.realpath(__file__))  \
            + '/vendor/dirb/' + ':' \
            + original_pathvar
        host_name = "infosec.mozilla.org"
        # By default this will use the short wordlist
        scanner = DirectoryEnumScanner()
        return_code, result = scanner.scan(host_name)
        assert return_code == 0
        assert 'host' in result
        assert 'routes' in result
        assert len(result['routes']) > 0
        
        # Set PATH to original value
        os.environ['PATH'] = original_pathvar

    # Same as the above function
    @pytest.mark.skipif("TRAVIS" in os.environ
                        and os.environ["TRAVIS"] == "true",
                        reason="Skipping this test on Travis CI.")
    def test_scan_timeout(self):
        # This is needed for nmap static library to be added to the path
        original_pathvar = os.environ['PATH']
        os.environ['PATH'] = os.path.dirname(os.path.realpath(__file__))  \
            + '/vendor/dirb/' + ':' \
            + original_pathvar
        host_name = "infosec.mozilla.org"
        # Give it a long wordlist to guarantee time out
        scanner = DirectoryEnumScanner(wordlist='long')
        return_code, result = scanner.scan(host_name)
        assert not return_code == 0
        assert not result
