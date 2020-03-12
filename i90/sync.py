# i90/sync.py

from json import loads

import pygsheets
from google.oauth2.credentials import Credentials

from i90.config import config
from i90.redirects import add_redirect


class sync:
    def __init__(self):
        pass

    def __client(self):
        return pygsheets.client.Client(
            Credentials.from_authorized_user_info(loads(config.google_credentials))
        )

    def __sheet(self):
        return self.__client().open_by_key(config.google_sheet)

    def __worksheet(self):
        return self.__sheet().worksheet_by_title(config.google_worksheet)

    def __values(self):
        return self.__worksheet().get_all_records()

    def __call__(self):
        for value in self.__values():
            token = value.get("token")
            destination = value.get("destination")
            if token and destination:
                add_redirect(token, destination, overwrite=True)
