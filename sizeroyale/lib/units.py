import requests
from decimal import Decimal
from urllib.parse import quote
from sizeroyale.lib.errors import ParseError


class UnitWrapper:
    def __init__(self, unit):
        self._unit = unit

    def parse(self, s):
        t = self._unit
        if not isinstance(s, str):
            raise ParseError(f"{s!r} is not a String.")
        if t not in ["SV", "WV", "TV", "Diff", "Rate", "LimitedRate"]:
            raise ValueError(f"Parsing type {t} not valid.")
        if s is None:
            raise ParseError(f"{s} is not a valid unit string.")
        r = requests.get(f"https://nizebot.bew.by/unit/{t}/parse?s=" + quote(s))
        responsejson = r.json()
        if t in ["SV", "WV", "TV"]:
            return Decimal(responsejson[t])
        return responsejson[t]


SV = UnitWrapper("SV")
WV = UnitWrapper("WV")
TV = UnitWrapper("TV")
Diff = UnitWrapper("Diff")
