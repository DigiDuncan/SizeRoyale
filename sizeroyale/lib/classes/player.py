from sizeroyale.lib.classes.metaparser import MetaParser
from sizeroyale.lib.utils import isURL
from sizeroyale.lib.units import SV


class Player:
    valid_data = [("team", "single"), ("gender", "single"), ("height", "single"), ("url", "single")]

    def __init__(self, name, meta):
        self._original_metadata = meta
        self._metadata = MetaParser(type(self)).parse(meta)
        self.name = name
        self.team = self._metadata.team
        self.gender = self._metadata.gender
        self.height = SV.parse(self._metadata.height) if isinstance(self._metadata.height, str) else SV.parse(str(self._metadata.height) + "m")
        if not isURL(self._metadata.url):
            raise ValueError(f"{self._metadata.url} is not a URL.")
        self.url = self._metadata.url
        self.inventory = []
        self.dead = False

    @property
    def subject(self):
        if self.gender == "M":
            return "he"
        elif self.gender == "F":
            return "she"
        elif self.gender == "X":
            return "they"

    @property
    def object(self):
        if self.gender == "M":
            return "him"
        elif self.gender == "F":
            return "her"
        elif self.gender == "X":
            return "them"

    @property
    def posessive(self):
        if self.gender == "M":
            return "his"
        elif self.gender == "F":
            return "her"
        elif self.gender == "X":
            return "their"

    @property
    def posessive2(self):
        if self.gender == "M":
            return "his"
        elif self.gender == "F":
            return "hers"
        elif self.gender == "X":
            return "theirs"

    @property
    def reflexive(self):
        if self.gender == "M":
            return "himself"
        elif self.gender == "F":
            return "herself"
        elif self.gender == "X":
            return "themself"

    def __str__(self):
        return f"**{self.name}**: Team {self.team}, Gender {self.gender}, Height {self.height}, Inventory: {'Empty' if self.inventory == [] else self.inventory}. *{'Dead.' if self.dead else 'Alive.'}*"

    def __repr__(self):
        return f"Player(name={self.name!r}, team={self.team!r}, gender={self.gender!r}, height={self.height!r}, url={self.url!r}, inventory={self.inventory!r})"
