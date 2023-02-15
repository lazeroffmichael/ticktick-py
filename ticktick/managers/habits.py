class HabitManager:
    HABITS_BASE_URL = 'https://api.ticktick.com/api/v2/habits'

    def __init__(self, client_class):
        self._client = client_class
        self.access_token = ''

    #   ---------------------------------------------------------------------------------------------------------------
    #   Habit Methods
    def create(self):
        pass

    def update(self):
        pass

    def get_all(self):
        """
        Gets all current habit-information for the user.

        client.state['habits'] should have this information stored after login,
        only use this method to obtain habits if the client state is out of sync!

        Returns:
            httpx: The response from the get request.
        """
        return self._client.http_get(url=self.HABITS_BASE_URL, cookies=self._client.cookies, headers=self._client.HEADERS)
