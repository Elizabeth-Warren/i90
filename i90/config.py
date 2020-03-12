# i90/config.py

from os import environ

from cached_property import cached_property


class Config:
    @cached_property
    def protocol(self):
        return environ["MY_PROTOCOL"]

    @cached_property
    def host(self):
        return environ["MY_HOST"]

    @cached_property
    def token_byte_length(self):
        return int(environ.get("TOKEN_BYTE_LENGTH", 16))

    @cached_property
    def stage(self):
        return environ["STAGE"]

    @cached_property
    def dynamo_configuration(self):
        endpoint = environ.get("DYNAMO_ENDPOINT")
        if endpoint:
            return {"endpoint_url": endpoint}
        return {}

    @cached_property
    def redirects_table(self):
        return environ["REDIRECTS_TABLE"]

    @cached_property
    def catchall_redirect(self):
        return environ.get("CATCHALL_REDIRECT", "https://elizabethwarren.com/")


    @cached_property
    def tracking_stream(self):
        return environ["TRACKING_STREAM"]


config = Config()
