# i90/urls.py

from urllib.parse import parse_qs, urlparse

import validators


class urls:
    @staticmethod
    def is_valid(url):
        return validators.url(url)

    @staticmethod
    def extract_dimensions(url):
        parsed = urlparse(url)
        params = {}

        for k, vs in parse_qs(parsed.query).items():
            if len(vs) == 1:
                params[f"query_{k}"] = vs[0]
            else:
                for i, v in enumerate(sorted(vs)):
                    params[f"query_{k}_{i}"] = v

        dimensions = {
            "scheme": parsed.scheme,
            "domain": parsed.hostname,
            "path": parsed.path.lstrip("/"),
            "query": parsed.query,
        }
        dimensions.update(params)
        dimensions = {k: v for k, v in dimensions.items() if v}
        return dimensions
