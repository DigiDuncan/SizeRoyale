import requests
from decimal import Decimal
from urllib.parse import quote


class UnitWrapper:
    def __init__(self, unit):
        self._unit = unit

    def parse(self, s):
        t = self._unit
        if t not in ["SV", "WV", "TV", "Diff", "Rate", "LimitedRate"]:
            raise ValueError(f"Parsing type {t} not valid.")
        r = requests.get(f"https://nizebot.bew.by/unit/{t}/parse?s=" + quote(s))
        responsejson = r.json()
        if t in ["SV", "WV", "TV"]:
            return Decimal(responsejson[t])
        return responsejson[t]


SV = UnitWrapper("SV")
WV = UnitWrapper("WV")
TV = UnitWrapper("TV")
