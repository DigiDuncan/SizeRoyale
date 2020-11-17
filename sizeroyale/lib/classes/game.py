import logging

from sizeroyale.lib.classes.royale import Royale

logger = logging.getLogger("sizeroyale")


class Game:
    def __init__(self, filepath):
        self.royale = Royale(filepath)
        if self.royale.parser.errors:
            for e in self.royale.parser.errors:
                logger.error(e)

    def next_round(self):
        raise NotImplementedError

    def _next_event(self):
        raise NotImplementedError

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Game(royale={self.royale!r})"
