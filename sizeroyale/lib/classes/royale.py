from decimal import Decimal
from typing import Tuple, Union

from sizeroyale.lib.attrdict import AttrDict
from sizeroyale.lib.classes.parser import Parser
from sizeroyale.lib.units import SV

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

        self.current_day = 0
        self.current_event = None

    def is_player_alive(self, player) -> bool:
        if self.autoelim:
            return player.height > self.minsize and player.height < self.maxsize and player.dead == False
        return player.dead == False

    @property
    def alive_players(self) -> dict:
        return {k:v for k, v in self.players if self.is_player_alive(v)}

    @property
    def dead_players(self) -> dict:
        return {k:v for k, v in self.players if not self.is_player_alive(v)}

    @property
    def remaining(self) -> int:
        return len(self.alive_players)

    def run_event(self, players, event):
        raise NotImplementedError

    def next(self) -> Tuple[str, Union[str, None]]:
        """
        Returns the text of the next event, and either an associated image, or None.
        """
        raise NotImplementedError

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Royale(autoelim={self.autoelim!r}, deathrate={self.deathrate!r}, maxsize={self.maxsize!r}, minsize={self.minsize!r}, players={self.players!r}, arenas={self.arenas!r}, events={self.events!r})"
