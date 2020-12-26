def logged_in(func):
    """
    Serves as a decorator making sure that the instance is still logged in for a function call.
    """

    def call(self, *args, **kwargs):
        if not self.access_token:
            raise RuntimeError('ERROR -> Not Logged In')
        return func(self, *args, **kwargs)

    return call