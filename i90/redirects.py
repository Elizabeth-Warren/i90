# i90/redirects.py

import logging
import secrets
from datetime import datetime

import boto3

from i90.config import config
from i90.urls import urls


class Redirects:
    """Data store for the redirects"""

    class RedirectAlreadyExists(Exception):
        """Raised when the redirect already exists in the redirects table. Used
        on calls when we attempt to add a redirect that we shouldn't."""

        pass

    class RedirectDoesNotExist(Exception):
        """Raised when the redirect does not exist in the table. Used on calls
        to 'get' a redirect"""

        pass

    class InvalidRedirectDestination(Exception):
        """Raised when the redirect destination is not a valid url. Used on calls
        to 'add' a redirect"""

        pass

    def __init__(self, table=None, firehose=None):
        self.table = table or boto3.resource(
            "dynamodb", **config.dynamo_configuration
        ).Table(config.redirects_table)

    def get(self, token):
        """Given a token, return the redirect record"""
        try:
            result = self.table.get_item(Key={"token": token})
            return result["Item"]
        except Exception as e:
            raise self.RedirectDoesNotExist(f"token: {token}; exception: {str(e)}")

    def add(self, token, destination, overwrite=False, **kwargs):
        """Given a token and a destination, stash it"""
        if not overwrite:
            try:
                record = self.get(token)
            except self.RedirectDoesNotExist:
                # There is no redirect associated with this token so we're not
                # attempting and overwrite
                pass
            else:
                # There _is_ a redirect associated with this token so we raise
                # the "RedirectAlreadyExists" exception here
                destination = record.get("destination")
                raise self.RedirectAlreadyExists(
                    f"'{token}' is already associated with '{destination}'"
                )

        if not urls.is_valid(destination):
            raise self.InvalidRedirectDestination(f"{destination} is not a valid url")

        record = kwargs

        dimensions = urls.extract_dimensions(destination)
        record.update({f"dimensions_{k}": v for k, v in dimensions.items()})

        record.update(
            {
                "token": token,
                "destination": destination,
                "updated_at": datetime.utcnow().isoformat(),
            }
        )

        self.table.put_item(Item=record)
        return record

    def __find_unused_token(self, attempts=10):
        """Generate an unused token"""
        for _ in range(attempts):
            token = secrets.token_urlsafe(config.token_byte_length)

            try:
                self.get(token)
            except self.RedirectDoesNotExist:
                # This means that we do not already have the token associated
                # with a destination so we're free to use it
                return token  # Early Return

        raise Exception(f"Failed to find an unused token after {attempts} attempts...")

    def conceive(self, destination, **kwargs):
        """Given a destination, create a new token, stash the redirect and return the
        the record"""
        token = self.__find_unused_token()
        return self.add(token, destination, **kwargs)
