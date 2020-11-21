import logging
from pathlib import Path
from sizeroyale.lib.classes.game import Game
from digiformatter import logger as digilogger

# Logging stuff.
logging.basicConfig(level=logging.INFO)
dfhandler = digilogger.DigiFormatterHandler()
logger = logging.getLogger()
logger.handlers = []
logger.propagate = False
logger.addHandler(dfhandler)


def main():
    logger.info("Welcome to the poopview!")
    game = Game(Path(__file__).parent.parent / "royale-spec.txt")
    logger.info(game)
    print(game.royale.current_players)
    game.royale._run_event(game.royale.events.fatalnight_events[0], game.royale.alive_players)
    print(game.royale.current_players)
    game.royale._run_event(game.royale.events.bloodbath_events[0], game.royale.alive_players)
    print(game.royale.current_players)
    logger.info("Your poop has been viewed.")


if __name__ == "__main__":
    main()
