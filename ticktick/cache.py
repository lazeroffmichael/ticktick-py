import json
import errno
import logging

log = logging.getLogger(__name__)


class CacheHandler:
    """
    Handles the caching for TickTick auth tokens to disk
    """

    def __init__(self,
                 path):
        """
        Initializes the path of the cache
        :param path:
        """
        # set path
        self.path = path

    def get_cached_token(self):
        """
        Retrieves the cached token - and raises an exception if it doesn't work
        :return:
        """
        access_token_info = None
        try:
            f = open(self.path)
            access_token_info_full_string = f.read()
            f.close()
            access_token_info = json.loads(access_token_info_full_string)

        except IOError as error_occurred:
            if error_occurred == errno.ENOENT:
                log.debug(f"No cache exists at: {self.path}")
            else:
                log.warning(f"Cache could not be read at: {self.path}")

        return access_token_info

    def write_token_to_cache(self, access_token_info):
        """
        Writes the token to cache
        :return:
        """
        try:
            f = open(self.path, "w")
            f.write(json.dumps(access_token_info))
            f.close()

        except IOError:
            log.warning(f"Cache could not be written to at: {self.path}")
