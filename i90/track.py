# i90/track.py

import logging
from datetime import datetime
from json import dumps

import boto3

from i90.config import config


class Tracker:
    """Event tracking/structured logging for the pike"""

    REDIRECT_CREATED = "REDIRECT_CREATED"
    REDIRECT_CREATION_FAILURE = "REDIRECT_CREATION_FAILURE"
    REDIRECT_SUCCESS = "REDIRECT_SUCCESS"
    REDIRECT_MISS = "REDIRECT_MISS"
    REDIRECT_DESTINATION_MISSING = "REDIRECT_DESTINATION_MISSING"
    REDIRECT_DESTINATION_INVALID = "REDIRECT_DESTINATION_INVALID"
    REDIRECT_TOKEN_MISSING = "REDIRECT_TOKEN_MISSING"
    CREATE_TOKEN_COLLISION = "CREATE_TOKEN_COLLISION"
    INVALID_BODY = "INVALID_BODY"

    def __init__(self, client=None, stream=None):
        # Never retry. Speed > Tracking
        self.client = client or boto3.client("firehose")
        self.stream = stream or config.tracking_stream

    def __send(self, event):
        """Given an event_type and event, see that it's tracked. This
        method cannot throw any exception by design. Futhermore, we do not perform
        any retries outside of what firehose does. It is more important the the
        redirect take place than we collect data about it."""
        try:
            event.update({"__raw": dumps(event)})
            self.client.put_record(
                DeliveryStreamName=self.stream, Record={"Data": dumps(event) + "\n"}
            )
        except Exception as e:
            logging.exception(f"Failed writing data to Firehose. (event: '{event}')")


    def record(self, event_type, **kwargs):
        """Record an event with the given type and kwargs"""
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "stage": config.stage,
            "redirects_table": config.redirects_table,
        }
        event.update(kwargs)
        self.__send(event)
        return self

    def record_redirect_created(self, **kwargs):
        """Record redirect creation in the canonical style"""
        return self.record(self.__class__.REDIRECT_CREATED, **kwargs)

    def record_redirect_create_failure(self, **kwargs):
        """Record redirect creation failure in the canonical style"""
        return self.record(self.__class__.REDIRECT_CREATION_FAILURE, **kwargs)

    def record_redirect_success(self, **kwargs):
        """Record redirect success in the canonical style"""
        return self.record(self.__class__.REDIRECT_SUCCESS, **kwargs)

    def record_miss(self, **kwargs):
        """Record redirect miss in the canonical style"""
        return self.record(self.__class__.REDIRECT_MISS, **kwargs)

    def record_token_missing(self, **kwargs):
        """Record when a token is missing in the canonical style"""
        return self.record(self.__class__.REDIRECT_TOKEN_MISSING, **kwargs)

    def record_destination_missing(self, **kwargs):
        """Record when a destination for a redirect is missing in the canonical style"""
        return self.record(self.__class__.REDIRECT_DESTINATION_MISSING, **kwargs)

    def record_invalid_destination(self, **kwargs):
        """Record when a destination is invalid in the canonical style"""
        return self.record(self.__class__.REDIRECT_DESTINATION_INVALID, **kwargs)

    def record_token_collision(self, **kwargs):
        """Record when we see a token collision in the canonical style"""
        return self.record(self.__class__.CREATE_TOKEN_COLLISION, **kwargs)

    def invalid_body(self, **kwargs):
        """Record when we receive an invalid body in the canonical style"""
        return self.record(self.__class__.INVALID_BODY, **kwargs)
