import pytest
import os
import subprocess
import sys
from scanners.direnum_scanner import DirectoryEnumScanner
from lib.utilities import uppath


@pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
class TestDirectoryEnumScanner():

    def test_defaults(self):
        scanner = DirectoryEnumScanner()
        assert scanner.tool == 'dirb'
        assert scanner.arguments == ['-f', '-w', '-S', '-r']
        assert scanner.wordlist == 'short'

    @pytest.mark.xfail(raises=AssertionError)
    def test_invalid_wordlist(self):
        DirectoryEnumScanner(wordlist='invalid')

    # This will never succeed in Travis, because
    # it relies on dirb being installed/available
    # locally, therefore adding a condition
    @pytest.mark.skipif("TRAVIS" in os.environ
                        and os.environ["TRAVIS"] == "true",
                        reason="Skipping this test on Travis CI.")
    def test_scan_invalid(self):
        # This is needed for dirb binary to be added to the path
        original_pathvar = os.environ['PATH']
        os.environ['PATH'] = uppath(os.path.realpath(__file__), 2)  \
            + '/vendor/dirb/' + ':' \
            + original_pathvar

        host_name = "infosec.mozilla.org"
        # Wordlist does not matter here, but we want to give it
        # an invalid command line option (e.g '-b')
        scanner = DirectoryEnumScanner(arguments_list=['-b'])
        return_code, result = scanner.scan(host_name)
        assert not return_code == 0
        assert 'host' in result
        assert 'illegal' in result['errors']

    # Same as the above function
    @pytest.mark.skipif("TRAVIS" in os.environ
                        and os.environ["TRAVIS"] == "true",
                        reason="Skipping this test on Travis CI.")
    def test_scan_no_timeout(self):
        # This is needed for dirb binary to be added to the path
        original_pathvar = os.environ['PATH']
        os.environ['PATH'] = uppath(os.path.realpath(__file__), 2)  \
            + '/vendor/dirb/' + ':' \
            + original_pathvar

        host_name = "infosec.mozilla.org"
        # By default this will use the short wordlist
        scanner = DirectoryEnumScanner(wordlist='short')
        return_code, result = scanner.scan(host_name)
        assert return_code == 0
        assert 'host' in result
        assert 'output' in result
        assert len(result['errors']) == 0
        assert len(result['output']) > 0

        # Set PATH to original value
        os.environ['PATH'] = original_pathvar

    # Same as the above function
    @pytest.mark.skipif("TRAVIS" in os.environ
                        and os.environ["TRAVIS"] == "true",
                        reason="Skipping this test on Travis CI.")
    def test_scan_timeout(self):
        # This is needed for dirb binary to be added to the path
        original_pathvar = os.environ['PATH']
        os.environ['PATH'] = uppath(os.path.realpath(__file__), 2)  \
            + '/vendor/dirb/' + ':' \
            + original_pathvar

        host_name = "infosec.mozilla.org"
        # Give it a long wordlist to guarantee time out
        scanner = DirectoryEnumScanner(wordlist='long')
        return_code, result = scanner.scan(host_name)
        assert not return_code == 0
        assert 'host' in result
        assert 'output' in result
        assert 'TIMEDOUT' in result['errors']

        # Set PATH to original value
        os.environ['PATH'] = original_pathvar
