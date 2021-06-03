"""
Integration tests for oauth2.py
"""
import os

from ticktick.oauth2 import OAuth2


def test_oauth2_from_environment():
    """
    Tests successful validation of access token from environment
    """
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    redirect_uri = os.getenv('URI')

    auth_client = OAuth2(client_id=client_id,
                         client_secret=client_secret,
                         redirect_uri=redirect_uri,
                         env_key="ACCESS_TOKEN_DICT")

    assert auth_client.access_token_info["access_token"] == os.getenv('ACCESS_TOKEN')