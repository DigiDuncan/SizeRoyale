import logging
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


if __name__ == "__main__":
    main()
