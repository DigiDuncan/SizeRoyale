import requests
from decimal import Decimal
from urllib.parse import quote

class SV:
    def __init__(self):
        pass

    @classmethod
    def parse(cls, s):
        return _parse("SV", s)


def _parse(t, s):
    if t not in ["SV", "WV", "TV", "Diff", "Rate", "LimitedRate"]:
        raise ValueError(f"Parsing type {t} not valid.")
    r = requests.get(f"https://nizebot.bew.by/unit/{t}/parse?s=" + quote(s))
    responsejson = r.json()
    if t in ["SV", "WV", "TV"]:
        return Decimal(responsejson[t])
    return responsejson[t]
