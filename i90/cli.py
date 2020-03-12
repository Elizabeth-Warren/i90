# i90/cli.py

import boto3
import requests


class Cli:
    """cli helpers for i90. This cli does not interact with with the database
    directly. Instead, it uses the api we expose. This is infinitely more useful
    when exercising deployed software"""

    SSM_API_KEY = "/shared/api-gateway/defaults/api-key"

    @staticmethod
    def denude_arguments(arguments):
        """Denude the docopt arguments object"""
        return {
            k.lstrip("-").lstrip("<").rstrip(">"): v for k, v in arguments.items() if v
        }

    def __init__(self, arguments):
        self.arguments = Cli.denude_arguments(arguments)
        self.endpoint = self.arguments["api-endpoint"].rstrip("/")
        self.api_key = (
            self.arguments["api-key"]
            if "api-key" in self.arguments
            else self.__default_api_key()
        )

    def __default_api_key(self):
        return boto3.client("ssm").get_parameter(
            Name=self.SSM_API_KEY, WithDecryption=True
        )["Parameter"]["Value"]

    def __make_request(self, method, path, **kwargs):
        return requests.request(
            method,
            f"{self.endpoint}/{path}",
            headers={"x-api-key": self.api_key},
            **kwargs,
        ).text

    def get(self):
        """Get a redirect based on our arguments"""
        token = self.arguments.get("token")
        if not token:
            raise Exception("No 'token' provided")

        return self.__make_request("GET", f"v1/redirect/{token}")

    def conceive(self):
        """Conceive of a redirect based on our arguments"""
        destination = self.arguments.get("destination")
        if not destination:
            raise Exception("No 'destination' provided")

        return self.__make_request(
            "POST",
            "v1/conceive",
            json={"destination": destination, "_app_name": "i90-tools"},
        )

    def claim(self):
        """Claim a redirect based on our arguments"""
        token = self.arguments.get("token")
        destination = self.arguments.get("destination")
        if not (token and destination):
            raise Exception("Both a 'token' and a 'destination' are required")

        return self.__make_request(
            "POST",
            "v1/claim",
            json={
                "destination": destination,
                "token": token,
                "_app_name": "i90-tools",
            },
        )

    def run(self):
        """Run the command defined in the passed arguments"""
        command = self.arguments["command"]
        if not hasattr(self, command):
            raise Exception(f"{command} is not a valid command")
        return getattr(self, command)()
