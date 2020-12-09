import httpx


class TickTick_Client:
    BASE_URL = 'https://api.ticktick.com/api/v2/'

    def __init__(self, username: str, password: str):
        """
        Initializes a client session by loggin into TickTick
        :param username: TickTick Username
        :param password: TickTick Password
        """
        self.access_token = ''
        self.cookies = {}
        self.login(username, password)

    def login(self, username: str, password: str):
        """
        Logs into TickTick using passed username and password
        :param username: TickTick Username
        :param password: TickTick Password
        :return:
        """
        url = self.BASE_URL + 'user/signon'
        user_info = {
            'username': username,
            'password': password
        }
        parameters = {
            'wc': True,
            'remember': True
        }
        # Make an HTTP POST request
        response = httpx.post(url, json=user_info, params=parameters)

        # Raise error for any status code other than 200 (OK)
        if response.status_code != 200:
            raise ValueError('Could Not Log In - Invalid Username or Password')

        response_information = response.json()
        self.access_token = response_information['token']
        self.cookies['t'] = self.access_token


if __name__ == '__main__':
