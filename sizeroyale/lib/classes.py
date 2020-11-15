from decimal import Decimal
from typing import Tuple, Union
import re

from sizeroyale.lib.attrdict import AttrDict
from sizeroyale.lib.units import SV
from sizeroyale.lib.utils import isURL

re_header = r"\[(.*)\]"
re_quotes = r"\"(.*)\""


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

        self._bloodbath_events = self.parser.bloodbath_events
        self._day_events = self.parser.day_events
        self._night_events = self.parser.night_events
        self._fatalday_events = self.parser.fatalday_events
        self._fatalnight_events = self.parser.fatalnight_events
        self._feast_events = self.parser.feast_events
        eventsdict = {
            "bloodbath_events": self._bloodbath_events,
            "day_events": self._day_events,
            "night_events": self._night_events,
            "fatalday_events": self._fatalday_events,
            "fatalnight_events": self._fatalnight_events,
            "feast_events": self._feast_events
        }
        self.events = AttrDict(eventsdict)

    @property
    def remaining(self) -> int:
        return len(self.players)

    def next(self) -> Tuple[str, Union[str, None]]:
        raise NotImplementedError


class Parser:
    def __init__(self, lines):
        self._lines = lines
        self.original_line_numbers = {}
        self.errors = []

        self.minsize = None
        self.maxsize = None
        self.autoelim = None
        self.deathrate = None
        self.players = []
        self.arenas = []
        self.bloodbath_events = []
        self.day_events = []
        self.night_events = []
        self.fatalday_events = []
        self.fatalnight_events = []
        self.feast_events = []

        self._current_header = None
        self._current_line = None
        self._skip_next_line = False

        # Setup
        self._clean_lines()
        self.parse()

    def parse(self):
        if not self.lines:
            raise ParseError("No lines to parse!")
        for n in range(len(self.lines)):
            try:
                self._parse_line(n)
            except ParseError as e:
                self.errors.append(f"Line {self.original_line_numbers[n]}: " + e.message)

    def _clean_lines(self):
        fixed_lines = []
        cln = 0

        for line in self._lines:
            # No newlines, please.
            cln += 1
            new_line = line.strip()
            new_line = new_line.replace("\n", "")
            # F*** smart quotes.
            new_line = new_line.replace("“", "\"")
            new_line = new_line.replace("”", "\"")
            # Don't bother adding back blank lines.
            if new_line != "":
                fixed_lines.append(new_line)
                self.original_line_numbers[len(fixed_lines) - 1] = cln

        self.lines = fixed_lines

    def _read_line(self, n):
        return self.lines[n]

    @property
    def _read_next_line(self):
        self._skip_next_line = True
        return self._read_line(self._current_line + 1)

    def _parse_line(self, n):
        self._current_line = n
        line = self.lines[n]

        # Skip
        if self._skip_next_line:
            self._skip_next_line = False
            return

        # Comments
        if line.startswith("#"):
            return
        
        # Headers
        if (match := re.match(re_header, line)):
            header = match.group(1)
            self._current_header = header
            return

        # Setup
        if self._current_header == "setup":
            setup = Setup(line)
            self.autoelim = setup.autoelim
            self.deathrate = setup.deathrate
            self.maxsize = setup.maxsize
            self.minsize = setup.minsize
            return

        # Players
        elif self._current_header == "players":
            if (match := re.match(re_quotes, line)):
                name = match.group(1)
            else:
                raise ParseError("No quoted string found for a player!")
            meta = self._read_next_line

            player = Player(name, meta)
            self.players.append(player)

        elif self._current_header in ["bloodbath", "day", "night", "fatalday", "fatalnight", "feast"]:
            if (match := re.match(re_quotes, line)):
                event_text = match.group(1)
            else:
                raise ParseError("No quoted string found for event!")
            meta = self._read_next_line

            event = Event(event_text, meta)
            getattr(self, self._current_header + "_events").append(event)

        else:
            return


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
        self.dummies = {}

        # self.parse(self.text)

    def parse(self, s):
        raise NotImplementedError


class Player:
    valid_data = ["team", "gender", "height", "url"]

    def __init__(self, name, meta):
        self._metadata = MetaParser(type(self)).parse(meta)
        self.name = name
        self.team = self._metadata.team
        self.gender = self._metadata.gender
        self.height = SV.parse(self._metadata.height) if isinstance(self._metadata.height, str) else SV.parse(str(self._metadata.height) + "m")
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
    def __init__(self, pid, *, lessthan, greaterthan, team, item, gender):
        self.pid = pid
        self.lessthan = SV.parse(lessthan)
        self.greaterthan = SV.parse(greaterthan)
        self.team = team
        self.item = item
        self.gender = gender

    def matches(self, player: Player):
        if not (self.team is None or player.team == self.team):
            return False
        if not (self.lessthan is None or player.height <= self.lessthan):
            return False
        if not (self.greaterthan is None or player.height >= self.greaterthan):
            return False
        if not (self.gender is None or self.gender in player.gender):
            return False
        if not (self.item is None or self.item in player.inventory):
            return False

        return True


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
            kv = item.split(":", 1)
            try:
                itemsdict[kv[0]] = kv[1]
            except IndexError:
                raise ParseError(f"Metatag {kv[0]} has no value.")
        for k, v in itemsdict.items():
            if k in ["size", "give", "remove"]:
                kv2 = v.split(":", 1)
                try:
                    v = AttrDict({kv2[0]: kv2[1]})
                except IndexError:
                    raise ParseError(f"Metatag {kv2[0]} has no value.")

        for key in self.t.valid_data:
            if key in itemsdict:
                returndict[key] = itemsdict[key]
            else:
                returndict[key] = None

        return AttrDict(returndict)
