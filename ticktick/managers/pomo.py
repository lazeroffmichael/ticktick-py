class PomoManager:

    def __init__(self, client_class):
        self._client = client_class
        self._access_token = self._client._access_token

    def start(self):
        pass

    def statistics(self):
        # https://api.ticktick.com/api/v2/statistics/general
        pass
