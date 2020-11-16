from decimal import Decimal

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
        self.autoelim = True if self.parser.autoelim is None else bool(self.parser.autoelim)
        self.deathrate = Decimal(10) if self.parser.deathrate is None else Decimal(self.parser.deathrate)

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
        self.current_event_type = None

    @property
    def alive_players(self) -> dict:
        return {k:v for k, v in self.players.items() if self.is_player_alive(v)}

    @property
    def dead_players(self) -> dict:
        return {k:v for k, v in self.players.items() if not self.is_player_alive(v)}

    @property
    def remaining(self) -> int:
        return len(self.alive_players)

    @property
    def current_players(self):
        return "\n".join([str(p) for p in self.alive_players.values()])

    def is_player_alive(self, player) -> bool:
        if self.autoelim:
            return player.height > self.minsize and player.height < self.maxsize and player.dead == False
        return player.dead == False

    def __str__(self):
        outstring = ""
        sublevel = 0
        def add(string):
            nonlocal outstring
            outstring += ("  " * sublevel + string + "\n")
        add(f"Royale {hex(id(self))}:")
        add(f"Autoelim: {self.autoelim!r}, Death Rate: {self.deathrate}, Max Size: {self.maxsize}, Min Size: {self.minsize}")
        add("Players:")
        sublevel += 1
        for n, p in self.players.items():
            add(f"{n!r}: Team: {p.team!r}, Gender: {p.gender!r}, Height: {p.height}, Dead: {p.dead!r}")
            sublevel += 1
            add(f"Image: {p.url!r}")
            add(f"Inventory: {p.inventory!r})")
            sublevel -=1
        sublevel -=1
        add("Arenas:")
        sublevel += 1
        for a in self.arenas:
            add(f"{a.name!r}:")
            sublevel += 1
            add(f"Description: {a.description!r},")
            add(f"Events: ")
            sublevel +=1
            for e in a.events:
                add(f"{e.text}")
                sublevel += 1
                edata = f"Tributes: {e.tributes!r}, "
                if e.sizes is not None:
                    edata += f"Sizes: {e.sizes!r}, "
                if e.elims is not None:
                    edata += f"Elims: {e.elims!r}, "
                if e.perps is not None:
                    edata += f"Perps: {e.perps!r}, "
                if e.gives is not None:
                    edata += f"Gives: {e.gives!r}, "
                if e.removes is not None:
                    edata += f"Removes: {e.removes!r}, "
                edata += f"Rarity: {e.rarity!r}"
                add(edata)
                if e.dummies == {}:
                    add("Dummies: {}")
                else:
                    add("Dummies: {")
                    sublevel += 1
                    for n, d in e.dummies.items():
                        add(f"{n!r}: {d!r}")
                    sublevel -= 1
                    outstring = outstring.rstrip() + "}"
                sublevel -= 1
            sublevel -= 1
            sublevel -= 1
        sublevel -= 1
        add("Events:")
        sublevel += 1
        for et, l in self.events._values.items():
            add(et.replace("_", " ").title() + ":")
            sublevel += 1
            for e in l:
                add(f"{e.text}")
                sublevel += 1
                edata = f"Tributes: {e.tributes!r}, "
                if e.sizes is not None:
                    edata += f"Sizes: {e.sizes!r}, "
                if e.elims is not None:
                    edata += f"Elims: {e.elims!r}, "
                if e.perps is not None:
                    edata += f"Perps: {e.perps!r}, "
                if e.gives is not None:
                    edata += f"Gives: {e.gives!r}, "
                if e.removes is not None:
                    edata += f"Removes: {e.removes!r}, "
                edata += f"Rarity: {e.rarity!r}"
                add(edata)
                if e.dummies == {}:
                    add("Dummies: {}")
                else:
                    add("Dummies: {")
                    sublevel += 1
                    for n, d in e.dummies.items():
                        add(f"{n!r}: {d!r}")
                    sublevel -= 1
                    outstring = outstring.rstrip() + "}\n"
                sublevel -= 1
            sublevel -= 1
        sublevel -= 1

        return outstring

    def __repr__(self):
        return f"Royale(autoelim={self.autoelim!r}, deathrate={self.deathrate!r}, maxsize={self.maxsize!r}, minsize={self.minsize!r}, players={self.players!r}, arenas={self.arenas!r}, events={self.events!r})"