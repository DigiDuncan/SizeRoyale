import io
import os
from decimal import Decimal
from functools import lru_cache
from PIL import ImageFont

import requests
from PIL import Image, ImageDraw

from sizeroyale.lib.errors import DownloadError, GametimeError, ThisShouldNeverHappenException
from sizeroyale.lib.classes.metaparser import MetaParser
from sizeroyale.lib.img_utils import crop_max_square, kill
from sizeroyale.lib.utils import isURL, truncate
from sizeroyale.lib.units import SV, Diff


class Player:
    valid_data = [("team", "single"), ("gender", "single"), ("height", "single"), ("url", "single"), ("attr", "list")]

    def __init__(self, name: str, meta: str):
        self._original_metadata = meta
        self._metadata = MetaParser(type(self)).parse(meta)
        self.name = name
        self.team = self._metadata.team
        self.gender = self._metadata.gender
        self.height = SV.parse(self._metadata.height) if isinstance(self._metadata.height, str) else SV.parse(str(self._metadata.height) + "m")
        if not isURL(self._metadata.url):
            raise ValueError(f"{self._metadata.url} is not a URL.")
        self.url = self._metadata.url
        self.attributes = [] if self._metadata.attr is None else self._metadata.attr

        self.inventory = []
        self.dead = False
        self.elims = 0

    @property
    @lru_cache(maxsize = 2)
    def image(self) -> Image:
        size = (200, 200)

        r = requests.get(self.url, stream=True)
        if r.status_code == 200:
            i = Image.open(io.BytesIO(r.content))
        else:
            raise DownloadError("Profile image could not be downloaded.")

        i = crop_max_square(i)
        i = i.resize(size)
        rgbimg = Image.new("RGBA", i.size)
        rgbimg.paste(i)
        i = rgbimg
        d = ImageDraw.Draw(i)
        fnt = ImageFont.truetype(os.environ['WINDIR'] + "\\Fonts\\arial.ttf", size = 20)
        name = self.name
        while fnt.getsize(name)[0] > i.width:
            name = truncate(name, len(name) - 1)
        textwidth, textheight = fnt.getsize(name)
        d.text(((i.width - textwidth) // 2, i.height - textheight - 10),
               name, align = "center", font = fnt, fill = (0, 0, 0),
               stroke_width = 2, stroke_fill = (255, 255, 255))

        if self.dead:
            i = kill(i)

        return i

    @property
    def subject(self) -> str:
        if self.gender == "M":
            return "he"
        elif self.gender == "F":
            return "she"
        elif self.gender == "X":
            return "they"

    @property
    def object(self) -> str:
        if self.gender == "M":
            return "him"
        elif self.gender == "F":
            return "her"
        elif self.gender == "X":
            return "them"
        else:
            raise ThisShouldNeverHappenException(f"Invalid gender {self.gender!r} on player {self.name!r}.")

    @property
    def posessive(self) -> str:
        if self.gender == "M":
            return "his"
        elif self.gender == "F":
            return "her"
        elif self.gender == "X":
            return "their"
        else:
            raise ThisShouldNeverHappenException(f"Invalid gender {self.gender!r} on player {self.name!r}.")

    # Unused, hope we don't need this.
    @property
    def posessive2(self) -> str:
        if self.gender == "M":
            return "his"
        elif self.gender == "F":
            return "hers"
        elif self.gender == "X":
            return "theirs"
        else:
            raise ThisShouldNeverHappenException(f"Invalid gender {self.gender!r} on player {self.name!r}.")

    @property
    def reflexive(self) -> str:
        if self.gender == "M":
            return "himself"
        elif self.gender == "F":
            return "herself"
        elif self.gender == "X":
            return "themself"
        else:
            raise ThisShouldNeverHappenException(f"Invalid gender {self.gender!r} on player {self.name!r}.")

    def give_item(self, item: str):
        self.inventory.append(item)

    def remove_item(self, item: str):
        if item in self.inventory:
            self.inventory.remove(item)
        else:
            raise GametimeError(f"{self.name} has no item {self.item!r}!")

    def clear_inventory(self):
        self.inventory = []

    def give_attribute(self, attribute: str):
        self.inventory.append(attribute)

    def remove_attribute(self, attribute: str):
        if attribute in self.inventory:
            self.inventory.remove(attribute)
        else:
            raise GametimeError(f"{self.name} has no attribute {self.attribute!r}!")

    def change_height(self, diff: Diff):
        if diff.changetype == "add":
            self.height += Decimal(diff.amount)
        elif diff.changetype == "multiply":
            self.height *= Decimal(diff.amount)

        else:
            raise GametimeError(f"Unsupported changetype {diff.changetype!r}.")

    def __str__(self):
        return f"**{self.name}**: Team {self.team}, Gender {self.gender}, Height {self.height}, Eliminations: {self.elims}, Inventory: {'Empty' if self.inventory == [] else self.inventory}. *{'Dead.' if self.dead else 'Alive.'}*"

    def __repr__(self):
        return f"Player(name={self.name!r}, team={self.team!r}, gender={self.gender!r}, height={self.height!r}, url={self.url!r}, inventory={self.inventory!r})"
