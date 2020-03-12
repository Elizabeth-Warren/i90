# i90/test_redirects.py

import pytest

from i90.config import config
from i90.redirects import Redirects
from i90.test_helpers import *


def extract_item(response):
    return response.get("Item")


def get_by_hash_key(redirects_table, hash_key):
    return extract_item(redirects_table.get_item(Key={"token": hash_key}))


def test_simple_add(redirects_table):
    redirects = Redirects()

    token = "my-token"
    destination = "https://example.com"

    redirect = redirects.add(token, destination)

    assert redirect["token"] == token
    assert redirect["destination"] == destination

    item = get_by_hash_key(redirects_table, token)
    assert redirect["token"] == item["token"]
    assert redirect["destination"] == item["destination"]


def test_complex_add(redirects_table):
    redirects = Redirects()

    token = "my-token"
    destination = "https://example.com"
    payload = {"a": "hello", "b": "world"}

    redirect = redirects.add(token, destination, **payload)

    assert redirect["token"] == token
    assert redirect["destination"] == destination
    assert redirect["a"] == "hello"
    assert redirect["b"] == "world"

    item = get_by_hash_key(redirects_table, token)

    assert redirect["token"] == item["token"]
    assert redirect["destination"] == item["destination"]
    assert redirect["a"] == item["a"]
    assert redirect["b"] == item["b"]


def test_when_adding_a_bunch(redirects_table):
    redirects = Redirects()

    token_prefix = "token"
    destination_prefix = "https://example.com/"

    for index in range(10):
        redirects.add(
            f"{token_prefix}-{index}", f"{destination_prefix}#{index}", index=index
        )

    for index in range(10):
        item = get_by_hash_key(redirects_table, f"{token_prefix}-{index}")
        print(item)
        assert item["index"] == index


def test_overwrite_flag(redirects_table):
    redirects = Redirects()

    redirects.add("test", "https://example.com")

    with pytest.raises(redirects.RedirectAlreadyExists):
        redirects.add("test", "https://example.com/something-else")

    assert redirects.get("test")["destination"] == "https://example.com"

    redirects.add("test", "https://example.com/overwritten", overwrite=True)
    assert redirects.get("test")["destination"] == "https://example.com/overwritten"


def test_simple_get(redirects_table):
    redirects = Redirects()

    token = "another-token"
    destination = "https://example.com/#another-token"

    redirects.add(token, destination)
    redirect = redirects.get(token)

    assert redirect["destination"] == destination
    assert (
        get_by_hash_key(redirects_table, token)["destination"]
        == redirect["destination"]
    )


def test_get_failure(redirects_table):
    redirects = Redirects()

    with pytest.raises(redirects.RedirectDoesNotExist):
        redirects.get("literally-anything")


def test_simple_conception(redirects_table):
    redirects = Redirects()

    redirect = redirects.conceive("https://example.com")
    token = redirect["token"]

    record = get_by_hash_key(redirects_table, token)
    assert record["destination"] == "https://example.com"


def test_complex_conception(redirects_table):
    redirects = Redirects()

    redirect = redirects.conceive("https://example.com", sentinel="test")
    token = redirect["token"]

    record = get_by_hash_key(redirects_table, token)
    assert record["destination"] == "https://example.com"
    assert record["sentinel"] == "test"


def test_multiple_conceptions(redirects_table):
    redirects = Redirects()

    count = 10
    destination = "https://example.com"

    for index in range(count):
        redirects.conceive(destination)

    response = redirects_table.scan(Select="ALL_ATTRIBUTES")
    assert response["Count"] == count

    for item in response["Items"]:
        assert item["destination"] == destination

    assert len(set(item["token"] for item in response["Items"])) == count
