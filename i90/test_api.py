# i90/test_api.py

from json import loads

from i90.api import Api
from i90.config import config
from i90.redirects import Redirects
from i90.test_helpers import *
from i90.track import Tracker


def get_api():
    return Api(redirects=Redirects(), tracker=Tracker(FakeFirehose()))


def test_validate_body():
    api = get_api()
    assert api.validate_body({"hello": "world"})
    assert not api.validate_body({"hello": {"world": "it-me"}})
    assert not api.validate_body({"hello": ["world"]})


def test_redirect(redirects_table):
    api = get_api()

    response = api.redirect("hello")
    assert response["statusCode"] == 302
    assert response["headers"]["Location"] == config.catchall_redirect

    api.redirects.add("hello", "https://example.com")
    response = api.redirect("hello")
    assert response["statusCode"] == 302
    assert response["headers"]["Location"] == "https://example.com"


def test_claim(redirects_table):
    api = get_api()

    response = api.claim("hello", "https://example.com", hello="world")

    assert response["statusCode"] == 200

    data = loads(response["body"])
    token = data["token"]

    assert data["short_url"] == f"http://localhost/x/{token}"
    assert data["dimensions_domain"] == "example.com"
    assert data["hello"] == "world"

    response = api.claim("hello", "https://example.com/but-different")
    assert response["statusCode"] == 400

    response = api.claim(
        "more-different", "https://example.com", too={"complex": "am i"}
    )
    assert response["statusCode"] == 400


def test_claim_errors_with_nones(redirects_table):
    api = get_api()

    response = api.claim("hello", None)
    assert response["statusCode"] == 400

    response = api.claim(None, "hello")
    assert response["statusCode"] == 400


def test_conceive(redirects_table):
    api = get_api()

    response = api.conceive("https://example.com", hello="world")
    assert response["statusCode"] == 200

    data = loads(response["body"])

    assert data["dimensions_domain"] == "example.com"
    assert data["hello"] == "world"

    token = data["token"]

    assert data["short_url"] == f"http://localhost/x/{token}"

    response = api.conceive("not a url")
    assert response["statusCode"] == 400

    response = api.conceive("https://example.com", too={"complex": "am i"})
    assert response["statusCode"] == 400
