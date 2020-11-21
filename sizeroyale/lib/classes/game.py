import logging
import random

import petname

from sizeroyale.lib.classes.royale import Royale

logger = logging.getLogger("sizeroyale")


class Game:
    def __init__(self, filepath, *, seed = None):
        self.royale = Royale(filepath)
        if self.royale.parser.errors:
            for e in self.royale.parser.errors:
                logger.error(e)

        if seed is None:
            self.seed = petname.generate(3, letters = 10)
        else:
            self.seed = seed

        random.seed(self.seed)

        self.current_day = 0
        self.current_event_type = None

    def next_round(self):
        # Reset player pool.
        playerpool = self.royale.alive_players

        # Progress the round type forward.
        if self.current_day == 0:
            self.current_event_type = "bloodbath"
            self.current_day += 1
        elif self.current_event_type == "bloodbath":
            self.current_event_type = "day"
        else:
            if random.randint(10) == 10:
                self.current_event_type = "arena"
            elif self.current_event_type == "day":
                self.current_event_type = "night"
            elif self.current_event_type == "night":
                self.current_event_type = "day"
                self.current_day += 1
            elif self.current_event_type == "arena":
                self.current_event_type = "day"
                self.current_day += 1

    def _next_event(self, playerpool: dict):
        raise NotImplementedError

    def __str__(self):
        return f"Game(seed={self.seed!r}\n{str(self.royale)}\n)"

    def __repr__(self):
        return f"Game(seed={self.seed}, royale={self.royale!r})"
