import logging
from pathlib import Path

from digiformatter import logger as digilogger

from sizeroyale.lib.classes.game import Game
from sizeroyale.lib.loglevels import ROYALE

# Logging stuff.
logging.basicConfig(level=logging.INFO)
dfhandler = digilogger.DigiFormatterHandler()
logger = logging.getLogger()
logger.handlers = []
logger.propagate = False
logger.addHandler(dfhandler)


def main():
    p = input("Input a Royale Spec file path, or hit [ENTER] for the default path.")
    if not p:
        p = Path(__file__).parent.parent / "royale-spec.txt"
    else:
        p = Path(p)
    game = Game(p)
    # logger.info(game)
    logger.log(ROYALE, f"seed = {game.seed}")
    print(game.royale.current_players)
    game.royale.stats_screen.show()

    while game.game_over is None:
        game.next()


if __name__ == "__main__":
    main()
