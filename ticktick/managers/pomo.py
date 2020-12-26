class PomoManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def start(self):
        pass
