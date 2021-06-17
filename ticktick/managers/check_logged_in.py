from functools import wraps


def logged_in(func):
    """
    Serves as a decorator making sure that the instance is still logged in for a function call.
    """

    @wraps(func)
    def call(self, *args, **kwargs):
        if not self.oauth_access_token:
            raise RuntimeError('ERROR -> Not Logged In')
        return func(self, *args, **kwargs)

    return call
