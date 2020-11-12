from decimal import Decimal
from typing import Tuple, Union

from sizeroyale.lib.attrdict import AttrDict
from sizeroyale.lib.units import SV
from sizeroyale.lib.utils import isURL


class ParseError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


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
    valid_data = ["tributes", "sizes", "elims", "perps", "gives", "removes", "rarity"]

    def __init__(self, text: str, meta):
        self._metadata = MetaParser(type(self)).parse(meta)
        self.text = text
        self.tributes = self._metadata.tributes
        self.sizes = self._metadata.sizes
        self.elims = self._metadata.elims
        self.perps = self._metadata.perps
        self.gives = self._metadata.gives
        self.removes = self._metadata.removes
        self.rarity = 1 if self._metadata.rarity is None else self._metadata.rarity
        self.fillins = {}

    def parse(self, s):
        raise NotImplementedError


class Player:
    valid_data = ["name", "team", "gender", "height", "url"]

    def __init__(self, name, meta):
        self._metadata = MetaParser(type(self)).parse(meta)
        self.name = name
        self.team = self._metadata.team
        self.gender = self._metadata.gender
        self.height = SV.parse(self._metadata.height) if isinstance(str, self._metadata.height) else SV.parse(str(self._metadata.height) + "m")
        if not isURL(self._metadata.url):
            raise ValueError(f"{self._metadata.url} is not a URL.")
        self.url = self._metadata.url
        self.inventory = []


class Setup:
    valid_data = ["autoelim", "deathrate", "maxsize", "minsize"]

    def __init__(self, meta):
        self._metadata = MetaParser(type(self)).parse(meta)
        self.autoelim = self._metadata.autoelim
        self.deathrate = self._metadata.deathrate
        self.maxsize = self._metadata.maxsize
        self.minsize = self._metadata.minsize


class DummyPlayer:
    def __init__(self, *, lessthan, greaterthan, team, item, gender):
        self.lessthan = SV.parse(lessthan)
        self.greaterthan = SV.parse(greaterthan)
        self.team = team
        self.item = item
        self.gender = gender


class MetaParser:
    def __init__(self, t):
        self.t = t

    def parse(self, s):
        try:
            _ = self.t.valid_data
        except AttributeError:
            raise ParseError(f"Type {self.t} does not define valid metadata.")

        returndict = {}
        itemsdict = {}

        items = s.split(",")
        for item in items:
            item = item.strip()
            kv = [item.split(":", 1)]
            try:
                itemsdict[kv[0]] = kv[1]
            except IndexError:
                raise ParseError(f"Metatag {kv[0]} has no value.")
        for k, v in itemsdict:
            if k in ["size", "give", "remove"]:
                kv2 = [v.split(":", 1)]
                try:
                    v = AttrDict({kv2[0]: kv2[1]})
                except IndexError:
                    raise ParseError(f"Metatag {kv2[0]} has no value.")

        for key in self.t.valid_data:
            if key in items:
                returndict[key] = itemsdict[key]
            else:
                returndict[key] = None

        return AttrDict(returndict)
