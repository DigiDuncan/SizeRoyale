import logging
from sizeroyale.lib.classes import Royale
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
    game = Royale("C:/Users/digid/Documents/GitHub/SizeRoyale/royale-spec.txt")
    print(game)
    logger.info("You're poop has been viewed.")


if __name__ == "__main__":
    main()
