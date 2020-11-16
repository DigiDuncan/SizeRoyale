import logging
from sizeroyale.lib.classes import royale
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
    game = Game("C:/Users/digid/Documents/GitHub/SizeRoyale/royale-spec.txt")
    print(game)
    print(game.royale.current_players)
    logger.info("You're poop has been viewed.")


if __name__ == "__main__":
    main()
