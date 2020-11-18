import random
import re
from decimal import Decimal
from typing import List

from sizeroyale.lib.errors import ParseError
from sizeroyale.lib.classes.dummyplayer import DummyPlayer
from sizeroyale.lib.classes.metaparser import MetaParser
from sizeroyale.lib.classes.player import Player

re_format = r"%(\d.*?)%"
re_team = r"[A-Z]"
re_gender = r"[MFX]"


class Event:
    valid_data = [("tributes", "single"), ("size", "compound"), ("elim", "list"), ("perp", "list"),
                  ("give", "compound"), ("remove", "compound"), ("rarity", "single")]

    def __init__(self, text: str, meta):
        self._original_metadata = meta
        self._metadata = MetaParser(type(self)).parse(meta)
        self.text = text
        self.tributes = None if self._metadata.tributes is None else Decimal(self._metadata.tributes)
        self.sizes = None if self._metadata.size is None else [(int(k), v) for k, v in self._metadata.size]
        self.elims = None if self._metadata.elim is None else [int(i) for i in self._metadata.elim]
        self.perps = None if self._metadata.perp is None else [int(i) for i in self._metadata.perp]
        self.gives = None if self._metadata.give is None else [(int(k), v) for k, v in self._metadata.give]
        self.removes = None if self._metadata.remove is None else [(int(k), v) for k, v in self._metadata.remove]
        self.rarity = Decimal(1) if self._metadata.rarity is None else Decimal(self._metadata.rarity)
        self.dummies = {}

        self.parse(self.text)

        if self.tributes is None:
            raise ParseError("Tribute amount not defined.")

        if self.tributes != len(self.dummies):
            raise ParseError(f"Tribute amount mismatch. ({self.tributes} != {len(self.dummies)})")

    def parse(self, s):
        formats = re.findall(re_format, s)

        formatchecker = {}

        for f in formats:
            if f[0] not in formatchecker:
                formatchecker[f[0]] = f[1:]
            else:
                if formatchecker[f[0]] != f[1:]:
                    raise ParseError("Multiple definitions for one player!")

        for ff in formats:
            pid = None
            lessthan = None
            greaterthan = None
            team = None
            item = None
            gender = None

            pid = ff[0]
            fs = ff.split("&")

            fs = [pid + ":" + f for f in fs]

            for f in fs:
                if len(f) > 1:
                    if f[1] == "<":  # lessthan
                        lessthan = f[2:]
                    elif f[1] == ">":  # greaterthan
                        greaterthan = f[2:]
                    elif f[1] == ":":
                        parts = f.split(":")
                        if len(parts) == 2:
                            if re.match(re_team, parts[1]):
                                team = parts[1]
                            else:
                                ParseError(f"{parts[1]} is not a valid team.")
                        elif len(parts) == 3:
                            if parts[1] == "g":
                                if re.match(re_gender, parts[2]):
                                    gender = parts[2]
                                else:
                                    ParseError(f"{parts[2]} is not a vaild gender.")
                            if parts[1] == "inv":
                                item = parts[2]
                        else:
                            ParseError(f"Invalid format tag: {f}")
                elif len(f) == 1:
                    pass
                else:
                    ParseError(f"Invalid format tag: {f}")

            self.dummies[int(pid)] = DummyPlayer(lessthan = lessthan,
                                                 greaterthan = greaterthan,
                                                 team = team,
                                                 item = item,
                                                 gender = gender)

    def get_players(self, playerpool: List(Player)):
        good_players = []
        random.shuffle(playerpool)

        # Assign dummy teams to real teams.
        teams = set()
        teammap = {}
        for player in self.alive_players:
            teams.add(player.team)
        for d in self.dummies:
            if d.team:
                if d.team in teammap:
                    d.realteam = teammap[d.team]
                else:
                    randomteam = random.choice(teams)
                    teammap[d.team] = randomteam
                    d.realteam = teammap[d.team]
                    teams.remove(randomteam)

        # Assign dummy players to real players.
        for d in self.dummies:
            for n, p in enumerate(playerpool):
                if d.matches(p):
                    good_players.append(playerpool.pop(n))
                    break

        return good_players

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Event(text={self.text!r}, tributes={self.tributes}, sizes={self.sizes!r}, elims={self.elims!r}, perps={self.perps!r}, gives={self.gives!r}, removes={self.removes!r}, rarity={self.rarity}, dummies={self.dummies!r})"
