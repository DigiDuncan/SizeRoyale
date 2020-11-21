import logging
import random

import petname

from sizeroyale.lib.classes.royale import Royale
from sizeroyale.lib.errors import ThisShouldNeverHappenException

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

        # Switch to a normal day after the bloodbath.
        elif self.current_event_type == "bloodbath":
            self.current_event_type = "day"
        else:
            # Run a feast when half the population is eliminated.
            if self.royale.original_player_count / 2 > self.royale.remaining:
                self.current_event_type = "feast"

            # Run an arena every 10.
            elif random.randint(10) == 10:
                self.current_event_type = "arena"

            # Day -> night.
            elif self.current_event_type == "day":
                self.current_event_type = "night"

            # Rollover to day.
            elif (self.current_event_type == "night"
                  or self.current_event_type == "arena"
                  or self.current_event_type == "feast"):
                self.current_event_type = "day"
                self.current_day += 1

            else:
                raise ThisShouldNeverHappenException("Round type not valid.")

        events = []
        while playerpool:
            events.append(self._next_event(playerpool))

        return events

    def _next_event(self, playerpool: dict):
        raise NotImplementedError

    def __str__(self):
        return f"Game(seed={self.seed!r}\n{str(self.royale)}\n)"

    def __repr__(self):
        return f"Game(seed={self.seed}, royale={self.royale!r})"
