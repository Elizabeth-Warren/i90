# i90/responses.py

from json import dumps
from urllib.parse import urljoin

from i90.config import config


class responses:
    """A container we use to generate responses to lambda proxy requests"""

    CONTENT_TYPE_HTML = "text/html"
    CONTENT_TYPE_JSON = "application/json"

    CONTENT_TYPE_HEADER = "Content-Type"
    LOCATION_HEADER = "Location"

    # We prefer 302s to 301s because we'll make a mistake someday
    # and 301s live in the browser damn near forever.
    REDIRECT_STATUS_CODE = 302
    SUCCESS_STATUS_CODE = 200
    USER_ERROR_STATUS_CODE = 400
    SERVER_ERROR_STATUS_CODE = 500
    NOT_FOUND_STATUS_CODE = 404

    @staticmethod
    def html_moved(destination_url):
        """Given a destination url, return HTML that tells us its moved."""
        return f"""
            <html><body>Moved: <a href="{destination_url}">{destination_url}</a></body></html>
        """.strip()

    @staticmethod
    def redirect(destination_url, headers=None):
        """Given a destination URL and an optional headers dictionary, return an
        appropriate redirect."""
        if not headers:
            headers = {}

        headers.update(
            {
                responses.LOCATION_HEADER: destination_url,
                responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_HTML,
            }
        )

        return {
            "statusCode": responses.REDIRECT_STATUS_CODE,
            "body": responses.html_moved(destination_url),
            "headers": headers,
        }

    @staticmethod
    def not_found():
        """Return the appropriate 'not found' response. Rather than return 404s,
        we redirect to the configured catchall URL"""
        return responses.redirect(config.catchall_redirect)

    @staticmethod
    def user_error():
        """Returns a user error response"""
        return {
            "statusCode": responses.USER_ERROR_STATUS_CODE,
            "body": dumps({"error": "invalid arguments"}),
            "headers": {responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_JSON},
        }

    @staticmethod
    def already_claimed():
        return {
            "statusCode": responses.USER_ERROR_STATUS_CODE,
            "body": dumps({"error": "redirect already claimed"}),
            "headers": {responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_JSON},
        }

    @staticmethod
    def invalid_destination():
        return {
            "statusCode": responses.USER_ERROR_STATUS_CODE,
            "body": dumps({"error": "redirect destination invalid"}),
            "headers": {responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_JSON},
        }

    @staticmethod
    def server_error():
        return {
            "statusCode": responses.SERVER_ERROR_STATUS_CODE,
            "body": dumps({"error": "server failure"}),
            "headers": {responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_JSON},
        }

    @staticmethod
    def redirect_created(result):
        # We let this blow up on a key error because it should never happen.
        token = result["token"]
        short_url = urljoin(f"{config.protocol}://{config.host}", f"x/{token}")

        result.update({"short_url": short_url})

        return {
            "statusCode": responses.SUCCESS_STATUS_CODE,
            "body": dumps(result),
            "headers": {responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_JSON},
        }

    @staticmethod
    def redirect_json(result):
        return {
            "statusCode": responses.SUCCESS_STATUS_CODE,
            "body": dumps(result),
            "headers": {responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_JSON},
        }

    @staticmethod
    def redirect_json_not_found():
        return {
            "statusCode": responses.NOT_FOUND_STATUS_CODE,
            "body": dumps({"error": "redirect not found"}),
            "headers": {responses.CONTENT_TYPE_HEADER: responses.CONTENT_TYPE_JSON},
        }
