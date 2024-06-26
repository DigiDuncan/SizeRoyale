from typing import Union
import logging
import requests
from decimal import Decimal
import urllib3
from urllib.parse import quote

from requests.models import HTTPError

from sizeroyale.lib.attrdict import AttrDict
from sizeroyale.lib.errors import ParseError

logger = logging.getLogger("sizeroyale")
urllib3.disable_warnings()

class UnitWrapper:
    def __init__(self, unit):
        self._unit = unit

    def parse(self, s: str) -> Union[Decimal, AttrDict, dict]:
        t = self._unit
        if not isinstance(s, str):
            raise ParseError(f"{s!r} is not a String.")
        if t not in ["SV", "WV", "TV", "Diff", "Rate", "LimitedRate"]:
            raise ValueError(f"Parsing type {t} not valid.")
        if s is None:
            raise ParseError(f"{s} is not a valid unit string.")
        try:
            r = requests.get(f"http://sizebot.digiduncan.com/unit/{t}/parse?s=" + quote(s), verify=False)
        except requests.exceptions.SSLError as e:
            logger.error("SSL Error: The SSL certificate has expired for Sizebot API.")
            raise e
        if r.status_code != 200:
            raise HTTPError
        responsejson = r.json()
        if t in ["SV", "WV", "TV"]:
            return Decimal(responsejson[t])
        if t == "Diff":
            return AttrDict(responsejson[t])
        return responsejson[t]

    def format(self, s: str, system: str = "m") -> str:
        t = self._unit
        if s is None:
            raise ParseError(f"{s} is not a valid unit string.")
        s = str(s)
        if t not in ["SV", "WV", "TV"]:
            raise ValueError(f"Formatting type {t} not valid.")
        try:
            r = requests.get(f"http://sizebot.digiduncan.com/unit/{t}/format?value=" + quote(s) + "&system=" + quote(system), verify=False)
        except requests.exceptions.SSLError as e: 
            logger.error("SSL Error: The SSL certificate has expired for Sizebot API.")
            raise e
        if r.status_code != 200:
            raise HTTPError
        responsejson = r.json()
        return responsejson["formatted"]


SV = UnitWrapper("SV")
WV = UnitWrapper("WV")
TV = UnitWrapper("TV")
Diff = UnitWrapper("Diff")
