class SettingsManager:

    def __init__(self, client_class):
        self._client = client_class
        self._access_token = self._client._access_token

    def get_templates(self):
        # https://api.ticktick.com/api/v2/templates
        pass

    def get_user_settings(self):
        # https://api.ticktick.com/api/v2/user/preferences/settings?includeWeb=true
        pass
