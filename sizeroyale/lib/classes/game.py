from sizeroyale.lib.classes.royale import Royale


class Game:
    def __init__(self, filepath):
        self.royale = Royale(filepath)

    def next_round(self):
        raise NotImplementedError

    def _next_event(self):
        raise NotImplementedError

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Game(royale={self.royale!r})"
