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

    def __str__(self):
        return f"**{self.name}**: Team {self.team}, Gender {self.gender}, Height {self.height}, Inventory: {'Empty' if self.inventory == [] else self.inventory}. *{'Dead.' if self.dead else 'Alive.'}*"

    def __repr__(self):
        return f"Player(name={self.name!r}, team={self.team!r}, gender={self.gender!r}, height={self.height!r}, url={self.url!r}, inventory={self.inventory!r})"
