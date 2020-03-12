# i90/test_responses.py


from json import loads

from i90.config import config
from i90.responses import responses

REDIRECT_EXAMPLE = """
    <html><body>Moved: <a href="https://example.com">https://example.com</a></body></html>
"""


def test_html_moved():
    assert REDIRECT_EXAMPLE.strip() == responses.html_moved("https://example.com")


def test_redirect_without_headers():
    response = responses.redirect("https://example.com")
    assert response["statusCode"] == 302
    assert response["body"] == REDIRECT_EXAMPLE.strip()
    assert response["headers"]["Location"] == "https://example.com"
    assert response["headers"]["Content-Type"] == "text/html"
    assert len(response["headers"]) == 2


def test_redirect_with_headers():
    response = responses.redirect(
        "https://example.com", headers={"X-EW-MSG": "Dream big, fight hard"}
    )
    assert response["statusCode"] == 302
    assert response["body"] == REDIRECT_EXAMPLE.strip()
    assert response["headers"]["Location"] == "https://example.com"
    assert response["headers"]["Content-Type"] == "text/html"
    assert response["headers"]["X-EW-MSG"] == "Dream big, fight hard"
    assert len(response["headers"]) == 3


def test_not_found():
    response = responses.not_found()
    assert response["statusCode"] == 302
    assert response["headers"]["Location"] == config.catchall_redirect


def test_user_error():
    response = responses.user_error()
    response["statusCode"] == 400
    response["headers"]["Content-Type"] == "application/json"
    # just making sure this is json
    loads(response["body"])


def test_already_claimed():
    response = responses.already_claimed()
    response["statusCode"] == 400
    response["headers"]["Content-Type"] == "application/json"
    # just making sure this is json
    loads(response["body"])


def test_server_error():
    response = responses.server_error()
    response["statusCode"] == 500
    response["headers"]["Content-Type"] == "application/json"
    # just making sure this is json
    loads(response["body"])


def test_redirect_created():
    response = responses.redirect_created({"hello": "world", "token": "world"})
    response["statusCode"] == 200
    response["headers"]["Content-Type"] == "application/json"
    body = loads(response["body"])
    assert body["hello"] == "world"
    assert body["short_url"] == "http://localhost/x/world"
