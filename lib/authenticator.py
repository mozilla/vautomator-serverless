class Authenticator(object):
    """Used to provide a simple token-based authentication layer."""

    def __init__(self, authorized_tokens=[]):
        self.authorized_tokens = authorized_tokens

    def valid_token(self, token):
        return token in self.authorized_tokens
