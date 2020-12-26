class SettingsManager:

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = self._client.access_token

    def get_templates(self):
        # https://api.ticktick.com/api/v2/templates
        pass
