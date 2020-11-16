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
    print(game.royale)
    print(game.royale.current_players)
    logger.info("Your poop has been viewed.")


if __name__ == "__main__":
    main()
