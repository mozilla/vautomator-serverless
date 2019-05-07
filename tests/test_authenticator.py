import random
from lib.authenticator import Authenticator


class TestAuthenticator():
    def test_with_no_tokens(self):
        invalid_token = "foobar"
        authenticator = Authenticator()
        assert authenticator.valid_token(invalid_token) is False

    def test_with_valid_tokens(self):
        valid_token = "barbaz"
        valid_tokens = [valid_token]
        invalid_token = "foobar"

        authenticator = Authenticator(valid_tokens)
        assert authenticator.valid_token(invalid_token) is False
        assert authenticator.valid_token(valid_token) is True
