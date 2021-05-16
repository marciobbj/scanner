from application.exceptions import LoginNotCompleted
from functools import wraps
import logging
import time


def check_auth_and_wait_load_delay(func):
    """Checks whether the user is logged in pr not and sets a 15sec delay.

    It can be implemented in any scanner if the scanner implements the logic
    of the flag :self.logged_in:"""
    @wraps(func)
    def inner(self, *args, **kwargs):
        if not self.logged_in:
            logging.error("%s cannot scan page of logged off user", self.baselog)
            raise LoginNotCompleted()
        time.sleep(15)
        return func(self, *args, **kwargs)
    return inner