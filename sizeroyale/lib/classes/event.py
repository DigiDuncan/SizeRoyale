import random
import re
from decimal import Decimal
from typing import Dict, List

from sizeroyale.lib.errors import ParseError
from sizeroyale.lib.classes.dummyplayer import DummyPlayer
from sizeroyale.lib.classes.metaparser import MetaParser
from sizeroyale.lib.classes.player import Player

re_format = r"%(\d.*?)%"
re_team = r"[A-Z]"
re_gender = r"[MFX]"
re_pronoun_weak = r"%[pP]:.*?%"
re_pronoun = r"^([pP]):(\d)(|o|s|self)$"


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

    def parse(self, s: str):
        formats = re.findall(re_format, s)

        formatchecker = {}

        for f in formats:
            if f[0] not in formatchecker:
                formatchecker[f[0]] = f[1:]
            else:
                if formatchecker[f[0]] != f[1:]:
                    raise ParseError("Multiple definitions for one player!")

        pids = [int(k) for k in formatchecker.keys()]
        pids.sort()
        highest_player = max(pids)
        if pids != list(range(1, highest_player + 1)):
            raise ParseError("Out of order player IDs!")

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

    def get_players(self, playerpool: Dict[str, Player]):
        playerpool = [v for k, v in playerpool]
        random.shuffle(playerpool)

        good_players = []

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

    def fillin(self, players: List[Player]):
        out = self.text
        for i in range(len(players)):
            subsstring = "%" + str(i + 1) + ".*?%"
            out = re.sub(subsstring, players[i].name, out)
        while (search := re.search(re_pronoun_weak, out)):
            replacestring = search.group(0)
            out = out.replace(replacestring, self._pronoun_parse(players, replacestring))

        return out

    def _pronoun_parse(self, players: List[Player], s: str):
        if not s.startswith("%") and s.endswith("%"):
            raise ParseError("Pronoun string does not start and end with %.")
        s = s[1:-1]
        if (match := re.match(re_pronoun, s)):
            capital = True if match.group(1) == "P" else False
            pid = int(match.group(2))
            player = players[pid - 1]
            if match.group(3) == "":
                return player.subject.capitalize() if capital else player.subject
            elif match.group(3) == "o":
                return player.object.capitalize() if capital else player.object
            elif match.group(3) == "s":
                return player.posessive.capitalize() if capital else player.posessive
            elif match.group(3) == "self":
                return player.reflexive.capitalize() if capital else player.reflexive
            else:
                raise ParseError(f"Invalid pronoun type '{match.group(3)}'")
        else:
            raise ParseError("Pronoun string in incorrect format.")

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Event(text={self.text!r}, tributes={self.tributes}, sizes={self.sizes!r}, elims={self.elims!r}, perps={self.perps!r}, gives={self.gives!r}, removes={self.removes!r}, rarity={self.rarity}, dummies={self.dummies!r})"
