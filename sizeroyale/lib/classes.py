from decimal import Decimal
from typing import Tuple, Union

from sizeroyale.lib.attrdict import AttrDict
from sizeroyale.lib.units import SV
from sizeroyale.lib.utils import isURL


class Royale:
    def __init__(self, file):
        self._file = file

        with open(self._file) as f:
            lines = f.readlines()
            self.parser = Parser(lines)

        self.minsize = SV.parse("1mm") if self.parser.minsize is None else SV.parse(self.parser.minsize)
        self.maxsize = SV.parse("4mi") if self.parser.maxsize is None else SV.parse(self.parser.maxsize)
        self.autoelim = True if self.parser.maxsize is None else self.parser.autoelim
        self.deathrate = Decimal(10) if self.parser.maxsize is None else Decimal(self.parser.deathrate)

        self.players = self.parser.players
        self.arenas = self.parser.arenas

        self._bloodbaths = self.parser.bloodbaths
        self._dayevents = self.parser.dayevents
        self._nightevents = self.parser.nightevents
        self._fataldayevents = self.parser.fataldayevents
        self._fatalnightevents = self.parser.fatalnightevents
        self._feasts = self.parser.feasts
        eventsdict = {
            "bloodbaths": self._bloodbaths,
            "dayevents": self._dayevents,
            "nightevents": self._nightevents,
            "fataldayevents": self._fataldayevents,
            "fatalnightevents": self._fatalnightevents,
            "feasts": self._feasts
        }
        self.events = AttrDict(eventsdict)

    @property
    def remaining(self) -> int:
        return len(self.players)

    def next(self) -> Tuple[str, Union(str, None)]:
        raise NotImplementedError


class Parser:
    def __init__(self, lines):
        self.minsize = None
        self.maxsize = None
        self.autoelim = None
        self.deathrate = None
        self.players = []
        self.arenas = []
        self.bloodbaths = []
        self.dayevents = []
        self.nightevents = []
        self.fataldayevents = []
        self.fatalnightevents = []
        self.feasts = []

    def parse(self):
        for line in self.lines:
            self._parse_line(line)

    def _parse_line(self, line):
        raise NotImplementedError


class Arena:
    def __init__(self, name: str, description: str, events: list):
        self.name = name
        self.description = description
        self.events = events


class Event:
    def __init__(self, text: str, tributes: int, *, sizes, elims, perps, gives, removes, rarity):
        self.text = text
        self.tributes = tributes
        self.sizes = None if sizes is None else sizes
        self.elims = None if elims is None else elims
        self.perps = None if perps is None else perps
        self.gives = None if gives is None else gives
        self.removes = None if removes is None else removes
        self.rarity = 1 if rarity is None else rarity


class Player:
    def __init__(self, name, team, gender, height, url):
        self.name = name
        self.team = team
        self.gender = gender
        self.height = SV.parse(height) if isinstance(str, height) else SV.parse(str(height) + "m")
        if not isURL(url):
            raise ValueError(f"{url} is not a URL.")
        self.url = url
        self.inventory = []
