# i90/test_urls.py

from i90.urls import urls


def test_extract_dimensions():
    dimensions = urls.extract_dimensions("https://example.com")
    assert dimensions["scheme"] == "https"
    assert dimensions["domain"] == "example.com"

    dimensions = urls.extract_dimensions("https://example.com/path?hello=world")

    assert dimensions["scheme"] == "https"
    assert dimensions["domain"] == "example.com"
    assert dimensions["path"] == "path"
    assert dimensions["query_hello"] == "world"

    dimensions = urls.extract_dimensions(
        "https://secure.actblue.com/donate/ew-feb20fr-march3?email=pstein@elizabethwarren.com&refcode=EMO21F_EGL_GRM_W_20200205_V1S3_P"
    )

    assert dimensions["scheme"] == "https"
    assert dimensions["domain"] == "secure.actblue.com"
    assert dimensions["path"] == "donate/ew-feb20fr-march3"
    assert dimensions["query_email"] == "pstein@elizabethwarren.com"
    assert dimensions["query_refcode"] == "EMO21F_EGL_GRM_W_20200205_V1S3_P"

    dimensions = urls.extract_dimensions(
        "https://prod-supportal-api.elizabethwarren.codes/v1/shifter/recommended_events?strategy=shifter_engine&event_types=CANVASS&states=NH&tag_ids=34%2C35&zip5=02145&limit=20"
    )

    assert dimensions["query_strategy"] == "shifter_engine"
    assert dimensions["query_event_types"] == "CANVASS"
    assert dimensions["query_states"] == "NH"
    assert dimensions["query_tag_ids"] == "34,35"
    assert dimensions["query_zip5"] == "02145"
    assert dimensions["query_limit"] == "20"

    dimensions = urls.extract_dimensions(
        "https://prod-supportal-api.elizabethwarren.codes/v1/shifter/recommended_events?strategy=shifter_engine&event_types=CANVASS&states=NH&tag_ids=34%2C35&zip5=02145&zip5=12345&limit=20"
    )
    assert dimensions["query_zip5_0"] == "02145"
    assert dimensions["query_zip5_1"] == "12345"
