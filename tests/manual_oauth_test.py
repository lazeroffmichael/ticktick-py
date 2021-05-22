"""
Testing file for testing the OAuth module works. This is not included in the normal testing packages since it
requires user input to work.
"""
from ticktick.oauth2 import OAuth2
import os

if __name__ == '__main__':
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    redirect_uri = os.getenv('URI')
    auth_client = OAuth2(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    pass

