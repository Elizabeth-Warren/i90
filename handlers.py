# handlers.py

import logging
from json import loads

from i90.api import Api
from i90.responses import responses

api = Api()


def get_redirect(event, *args, **kwargs):
    if event.get("source") == "aws.events":
        return

    params = event.get("pathParameters", {})
    token = params.get("token", "").strip()
    return api.get(token)


def redirect(event, *args, **kwargs):
    if event.get("source") == "aws.events":
        return

    params = event.get("pathParameters", {})
    token = params.get("token", "").strip()
    return api.redirect(token, event=event)


def claim(event, *args, **kwargs):
    if event.get("source") == "aws.events":
        return

    body = loads(event.get("body", "{}"))

    if not len(body):
        return responses.user_error()

    token = body.pop("token", None)
    destination = body.pop("destination", None)

    return api.claim(token, destination, **body)


def conceive(event, *args, **kwargs):
    if event.get("source") == "aws.events":
        return

    body = loads(event.get("body", "{}"))
    destination = body.pop("destination", None)

    return api.conceive(destination, **body)
