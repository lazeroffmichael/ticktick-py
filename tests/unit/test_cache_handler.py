"""
Tests the cache.py module
"""

import json
import os
from ticktick.cache import CacheHandler


class TestInitMethod:

    def test_set_custom_path(self):
        """
        Tests setting a custom path occurs properly
        """
        custom_path = 'new path here'
        cache = CacheHandler('new path here')
        assert cache.path == custom_path


class TestWriteToken:

    def test_write_token_to_cache_success(self):
        """
        Tests writing the token dictionary to cache works properly
        """
        path = '.token-write-test'
        token_info = {"access_token": 48573490857892}
        cache = CacheHandler(path)
        cache.write_token_to_cache(token_info)

        # check to see if we can open the file in the directory
        f = open(path)
        read_from_file = f.read()
        f.close()
        token_dict = json.loads(read_from_file)
        assert token_dict == token_info

        # delete the file
        os.remove(path)


class TestGetToken:

    def test_get_cached_token(self):
        """
        Tests retrieving a cached token
        """
        path = '.token-read-test'
        token_info = {"access_token": 45983495345}
        cache = CacheHandler(path)

        # create a new file in the directory
        cache.write_token_to_cache(token_info)

        # get the token
        returned_token = cache.get_cached_token()

        assert token_info == returned_token

        os.remove(path)

    def test_get_cached_token_fail(self):
        """
        Tests it the path doesn't exist the function returns none
        """
        path = '.not-real'
        cache = CacheHandler(path)

        assert cache.get_cached_token() is None
