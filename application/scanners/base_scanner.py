from time import sleep
from random import uniform 


class BaseScanner:
    """Holds all commom properties for scanners."""

    def __init__(self, settings):
        self.settings = settings

    # Use time.sleep for waiting and uniform for randomizing
    def wait_between(self, a, b):
        rand=uniform(a, b)
        sleep(rand)

    @property
    def base_url(self):
        """Base URL for the scanned service."""
        raise NotImplementedError
    
    @property
    def headers(self):
        """Headers for the request."""
        raise NotImplementedError

    def login(self, user_info):
        """Auth flow to login into the service"""
        raise NotImplementedError

    def parse(html):
        """Parses the response from the service to an Python object."""
        raise NotImplementedError