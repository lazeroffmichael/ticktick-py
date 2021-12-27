"""
Helper module for generating a new .token-oauth file
"""
from ticktick.oauth2 import OAuth2        # OAuth2 Manager
from ticktick.api import TickTickClient   # Main Interface
from dotenv import dotenv_values


if __name__ == "__main__":
    
    config = dotenv_values(".env")

    auth_client = OAuth2(client_id=config["CLIENT_ID"],
                         client_secret=config["CLIENT_SECRET"],
                         redirect_uri=config["URI"])

    client = TickTickClient(config["TICKTICK_USER"], config["TICKTICK_PASS"], auth_client)
