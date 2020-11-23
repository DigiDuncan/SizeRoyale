import logging
import random
from copy import copy
from sizeroyale.lib.loglevels import ROYALE

import petname

from sizeroyale.lib.classes.royale import Royale
from sizeroyale.lib.errors import OutOfEventsError, OutOfPlayersError, ThisShouldNeverHappenException

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
        self.current_arena = None

    def next(self):
        round = self._next_round()
        text = []
        for e in round:
            text.append(e["text"])
        return "\n".join(text)

    def _next_round(self):
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
            elif random.randint(1, 10) == 10:
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

        logger.log(ROYALE, "[ROUND] " + self.current_event_type.capitalize() + f", Day {self.current_day}")
        events = []
        while playerpool:
            e = self._next_event(playerpool)
            for p in e["players"]:
                playerpool.pop(p)
            events.append(e)

        return events

    def _next_event(self, playerpool: dict):
        if self.royale.game_over is not None:
            logger.log(ROYALE, f"[GAME] GAME OVER! Winning Team: {self.royale.game_over}")
        if self.current_event_type in ["bloodbath", "feast", "arena"]:
            event_type = self.current_event_type
        elif self.current_event_type in ["day", "night"]:
            if random.randint(1, self.royale.deathrate) == self.royale.deathrate:
                event_type = "fatal" + self.current_event_type
            else:
                event_type = self.current_event_type
        else:
            raise ThisShouldNeverHappenException("Round type not valid.")

        if self.current_event_type == "arena":
            self.current_arena = random.choice(self.royale.arenas)

        else:
            trying_events = True
            events = copy(getattr(self.royale.events, event_type + "_events"))
            while trying_events:
                if not events:
                    raise OutOfEventsError
                event = random.choices(events, [e.rarity for e in events])[0]
                try:
                    players = event.get_players(playerpool)
                    r = self.royale._run_event(event, players)
                    trying_events = False
                    return r
                except OutOfPlayersError:
                    events.remove(event)

    def __str__(self):
        return f"Game(seed={self.seed!r}\n{str(self.royale)}\n)"

    def __repr__(self):
        return f"Game(seed={self.seed}, royale={self.royale!r})"
