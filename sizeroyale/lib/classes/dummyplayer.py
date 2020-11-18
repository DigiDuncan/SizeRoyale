from sizeroyale.lib.classes.player import Player
from sizeroyale.lib.units import SV


class DummyPlayer:
    def __init__(self, *, lessthan, greaterthan, team, item, gender):
        self.lessthan = None if lessthan is None else SV.parse(lessthan)
        self.greaterthan = None if greaterthan is None else SV.parse(greaterthan)
        self.team = team
        self.item = item
        self.gender = gender

        self.realteam = None

    def matches(self, player: Player):
        if not (self.lessthan is None or player.height <= self.lessthan):
            return False
        if not (self.greaterthan is None or player.height >= self.greaterthan):
            return False
        if not (self.gender is None or self.gender in player.gender):
            return False
        if not (self.item is None or self.item in player.inventory):
            return False
        if not (self.realteam is None or self.realteam == player.team):
            return False

        return True

    def __str__(self):
        return repr(self)

    def __repr__(self):
        reprstring = "DummyPlayer("
        if self.lessthan is not None:
            reprstring += f"lessthan={self.lessthan!r}, "
        if self.greaterthan is not None:
            reprstring += f"greaterthan={self.greaterthan!r}, "
        if self.item is not None:
            reprstring += f"item={self.item!r}, "
        if self.gender is not None:
            reprstring += f"gender={self.gender!r}, "
        if self.team is not None:
            reprstring += f"team={self.team!r}, "
        if self.realteam is not None:
            reprstring += f"realteam={self.realteam!r}, "
        return reprstring.rstrip().removesuffix(",") + ")"
