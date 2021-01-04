class FocusTimeManager:

    def __init__(self, client_class):
        self._client = client_class
        self._access_token = self._client._access_token

    #   ---------------------------------------------------------------------------------------------------------------
    #   Focus Timer Methods

    def start(self):
        """Starts the focus timer"""
        pass



