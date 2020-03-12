# i90/api.py

import logging

from i90.redirects import Redirects
from i90.responses import responses
from i90.track import Tracker


class Api:
    """Container for api responses"""

    def __init__(self, redirects=None, tracker=None):
        self.redirects = redirects or Redirects()
        self.tracker = tracker or Tracker()

    def validate_body(self, body):
        """Given a request body, determine whether or not we can handle it"""
        for _, v in body.items():
            if isinstance(v, dict) or isinstance(v, list):
                return False
            return True

    def get(self, token):
        """Given a token, look it up in the redirects database and return
        a lambda compatible json responses"""
        try:
            return responses.redirect_json(self.redirects.get(token))
        except self.redirects.RedirectDoesNotExist:
            return responses.redirect_json_not_found()

    def redirect(self, token, **kwargs):
        """Given a token and arbitrary jsonifiable kwargs, return a lambda proxy
        compatible response for a redirect"""
        if not token:
            self.tracker.record_token_missing(**kwargs)
            return responses.not_found()  # Early Return

        try:
            data = self.redirects.get(token)
        except self.redirects.RedirectDoesNotExist:
            logging.warn(f"Failed to find redirect for '{token}'")
            self.tracker.record_miss(token=token, **kwargs)
            return responses.not_found()  # Early Return

        destination = data.get("destination")
        if not destination:
            self.tracker.record_destination_missing(token=token, **kwargs)
            return responses.not_found()  # Early Return

        self.tracker.record_redirect_success(
            token=token, destination=destination, redirect=data, **kwargs
        )
        return responses.redirect(destination)

    def claim(self, token, destination, **kwargs):
        """Given a token, destination, and arbitrary jsonifiable kwargs, return
        a lambda-proxy compatible response"""
        if not (token and destination):
            logging.warn(
                f"Either token or destination was None. (token: '{token}'; destination: '{destination}'; kwargs: '{kwargs}')"
            )
            return responses.user_error()  # Early Return

        if not self.validate_body(kwargs):
            self.tracker.invalid_body(token=token, destination=destination, **kwargs)
            return responses.user_error()  # Early Return

        # Be careful with the order here
        try:
            result = self.redirects.add(token, destination, **kwargs)

        except self.redirects.RedirectAlreadyExists:
            logging.error(f"The redirect for '{token}' already exists")
            self.tracker.record_token_collision(
                token=token, destination=destination, **kwargs
            )
            return responses.already_claimed()  # Early Return

        except self.redirects.InvalidRedirectDestination:
            logging.error(
                f"Claiming redirect for '{token}' failed because '{destination}' was an invalid desintation."
            )
            self.tracker.record_invalid_destination(
                token=token, destination=destination, **kwargs
            )
            return responses.invalid_destination()  # Early Return

        # ^^^^^
        # Allow other exceptions to bubble up so that they are captured by the
        # top-level error handler and delivered to mission control

        self.tracker.record_redirect_created(**result)
        return responses.redirect_created(result)

    def conceive(self, destination, **kwargs):
        """Given a destination and arbitrary jsonifiable kwargs, return a lambda-proxy
        compatible response"""
        if not destination:
            logging.warn(
                f"Request to conceive of redirect because destination was falsey. (kwargs: '{kwargs}')"
            )
            return responses.user_error()  # Early Return

        if not self.validate_body(kwargs):
            self.tracker.invalid_body(destination=destination, **kwargs)
            return responses.user_error()  # Early Return

        try:
            result = self.redirects.conceive(destination, **kwargs)

        except self.redirects.InvalidRedirectDestination:
            logging.error(
                f"Failed to conceive of redirect to '{destination}' because it is invalid."
            )
            self.tracker.record_invalid_destination(destination=destination, **kwargs)
            return responses.invalid_destination()  # Early Return

        # ^^^^^
        # Allow other exceptions to bubble up so that they are captured by the
        # top-level error handler and delivered to mission control

        self.tracker.record_redirect_created(**result)
        return responses.redirect_created(result)
