# i90/test_tracker.py

from json import loads

from i90.config import config
from i90.test_helpers import *
from i90.track import Tracker


def test_record():
    firehose = FakeFirehose()
    tracker = Tracker(client=firehose)
    tracker.record("test", other="arg")

    recorded = loads(firehose.records[-1]["Data"])
    assert recorded["other"] == "arg"
    assert recorded["event_type"] == "test"
    assert recorded["stage"] == config.stage
    assert recorded["redirects_table"] == config.redirects_table
