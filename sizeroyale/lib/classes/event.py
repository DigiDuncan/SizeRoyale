import re

from sizeroyale.lib.errors import ParseError
from sizeroyale.lib.classes.dummyplayer import DummyPlayer
from sizeroyale.lib.classes.metaparser import MetaParser

re_format = r"%(\d:.*?)%"
re_team = r"[A-Z]"
re_gender = r"[MFX]"

class Event:
    valid_data = ["tributes", "sizes", "elims", "perps", "gives", "removes", "rarity"]

    def __init__(self, text: str, meta):
        self._original_metadata = meta
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

        self.parse(self.text)

    def parse(self, s):
        formats = re.findall(re_format, s)

        formatchecker = {}

        for f in formats:
            if f[0] not in formatchecker:
                formatchecker[f[0]] = f[1:]
            else:
                if formatchecker[f[0]] != f[1:]:
                    raise ParseError("Multiple definitions for one player!")

        for f in formats:
            pid = None
            lessthan = None
            greaterthan = None
            team = None
            item = None
            gender = None

            pid = f[0]
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

            self.dummies[pid] = DummyPlayer(lessthan = lessthan,
                                            greaterthan = greaterthan,
                                            team = team,
                                            item = item,
                                            gender = gender)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Event(text={self.text!r}, tributes={self.tributes!r}, sizes={self.sizes!r}, elims={self.elims!r}, perps={self.perps!r}, gives={self.gives!r}, removes={self.removes!r}, rarity={self.rarity!r}, dummies={self.dummies!r})"
